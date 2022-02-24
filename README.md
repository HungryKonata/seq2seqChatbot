# seq2seqChatbot
一个用中文语料训练的对话机器人，使用的语料为小黄鸡语料库和青云语料库

# 示例

![展示](https://img-blog.csdnimg.cn/8a20ecdcd3b9409b99c95a745d0eff6c.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5q2k5pa55a6255qE56m66IW5,size_19,color_FFFFFF,t_70,g_se,x_16)

![登录](https://img-blog.csdnimg.cn/836420f1f9c04806bb7bfa3dce661e87.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5q2k5pa55a6255qE56m66IW5,size_20,color_FFFFFF,t_70,g_se,x_16)

# 部署tomcat服务器

下载jdk环境，下载tomcat包，将前端页面放入webapps文件夹后，启动tomcat即可访问。

部署nodejs

官网下载并安装nodejs

接下来使用npm命令安装mysql访问包，express和socket.io

npm install --save express

npm install --save socket.io

npm install mysql

Nodejs文件编写完成后使用node index.js启动，或使用nohup指令保持后台运行。

# Requirements
* tensorflow
* jieba
* nodejs
* requests
* re
* sqlalchemy

# 分工

xzh: 前端，数据库，部署

dhy: 模型训练，语料处理，后端，自动化测试

lwz: 爬虫，选择模式，模型训练

software engineering homework
