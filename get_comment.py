# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import base64
import requests
import json
import time


headers = {'Host': 'music.163.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://music.163.com/song?id=347597',
            'Cookie': '__s_=1; _ntes_nnid=f17890f7160fd145486752ebbf2066df,1505221478108; _ntes_nuid=f17890f7160fd145486752ebbf2066df; JSESSIONID-WYYY=Z99pE%2BatJVOAGco1d%2FJpojOK94Xe9GHqe0epcCOj23nqP2SlHt1XwzWQ2FXTwaM2xgIN628qJGj8%2BikzfYkv%2FXAUo%2FSzwMxjdyO9oeQlGKBvH6nYoFpJpVlA%2F8eP57fkZAVEsuB9wqkVgdQc2cjIStE1vyfE6SxKAlA8r0sAgOnEun%2BV%3A1512200032388; _iuqxldmzr_=32; __utma=94650624.1642739310.1512184312.1512184312.1512184312.1; __utmc=94650624; __utmz=94650624.1512184312.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); playerid=10841206',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
           }


# 第二个参数
second_param = '010001'
# 第三个参数
third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
# 第四个参数
forth_param = '0CoJUm6Qyw8W8jud'


# 获取参数
def get_params(type, page):  # type为1时，page为uid，type为其他值时，page为页数
    iv = '0102030405060708'
    first_key = forth_param
    second_key = 16 * 'F'
    if type == 1:
        uid = page
        first_param = r'{"uid":"%s","type":"-1","limit":"1000","offset":"0","total":"true","csrf_token":""}' % str(uid)
        h_enctext = aes_encrypt(first_param, first_key, iv)
    else:
        if page == 1:  # 如果为第一页
            first_param = r'{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
            h_enctext = aes_encrypt(first_param, first_key, iv)
        else:
            offset = str((page-1)*20)
            first_param = r'{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' % (offset, 'false')
            h_enctext = aes_encrypt(first_param, first_key, iv)
    h_enctext = aes_encrypt(h_enctext, second_key, iv)
    return h_enctext


def get_encseckey():
    encseckey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
    return encseckey


def aes_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = str(base64.b64encode(encrypt_text))[2:-1]
    return encrypt_text


# 获得json数据
def get_json(url, params, encseckey):
    data = {
         'params': params,
         'encSecKey': encseckey
    }
    response = requests.post(url, headers=headers, data=data)
    return response.content


# 抓取用户听歌排行
def get_songsrank(uid):
    rank_list = []
    url = 'http://music.163.com/weapi/v1/play/record?csrf_token='
    params = get_params(1, uid)
    encseckey = get_encseckey()
    json_text = get_json(url, params, encseckey)
    json_dict = json.loads(str(json_text, encoding='utf-8'))
    try:
        for songs in json_dict['allData']:
            # songs['song']['name'] 歌曲名称
            rank_list.append(str(songs['song']['id']) + "\n")
    except KeyError:
        print('该uid已设置无法查看')
        exit(0)
    else:
        return rank_list


# 抓取一首歌的热门评论
def get_hot_comments(sid):
    hot_comments_list = []
    req = requests.get('http://music.163.com/api/v1/resource/comments/R_SO_4_' + sid, headers=headers)
    hot_comments_list.append(u'用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n')  # 头部信息
    json_dict = json.loads(req.text.encode(encoding='utf-8'))
    hot_comments = json_dict['hotComments']  # 热门评论
    print('共有%d条热门评论!' % len(hot_comments))
    for item in hot_comments:
            comment = item['content']  # 评论内容
            liked_count = item['likedCount']  # 点赞总数
            comment_time = item['time']  # 评论时间(时间戳)
            userid = item['user']['userId']  # 评论者id
            nickname = item['user']['nickname']  # 昵称
            avatar_url = item['user']['avatarUrl']  # 头像地址
            comment_info = str(userid) + " " + str(nickname) + " " + str(avatar_url) + " " + str(comment_time) + " " + str(liked_count) + " " + str(comment) + "\n"
            hot_comments_list.append(comment_info)
    return hot_comments_list


# 抓取一首歌的全部评论
def get_all_comments(url):
    all_comments_list = []
    all_comments_list.append(u'用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n')  # 头部信息
    params = get_params(2, 1)  # 第一页
    encseckey = get_encseckey()
    json_text = get_json(url, params, encseckey)
    json_dict = json.loads(str(json_text, encoding='utf-8'))
    comments_num = int(json_dict['total'])
    if comments_num % 20 == 0:
        page = comments_num / 20
    else:
        page = int(comments_num / 20) + 1
    print('共有%d页评论!' % page)
    for i in range(page):  # 逐页抓取
        params = get_params(2, i+1)
        encseckey = get_encseckey()
        json_text = get_json(url, params, encseckey)
        json_dict = json.loads(str(json_text, encoding='utf-8'))
        if i == 0:
            print("共有%d条评论!" % comments_num)  # 全部评论总数
        for item in json_dict['comments']:
            comment = item['content']  # 评论内容
            liked_count = item['likedCount']  # 点赞总数
            comment_time = item['time']  # 评论时间(时间戳)
            userid = item['user']['userId']  # 评论者id
            nickname = item['user']['nickname']  # 昵称
            avatar_url = item['user']['avatarUrl']  # 头像地址
            comment_info = str(userid) + " " + str(nickname) + " " + str(avatar_url) + " " + str(comment_time) + " " + str(liked_count) + " " + str(comment) + "\n"
            all_comments_list.append(comment_info)
        print('第%d页抓取完毕!' % (i+1))
    return all_comments_list


def save_to_file(list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(list)
    print('写入文件成功!')


if __name__ == "__main__":
    print(
        '1.爬取指定用户的听歌排行\n'
        + '2.爬取指定歌曲的热门评论\n'
        + '3.爬取指定歌曲的全部评论\n'
        + '0.退出'
    )
    choice = str(input('请选择操作:'))
    if choice == '1':
        uid = int(input('请输入用户uid:'))
        start_time = time.time()  # 开始时间
        rank_list = get_songsrank(uid)
        save_to_file(rank_list, 'rank.txt')
    elif choice == '2':
        comments_list = []
        sid = str(input('请输入想要爬取的歌曲ID：'))
        url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + sid + '?csrf_token='
        start_time = time.time()  # 开始时间
        filename = sid + '热评.txt'
        comments_list = get_hot_comments(sid)
        save_to_file(comments_list, filename)
    elif choice == '3':
        comments_list = []
        sid = str(input('请输入想要爬取的歌曲ID：'))
        url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + sid + '?csrf_token='
        start_time = time.time()  # 开始时间
        filename = sid + '全部评论.txt'
        comments_list = get_all_comments(url)
        save_to_file(comments_list, filename)
    else:
        start_time = 0
        exit(0)
    end_time = time.time()  # 结束时间
    print('爬取耗时%f秒' % (end_time - start_time))
