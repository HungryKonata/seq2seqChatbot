from urllib.parse import quote
import urllib.request
import gzip
import requests
from lxml import etree
import json
import re
import requests
import execute
import random

# 使用talk2
# 人输入的问句字符串
# req_msg = '你好啊'

##规定使用哪个模型
# model_name = 'talk2'
# cp_dir = 'model_data/' + model_name

# res_msg = execute.predict(req_msg, cp_dir)
# print(res_msg)

# 询问到天气时爬虫天气资讯
def get_weather(keyword):
    try:
        keyword = re.findall('(..)\u5929\u6c14', keyword)[0]  
    except:
        pass
    url = 'https://www.tianqi.com/tianqi/search?keyword=' + keyword
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    response = requests.get(url,headers=headers)
    tree = etree.HTML(response.text)
    # 检测城市天气是否存在
    try:
        city_name = tree.xpath('//dd[@class="name"]/h2/text()')
    except:
        content = '没有该城市天气信息，请确认查询格式'
        return content
    week = tree.xpath('//dd[@class="week"]/text()')[0]
    now = tree.xpath('//p[@class="now"]')[0].xpath('string(.)')
    temp = tree.xpath('//dd[@class="weather"]/span')[0].xpath('string(.)')
    shidu = tree.xpath('//dd[@class="shidu"]/b/text()')
    kongqi = tree.xpath('//dd[@class="kongqi"]/h5/text()')[0]
    pm = tree.xpath('//dd[@class="kongqi"]/h6/text()')[0]
    content = "{0}{1}天气\n当前温度：{2}\n今日天气：{3}\n{4}\n{5}\n{6}".format(keyword, week.split('\u3000')[0], now, temp, '\n'.join(shidu),kongqi,pm)
    return content

def get_star(keyword):  # 查询星座运势
    try:
        keyword = re.findall('(..)\u5ea7', keyword)[0]
    except:
        pass
    xingzuo_dict = {'白羊':'aries','金牛':'taurus','双子':'gemini','巨蟹':'cancer','狮子':'leo','处女':'virgo','天秤':'libra','天蝎':'scorpio','射手':'sagittarius','摩羯':'capricorn','水瓶':'aquarius','双鱼':'pisces'}
    keyword = xingzuo_dict[keyword]
    url = 'https://www.xzw.com/fortune/' + keyword
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    response = requests.get(url,headers=headers)
    tree = etree.HTML(response.text)
    # 检测城市天气是否存在
    yunshi = tree.xpath('//*[@id="view"]/div[2]/div[3]/div[2]/p[1]/span/text()')  # 注意最后的text()!!否则输出是一个奇怪的数据结构
    return yunshi[0]



def get_news():  # 使用免费API查新闻
    url = 'https://api.apiopen.top/getWangYiNews'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    response = requests.get(url,headers=headers)
    news = json.loads(response.text)
    index = random.randint(0,7)
    return news['result'][index]['title']  # 随机选一条新闻


def talk2(req_msg):  # 模型2 
    #规定使用哪个模型
    model_name = 'talk2'
    cp_dir = 'model_data/' + model_name
    res_msg = execute.predict(req_msg, cp_dir)
    return res_msg


def talk1(req_msg):  # 模型1
    #规定使用哪个模型
    model_name = 'talk1'
    cp_dir = 'model_data/' + model_name
    res_msg = execute.predict(req_msg, cp_dir)
    return res_msg
