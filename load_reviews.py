#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-24 13:40:59
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$
import csv
import datetime


def load_reviews(path, **kwargs):
    '''
    加载电影评价
    :param path: 文件路径
    :param kwargs:
    :return: yield　每一列
    '''
    #dict
    options = {'fieldnames': ('userid', 'movieid', 'rating', 'timestamp'), 'delimiter': '\t', }
    options.update(kwargs)
    parse_date = lambda r, k:datetime.fromtimestamp(float(r[k]))
    parse_int = lambda r, k:int(r[k])
    with open(path, 'r') as reviews:
        reader = csv.DictReader(reviews, **options)
        for row in reader:
            row['movieid'] = parse_int(row, 'movieid')
            row['userid'] = parse_int(row,'userid' )
            row['rating'] = parse_int(row, 'rating')
            row['timestamp'] = parse_int(row, 'timestamp')
            yield row

