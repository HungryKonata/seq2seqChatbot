from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymysql
import pandas
import time
import re
import json
import otherModes
from snownlp import SnowNLP


def chat_with_dbdata():
    # 创建对象的基类:
    Base = declarative_base()
    
    # ORM对象:
    class Dialog(Base):
        def __init__(self, id, c_to_s, s_to_c, model):
            self.id = id
            self.c_to_s = c_to_s
            self.s_to_c = s_to_c
            self.model = model 
        # 表的名字:
        __tablename__ = 'software_engineering'
    
        # 表的结构:
        id = Column(String(20))
        c_to_s = Column(String(200))
        s_to_c = Column(String(200))
        model = Column(String(5))
        
    # 初始化数据库连接:
    # engine = create_engine('mysql+pymysql://dev:123456^Abcde@121.42.142.102:3306/bzyun_wxorder')  # 库名bzyun_wxorder, engine即一库
    # 创建DBSession类型:
    db = create_engine('mysql+pymysql://root:123456@localhost:3306/software_engineering')  # 库名engine即一库

    DBSession = sessionmaker(bind=db)
    session = DBSession()  # session是数据库的句柄

    row = session.query(Dialog).order_by(Dialog.id)[0]  # 取第一条结果
    req = row.c_to_s  # 取出第一条结果进行询问
    #判断变化
    while True:
        row = session.query(Dialog).order_by(Dialog.id)[0]
        tmp = row.c_to_s
        if tmp!=req:
            req=tmp
            break
        time.sleep(1)
            
    if '座' in req:
        star = re.findall('(..)\u5ea7', req)[0]
        res= get_star(star)
    elif '新闻' in req:
        res = get_news()
    elif '天气' in req:
        place = re.findall('(..)\u5929\u6c14', req)[0]
        print(place)
        res = get_weather(place)
    else:
        res1 = talk1(req)
        res2 = talk2(req)
        snow1 = SnowNLP(res1)
        snow2 = SnowNLP(res2)
        if snow1.sentiments > snow2.sentiments:
            res = res1
        else:
            res = res2
    
    new_dialog = Dialog(row.id, req, res, row.model)
    session.add(new_dialgo)
    session.commit()

def chat_with_input():
    while True:
        req = input('>>>')
        res = ''
        if '座' in req:
            star = re.findall('(..)\u5ea7', req)[0]
            res= get_star(star)
        elif '新闻' in req:
            res = get_news()
        elif '天气' in req:
            place = re.findall('(..)\u5929\u6c14', req)[0]
            print(place)
            res = get_weather(place)
        else:
            res1 = talk1(req)
            res2 = talk2(req)
            snow1 = SnowNLP(res1)
            snow2 = SnowNLP(res2)
            if snow1.sentiments > snow2.sentiments:
                res = res1
            else:
                res = res2
        print(res)
    
    
if __name__=='main':
    while True:
        chat_with_dbdata()
        
    
    
#调用decode_line对生成回答信息
# res_msg = execute.predict(req_msg, cp_dir)
# print(res_msg)


# new_dialog = Dialog(0, '你好啊', '好啊 你更好', '2')
# session.add(new_dialgo)
## 提交即保存到数据库:
# session.commit()
## 关闭session:
# session.close()
