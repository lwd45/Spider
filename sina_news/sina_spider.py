import csv
import multiprocessing
import os
import time
from multiprocessing.pool import Pool
from random import random
import json
import requests
from bs4 import BeautifulSoup


# 保存文件
def writer_tofile(all_news, save_path):
    if not os.path.exists(save_path.split('/')[0]):  # 创建保存路径文件
        os.makedirs(save_path.split('/')[0])
    with open(save_path, 'a+', newline='', encoding='utf-8', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(all_news)


# 解析文章内容，现在正文的div的id是 artibody ，之前的是 article
def get_content_from_h5(soup, id_):
    article_div = soup.find('div', id=id_)
    article_div_soup = BeautifulSoup(str(article_div), 'html.parser')
    content_tx_ = article_div_soup.find_all('p')
    content = ''
    for x in content_tx_:
        if 'url' in x.text:  # 去掉一些有电影的新闻爬取的内容出现js代码
            content = content
        else:
            content += x.text.strip()
    return content


# 调用上面的函数解析文章内容
def get_article_content(article_url):
    rsp = requests.get(article_url)
    rsp.encoding = 'utf-8'
    html = rsp.text.replace(u'\xa0', u'').replace(u'\u3000', u'').encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    content = get_content_from_h5(soup, 'artibody')
    if len(content) == 0:
        content = get_content_from_h5(soup, 'article')
    return content


# 获得title和内容url,并调用其他方法解析出内容写入文件(只要了标题和正文)
def get_title_url(web_url, save_path):
    json_result = json.loads(requests.get(url=web_url).text)
    data = json_result['result']['data']
    for item in data:
        title = item['title']
        content = get_article_content(item['url'])
        data = [title, content]
        writer_tofile(data, save_path)


# def start(pageid, lid, start_page, end_page, save_path) lid是str表示新闻类型， start_page, end_page是int表示开始结束页, save_path是str表示保存路径
def start(params):  # 这里使用一个数组封装
    pageid, lid, start_page, end_page, save_path = params[0], params[1], params[2], params[3], params[4]
    while start_page < end_page:
        get_title_url('https://feed.mix.sina.com.cn/api/roll/get?pageid=' + pageid + '&lid='
                      + lid + '&k=&num=50&page=' + str(start_page) + '&r=' + str(random()), save_path)
        start_page += 1


if __name__ == '__main__':
    start_time = time.time()
    pool = Pool(processes=multiprocessing.cpu_count() - 1)  # 开启多进程,（进程并不会同时运行）
    # 娱乐 https://news.sina.com.cn/roll/#pageid=153&lid=2513&k=&num=50&page=1
    # 军事 https://news.sina.com.cn/roll/#pageid=153&lid=2514&k=&num=50&page=1
    # 科技 https://news.sina.com.cn/roll/#pageid=153&lid=2515&k=&num=50&page=1
    # 财经 https://news.sina.com.cn/roll/#pageid=153&lid=2516&k=&num=50&page=1
    # 股市 https://news.sina.com.cn/roll/#pageid=153&lid=2517&k=&num=50&page=1
    # 赛车  http://sports.sina.com.cn/roll/#pageid=13&lid=585&k=&num=50&page=1
    # NBA  http://sports.sina.com.cn/roll/#pageid=13&lid=571&k=&num=50&page=1
    # 足球  http://sports.sina.com.cn/roll/#pageid=13&lid=572&k=&num=50&page=1
    # 跑步  http://sports.sina.com.cn/roll/#pageid=13&lid=583&k=&num=50&page=1
    # 棋牌  http://sports.sina.com.cn/roll/#pageid=13&lid=576&k=&num=50&page=1
    # 彩票  http://sports.sina.com.cn/roll/#pageid=13&lid=581&k=&num=50&page=1
    param_list = [  # pageid, lid, start_page（包含）, end_page(不包含), save_path, 在这里更改想要的参数
        ('153', '2513', 1, 2, 'data/娱乐.csv'),
        ('153', '2514', 1, 2, 'data/军事.csv'),
        ('153', '2515', 1, 2, 'data/科技.csv'),
        ('153', '2516', 1, 2, 'data/财经.csv'),
        ('153', '2517', 1, 2, 'data/股市.csv'),
        ('13', '585', 1, 2, 'data/赛车.csv'),
        ('13', '571', 1, 2, 'data/篮球.csv'),
        ('13', '572', 1, 2, 'data/足球.csv'),
        ('13', '583', 1, 2, 'data/跑步.csv'),
        # ('13', '583', 1, 2, 'data/棋牌.csv'),
        ('13', '581', 1, 2, 'data/彩票.csv'),
    ]
    pool.map_async(start, param_list)  # pool.map(start, params)
    pool.close()
    pool.join()
    end_time = time.time()
    print('program run time:', end_time - start_time, 'seconds')
