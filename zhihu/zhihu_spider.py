import json
import multiprocessing
import os
import re
import time
import urllib
import random
from multiprocessing.pool import Pool

import requests


# 保存内容到本地
def save_content(title, author_name, author_url, image_urls, request_header):
    save_path = title
    if not os.path.exists(save_path):  # 创建保存路径文件
        os.makedirs(save_path)

    # 保存用户主页url
    with open(save_path + '/AAA-用户主页url.txt', 'a+', encoding='utf-8', errors='ignore') as f:
        f.write(author_name + ":    " + author_url + '\n')

    # 开始下载用户图片
    percentage, total = 1, len(image_urls)
    for img_url in image_urls:
        filename = save_path + '/' + author_name + '-' + str(random.randint(1000000, 9999999)) + ".jpg"
        print('正在下载：', author_name, '的图片，进度：', percentage, '/', total)
        urllib.request.urlretrieve(img_url, filename=filename)
        percentage = percentage + 1


# 获取回答的内容
# answer_url：每一个回答的url
def get_content(answer_url, request_header):
    json_data = json.loads(requests.get(url=answer_url, headers=request_header).text)
    data = json_data['data']
    for author_list in data:
        answer_content = author_list['content']
        author_name = author_list['author']['name']  # 答主名称
        image_urls = re.findall('data-original=\"(https://.*?)"', answer_content)  # 答主发布的高清图片url集合
        if len(image_urls) == 0:  # 没有图片就返回
            continue
        title = author_list['question']['title']  # 题目标题
        author_url = "https://www.zhihu.com/people/" + author_list['author']['url_token'] + "/activities"  # 答主用户主页
        # 保存内容到本地
        save_content(title, author_name, author_url, set(image_urls), request_header)


# 获取下面所有回答的url
# param_url:问题的返回json连接,      request_header:请求头
def get_answer_url(param_url, request_header):
    json_data = json.loads(requests.get(url=param_url, headers=request_header).text)
    answer_count = json_data['paging']['totals']  # 总回答数
    offset = 0
    param_url = param_url.split('&')[0]
    while offset < answer_count:
        answer_url = param_url + '&offset=' + str(offset) + '&limit=10&platform=desktop&sort_by=default'
        offset += 10
        # 获取回答的内容
        get_content(answer_url, request_header)


if __name__ == '__main__':
    start_time = time.time()
    pool = Pool(processes=multiprocessing.cpu_count() - 1)  # 开启多进程,（进程并不会同时运行）
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36',
    }
    # 将url替换成你想要下载的问题的json链接
    url = 'https://www.zhihu.com/api/v4/questions/312744244/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset=0&limit=20&sort_by=updated'
    # get_answer_url(url, header)

    json_data = json.loads(requests.get(url=url, headers=header).text)
    answer_count = json_data['paging']['totals']  # 总回答数
    offset = 0
    param_url = url.split('&')[0]
    while offset < answer_count:
        answer_url = param_url + '&offset=' + str(offset) + '&limit=5&platform=desktop&sort_by=default'
        offset += 5
        # 获取回答的内容
        # get_content(answer_url, header)
        pool.apply_async(get_content, args=(answer_url, header))
    pool.close()
    pool.join()
    print('program run time:', time.time() - start_time, 'seconds')
