#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-24 13:40:17
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$

import csv
import datetime
from datetime import datetime


def load_movies(path, **kwargs):
    '''
    加载电影细节
    Load MovieLens movies
    :param path: 文件路径
    :param kwargs:
    :return: yield文件内容
    '''
    options = {'fieldnames': ('movieid', 'title', 'release', 'video', 'url'), 'delimiter': '|', 'restkey': 'genre', }
    #函数接受用户传递的任何参数
    options.update(kwargs)
    parse_int = lambda r, k: int(r[k])
    parse_date = lambda r, k: datetime.strptime(r[k], '%d-%b-%Y') if r[k] else None
    with open(path, 'r', encoding='gbk', errors='ignore') as movies:
        reader = csv.DictReader(movies,**options)
        for row in reader:
            row['movieid'] = parse_int(row, 'movieid')
            row['release'] = parse_date(row, 'release')
            row['video'] = parse_date(row, 'video')
            #使用yield而不是return是为了确保创建的生成器不会将这个数据集同时全部加载入内存
            #每次读出一段返回一段，回来接着读
            yield row
