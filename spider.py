import csv
import multiprocessing
import time
from multiprocessing.pool import Pool
from random import random
import json
import requests
from bs4 import BeautifulSoup


def writer_tofile(all_news, save_path):  # 保存文件
    with open(save_path, 'a+', newline='', encoding='utf-8', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(all_news)


def get_content_from_h5(soup, id_):  # 解析文章内容，现在正文的div的id是 artibody ，之前的是 article
    article_div = soup.find('div', id=id_)
    article_div_soup = BeautifulSoup(str(article_div), 'html.parser')
    content_tx_ = article_div_soup.find_all('p')
    content = ''
    for x in content_tx_:
        if 'url' in x.text:  # 去掉还有电影的新闻怕去的内容出现js代码
            content = content
        else:
            content += x.text.strip()
    return content


def get_article_content(article_url):  # 调用上面的函数解析文章内容
    rsp = requests.get(article_url)
    rsp.encoding = 'utf-8'
    html = rsp.text.replace(u'\xa0', u'').replace(u'\u3000', u'').encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    content = get_content_from_h5(soup, 'artibody')
    if len(content) == 0:
        content = get_content_from_h5(soup, 'article')
    return content


def get_title_url(web_url, save_path):  # 获得title和内容url,并调用其他方法解析出内容写入文件
    json_result = json.loads(requests.get(url=web_url).text)
    data = json_result['result']['data']
    for item in data:
        title = item['title']
        content = get_article_content(item['url'])
        data = [title, content]
        writer_tofile(data, save_path)


# def start(news_type, max_page, save_path) news_type是str表示新闻类型， max_page是int表示最大爬取多少页, save_path是str表示保存路径
def start(param_list):  # 这里使用一个数组封装
    for i in range(param_list[2]):
        get_title_url('https://feed.mix.sina.com.cn/api/roll/get?pageid=' + param_list[0] + '&lid='
                      + param_list[1] + '&k=&num=50&page=' + str(i + 1) + '&r=' + str(random()), param_list[3])


if __name__ == '__main__':
    start_time = time.time()
    pool = Pool(processes=multiprocessing.cpu_count() - 1)  # 开启多进程,（有时候，进程不会同时运行）
    params = [  # pageid,lid,max_page,path
        ('153', '2513', 1, 'data/娱乐.csv'),  # 娱乐 https://news.sina.com.cn/roll/#pageid=153&lid=2513&k=&num=50&page=1
        ('153', '2514', 1, 'data/军事.csv'),  # 军事 https://news.sina.com.cn/roll/#pageid=153&lid=2514&k=&num=50&page=1
        ('153', '2515', 1, 'data/科技.csv'),  # 科技 https://news.sina.com.cn/roll/#pageid=153&lid=2515&k=&num=50&page=1
        ('153', '2516', 1, 'data/财经.csv'),  # 财经 https://news.sina.com.cn/roll/#pageid=153&lid=2516&k=&num=50&page=1
        ('153', '2517', 1, 'data/股市.csv'),  # 股市 https://news.sina.com.cn/roll/#pageid=153&lid=2517&k=&num=50&page=1
        ('13', '585', 1, 'data/赛车.csv'),  # 赛车  http://sports.sina.com.cn/roll/#pageid=13&lid=585&k=&num=50&page=1
        ('13', '609', 1, 'data/篮球.csv'),  # 篮球  http://sports.sina.com.cn/roll/#pageid=13&lid=609&k=&num=50&page=1
        ('13', '572', 1, 'data/足球.csv'),  # 足球  http://sports.sina.com.cn/roll/#pageid=13&lid=572&k=&num=50&page=1
        ('13', '583', 1, 'data/跑步.csv'),  # 跑步  http://sports.sina.com.cn/roll/#pageid=13&lid=583&k=&num=50&page=1
        ('13', '581', 1, 'data/彩票.csv'),  # 彩票  http://sports.sina.com.cn/roll/#pageid=13&lid=581&k=&num=50&page=1
    ]
    pool.map_async(start, params)  # pool.map(start, params)
    pool.close()
    pool.join()
    end_time = time.time()
    print('program run time:', end_time - start_time, 'seconds')
