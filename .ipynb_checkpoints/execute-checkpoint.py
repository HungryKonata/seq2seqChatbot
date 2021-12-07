# -*- coding:utf-8 -*-
import os
import sys
import time
import tensorflow as tf
import s2sModel
import getConfig
import io
import jieba

gConfig = {}
gConfig=getConfig.get_config(config_file='config.ini')

# 读取模型名称列表
model_name_list = gConfig['model_name_list'].strip(',').split(',')

# 读取本次要训练模型的名称
training_model_name = gConfig['training_model_name']
print('training model name:' + training_model_name)

# 从配置文件获取词表大小、词嵌入维度、层大小、batch size
vocab_inp_size = gConfig['enc_vocab_size']
vocab_tar_size = gConfig['dec_vocab_size']
embedding_dim=gConfig['embedding_dim']
units=gConfig['layer_size']
BATCH_SIZE=gConfig['batch_size']
epoch_num=gConfig['epoch_num']

# 设置最大输入输出长度
max_length_inp,max_length_tar=20,20

# 新建checkpoint目录
checkpoint_root_dir = 'model_data/'
checkpoint_dir = checkpoint_root_dir + training_model_name
print('checkpoint_dir:'+checkpoint_dir)
isExists=os.path.exists(checkpoint_dir)
# 判断结果
if not isExists:
    # 如果不存在则创建目录
     # 创建目录操作函数
    os.makedirs(checkpoint_dir)
    print("make checkpoint_dir...")
else:
    print("checkpoint_dir found...")

#确定读入的seq.data路径
seq_data_path = 'train_data/'+training_model_name+'/seq.data'
print('seq_data_path:'+seq_data_path)

# 给句子前后加上start和end标志
def preprocess_sentence(w):
    w ='start '+ w + ' end'
    #print(w)
    return w

# 生成带start和end标志的问句和答句，输出形式：
# ('start 呵呵 end', 'start 不是 end', 'start 怎么 了 end', 'start 开心 点哈 , 一切 都 会 好 起来 end', 'start 我 还 喜欢 她 , 怎么办 end', 'start 短信 end', 'start 你 知道 谁 么 end', 'start 许兵 是 谁 end', 'start 这么 假 end', 'start 许兵 是 傻 逼 end')
# ('start 是 王若 猫 的 end', 'start 那 是 什么 end', 'start 我 很 难过 安慰 我 ~ end', 'start 嗯 end', 'start 我 帮 你 告诉 她 发短信 还是 打电话 end', 'start 嗯 嗯 我 也 相信 end', 'start 肯定 不是 我 是 阮德培 end', 'start 吴院 四班 小帅哥 end', 'start 三鹿 奶粉 也 假 不 一样 的 卖 啊 end', 'start 被 你 发现 了 end')
def create_dataset(path, num_examples):
    lines = io.open(path, encoding='UTF-8').read().strip().split('\n')
    word_pairs = [[preprocess_sentence(w)for w in l.split('\t')] for l in lines[:num_examples]]
    return zip(*word_pairs)


def max_length(tensor):
    return max(len(t) for t in tensor)

def read_data(path,num_examples):
    #取得带start和end标志的问句和答句
    input_lang,target_lang=create_dataset(path,num_examples)
    
    #生成向量化表示的输入句子，每一个句子用一个向量表示，每一个向量的长度为max_length_inp，输出形式：
    #  [[   2   50    3    0    0    0    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2   33    3    0    0    0    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2   20    6    3    0    0    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2  139 7137 2437   29   28   14  359    3    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2    5   31   23   74   56    3    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2 2861    3    0    0    0    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2    4   27   13   18    3    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2 1925    7   13    3    0    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2   63 1117    3    0    0    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]
    #  [   2 1925    7   44   60    3    0    0    0    0    0    0    0    0
    #      0    0    0    0    0    0]]
    input_tensor,input_token=tokenize(input_lang)
    
    #生成向量化表示的输出句子，每一个句子用一个向量表示，每一个向量的长度为max_length_tar
    target_tensor,target_token=tokenize(target_lang)

    return input_tensor,input_token,target_tensor,target_token

def tokenize(lang):
    # 将文本向量化，或将文本转换为序列（即单个字词以及对应下标构成的列表，从1开始），对文本进行分词预处理
    lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=gConfig['enc_vocab_size'], oov_token=3)
    lang_tokenizer.fit_on_texts(lang)
    tensor = lang_tokenizer.texts_to_sequences(lang)
    tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor, maxlen=max_length_inp,padding='post')
    return tensor, lang_tokenizer

# 运行read_data函数，得到每个句子的向量形式
input_tensor,input_token,target_tensor,target_token= read_data(seq_data_path, gConfig['max_train_data_size'])

def train(cp_dir,epoch_num):
    print("Preparing data in %s" % gConfig['train_data'])
    #计算一轮需要多少batch
    steps_per_epoch = len(input_tensor) // gConfig['batch_size']
    print(steps_per_epoch)
    
    #初始化隐藏层状态，全0初始化
    enc_hidden = s2sModel.encoder.initialize_hidden_state()
    
    #设置checkpoint保存点的路径
#     checkpoint_dir = gConfig['model_data']
    
    #列出cp_dir路径中所有文件名
    ckpt=tf.io.gfile.listdir(cp_dir)
    
    #如果checkpoint_dir路径中有文件，则认为使用预训练模型
    if ckpt:
        print("reload pretrained model")
        s2sModel.checkpoint.restore(tf.train.latest_checkpoint(cp_dir))
        
    #规定输入缓冲区大小
    BUFFER_SIZE = len(input_tensor)
    
    #从input_tensor,target_tensor生成数据集，并打乱顺序
    dataset = tf.data.Dataset.from_tensor_slices((input_tensor,target_tensor)).shuffle(BUFFER_SIZE)
    
    #按照顺序每次划分BATCH_SIZE行数据
    dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
    
    #又设置了一下保存路径，先注释掉了
    #checkpoint_dir = gConfig['model_data']
    
    #设置模型保存文件名的前缀
    checkpoint_prefix = os.path.join(cp_dir, "ckpt")
    start_time = time.time()

    #开始训练循环
    for i in range(epoch_num):
        start_time_epoch = time.time()
        total_loss = 0
        
        #从数据集中按batch读取数据，对每个batch进行训练，计算loss
        for (batch, (inp, targ)) in enumerate(dataset.take(steps_per_epoch)):
            batch_loss = s2sModel.train_step(inp, targ,target_token, enc_hidden)
            total_loss += batch_loss
            print(batch_loss.numpy())
            
        #计算每个batch的耗时
        step_time_epoch = (time.time() - start_time_epoch) / steps_per_epoch
        
        #计算每个batch的平均loss
        step_loss = total_loss / steps_per_epoch
        
        #已经训练的步长
        current_steps = +steps_per_epoch
        
        #计算已经训练的步长里平均训练一个batch需要多久
        step_time_total = (time.time() - start_time) / current_steps

        print('训练总步数: {} 平均每步耗时: {}  最新每步耗时: {} 最新每步loss {:.4f}'.format(current_steps, step_time_total, step_time_epoch,
                                                                      step_loss.numpy()))
        
        #一个epoch训练完毕，保存模型
        s2sModel.checkpoint.save(file_prefix=checkpoint_prefix)

        #刷新命令行输出
        sys.stdout.flush()
        
#调用decode_line对生成回答信息
def predict(sentence,cp_dir):
    #使用jieba分词
    sentence=" ".join(jieba.cut(sentence))
    
    #获取checkpoint地址
#     checkpoint_dir = gConfig['model_data']
    s2sModel.checkpoint.restore(tf.train.latest_checkpoint(cp_dir))
    
    #给输入的句子加上标志
    sentence = preprocess_sentence(sentence)
    
    #用训练语料集的tokenizer处理成向量
    inputs = [input_token.word_index.get(i,3) for i in sentence.split(' ')]

    #将输入序列转化为经过填充以后的一个长度相同的新序列，长度为max_length_inp，0补在尾部
    inputs = tf.keras.preprocessing.sequence.pad_sequences([inputs],maxlen=max_length_inp,padding='post')
    
    #把inputs的变量类型转换成tensor
    inputs = tf.convert_to_tensor(inputs)
    
    #初始化输出语句变量
    result = ''
    
    #隐层赋值全0
    hidden = [tf.zeros((1, units))]
    
    #输入神经网络编码器，得到编码器输出和编码器隐层参数
    enc_out, enc_hidden = s2sModel.encoder(inputs, hidden)

    #解码器隐层直接取编码器隐层参数
    dec_hidden = enc_hidden
    
    #解码器输入为start的向量
    dec_input = tf.expand_dims([target_token.word_index['start']], 0)
    
    #解码器开始预测
    for t in range(max_length_tar):
        #数据输入到解码器，计算出预测向量、解码器隐层参数、注意力权重
        predictions, dec_hidden, attention_weights = s2sModel.decoder(dec_input, dec_hidden, enc_out)

        #找预测向量的最大值，对应到词表的id
        predicted_id = tf.argmax(predictions[0]).numpy()

        #如果输出的预测是end，则结束预测
        if target_token.index_word[predicted_id] == 'end':
            break
            
        #根据id查到词，加入到结果中
        result += target_token.index_word[predicted_id] + ' '

        #设置下一步的输入为这一步的输出词
        dec_input = tf.expand_dims([predicted_id], 0)
    
    #去除结果的多余字符
    result = result.replace('_UNK', '^_^')
    result = result.strip()
    result.replace(' ','')
    return result




if __name__ == '__main__':
    if len(sys.argv) - 1:
        gConfig = getConfig.get_config(sys.argv[1])
    else:

        gConfig = getConfig.get_config()

    print('\n>> Mode : %s\n' %(gConfig['mode']))

    if gConfig['mode'] == 'train':
  
        train(checkpoint_dir,epoch_num)
    elif gConfig['mode'] == 'serve':
    
        print('Serve Usage : >> python3 app.py')
