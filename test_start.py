import pytest
import dataPreprocess
# import s2sModel
# import getConfig
import execute
# import app
import selectMode
import otherModes

# 可以再命令行中直接使用pytest -s -v test_start.py

# 规定测试用例的模型名称和语料名称
model_name = 'talk1'
raw_data_name = 'xiaohuangji50w_nofenci.conv'
class Test_dataPreprocess: #类名大写打头
#     def __init__(self):这个不能加
    def test_raw_data_path(self):#测试函数名用test_开头
        '''测试能不能找到对应的预料文件
        不同的模型要改名称'''
        assert dataPreprocess.corpus_name == raw_data_name
    
    def test_output_data_path(self):
        '''测试输出seq文件路径正确'''
        assert dataPreprocess.seq_data_dir == 'train_data/' + model_name + '/seq.data'
        
class Test_execute: #类名大写打头
#     def __init__(self):这个不能加
    def test_seq_data_path(self):
        '''测试读入seq.data路径正确'''
        assert execute.seq_data_path == 'train_data/' + model_name + '/seq.data'
        
    def test_preprocess_sentence(self):
        '''测试preprocess_sentence函数正确正确'''
        assert execute.preprocess_sentence('test_str') == 'start test_str end'
        
    def test_checkpoint_dir(self):
        '''测试checkpoint保存路径正确'''
        assert execute.checkpoint_dir == 'model_data/' + model_name
        

class Test_othermodes:
    def test_get_weather(self):
        res_weather = otherModes.get_weather('北京')
        assert ('北京' in res_weather) and ('今日天气' in res_weather)
        
    def test_get_star(self):
        res_get_star = otherModes.get_star('天秤')
        assert (isinstance(res_get_star,str)) and (len(res_get_star) > 10)
        
    def test_get_news(self):
        res_get_news = otherModes.get_news()
        assert (isinstance(res_get_news,str)) and (len(res_get_news) > 10)
if __name__ == "__main":
    pytest.main(['-s','-v'])