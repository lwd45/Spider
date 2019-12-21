import csv
import json
import multiprocessing
import os
import time
from multiprocessing.pool import Pool
from random import random

import requests
from bs4 import BeautifulSoup


def writer_tofile(all_news, save_path):  # 保存文件
    if not os.path.exists("/".join(save_path.split('/')[0:-1])):  # 创建保存路径文件
        os.makedirs("/".join(save_path.split('/')[0:-1]))
    with open(save_path, 'a+', newline='', encoding='utf-8', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(all_news)


def get_content_from_h5(soup, id_):  # 根据id解析文章内容，现在正文的div的id是 artibody ，之前的是 article ?
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


def get_content(article_url):  # 调用上面的函数解析文章内容
    rsp = requests.get(article_url)
    rsp.encoding = 'utf-8'
    html = rsp.text.replace(u'\xa0', u'').replace(u'\u3000', u'').encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    content = get_content_from_h5(soup, 'artibody')
    if len(content) == 0:
        content = get_content_from_h5(soup, 'article')
    return content


def get_title_url(web_url, save_path):  # 获得title和内容url,并调用其他方法解析出内容写入文件(只要了标题和正文)
    json_result = json.loads(requests.get(url=web_url).text)
    data = json_result['result']['data']
    for item in data:
        title = item['title']
        content = get_content(item['url'])
        data = [title, content]
        writer_tofile(data, save_path)  # 保存文件


# def start(pageid, lid, start, end, path) pageid lid是str表示新闻类型， start end是int表示最大爬取多少页, path是str表示保存路径
def start_spider(param_list):  # 这里使用一个数组封装
    pageid, lid, start, end, path = param_list[0], param_list[1], param_list[2], param_list[3], param_list[4]
    while start < end:
        url_parten = 'https://feed.mix.sina.com.cn/api/roll/get?pageid={}&lid={}&k=&num=50&page={}&r={}'
        get_title_url(url_parten.format(pageid, lid, start, random()), path)
        start += 1


if __name__ == '__main__':
    # 跑步  http://sports.sina.com.cn/roll/#pageid=13&lid=583&k=&num=50&page=1
    # 足球  http://sports.sina.com.cn/roll/#pageid=13&lid=572&k=&num=50&page=1
    # NBA  http://sports.sina.com.cn/roll/#pageid=13&lid=571&k=&num=50&page=1
    # 赛车  http://sports.sina.com.cn/roll/#pageid=13&lid=585&k=&num=50&page=1
    # 股市 https://news.sina.com.cn/roll/#pageid=153&lid=2517&k=&num=50&page=1
    # 财经 https://news.sina.com.cn/roll/#pageid=153&lid=2516&k=&num=50&page=1
    # 科技 https://news.sina.com.cn/roll/#pageid=153&lid=2515&k=&num=50&page=1
    # 军事 https://news.sina.com.cn/roll/#pageid=153&lid=2514&k=&num=50&page=1
    # 娱乐 https://news.sina.com.cn/roll/#pageid=153&lid=2513&k=&num=50&page=1
    # 彩票  http://sports.sina.com.cn/roll/#pageid=13&lid=581&k=&num=50&page=1
    # ------------------以下参数自己修改----------------
    start_page = 1
    end_page = 2
    # home_path = 'test_data/'
    home_path = 'train_data/'
    # ------------------以上参数自己修改----------------
    params = [  # pageid, lid, start_page(包含), end_page(不包含), save_path
        ('153', '2513', start_page, end_page, home_path + '娱乐.csv'),
        ('153', '2514', start_page, end_page, home_path + '军事.csv'),
        ('153', '2515', start_page, end_page, home_path + '科技.csv'),
        ('153', '2516', start_page, end_page, home_path + '财经.csv'),
        ('153', '2517', start_page, end_page, home_path + '股市.csv'),
        ('13', '585', start_page, end_page, home_path + '赛车.csv'),
        ('13', '571', start_page, end_page, home_path + '篮球.csv'),
        ('13', '572', start_page, end_page, home_path + '足球.csv'),
        ('13', '583', start_page, end_page, home_path + '跑步.csv'),
        ('13', '581', start_page, end_page, home_path + '彩票.csv'),
    ]
    print('program start...')
    start_time = time.time()
    pool = Pool(processes=multiprocessing.cpu_count() - 1)  # 开启多进程,（进程并不会同时运行）
    pool.map_async(start_spider, params)
    pool.close()
    pool.join()
    print('program run time:', time.time() - start_time, 'seconds')
