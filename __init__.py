#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-23 15:13:51
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$
import csv
import datetime
import os
import sys

sys.path.append(r'relative_path')
sys.path.append(r'MovieLens')
sys.path.append(r'Recommender')
from relative_path import *
from MovieLens import *
from Recommender import *

if __name__ == '__main__':
    data = relative_path("ml-100k/u.data")
    print(data)
    item = relative_path("ml-100k/u.item")
    model = MovieLens(data, item)
    print("电影评分数量平均数：",float(sum(num for mid,avg,num in model.average_reviews()))/len(model.movies))
    print("与用户%d欧式距离："%232)
    for item in model.similar_critics(232, 'euclidean', n=10):
        print("%4i: %0.3f" % item)
    print("与用户%d皮尔逊相关度："%232)
    for item in model.similar_critics(232, 'pearson', n=10):
        print("%4i: %0.3f" % item)

    print("用户%d与%d之间欧式距离：   %s " %(232,532,model.euclidean_distance(232, 532)))
    print("用户%d与%d之间皮尔逊相关度:  %s " % (232, 532,model.pearson_correlation(232, 532)))
    print("基于贝叶斯评分算法的电影排名前十:")
    for mid, avg, num in model.top_rated(10):
        title=model.movies[mid]['title']
        print("[%0.3f average rating (%i reviews)] %s" %(avg,num,title))
    

    print("预测ID为%i的用户对电影ID为%i,通过%s的方式评分为:%s" % (422, 50, 'euclidean', model.predict_ranking(422, 50, 'euclidean')))
    print("预测ID为%i的用户对电影ID为%i,通过%s的方式评分为:%s" % (422, 50, 'pearson', model.predict_ranking(422, 50, 'pearson')))
    print("系统预测的用户%d最喜欢的排名前十的电影:"%578)
    for mid, rating in model.predict_all_rankings(578, 'pearson', 10):
        print("%0.3f:%s" % (rating, model.movies[mid]['title']))

    print("电影ID%d的相似性排名前十部电影："%631)
    for movie, similarity in model.similar_items(631, 'pearson',10):
        print("%0.3f:%s" % (similarity, model.movies[movie]['title']))

    modelA = Recommender(data)
    print(modelA.reviews)

    print("%0.3f%% 稀疏" % modelA.sparsity())
    print("%0.3f%% 密集 " % modelA.density())

    print("从文件中读取并排名,用户%d对电影推测排名的结果："%234)
    # modelA.build('reccod.pickle')
    rec = Recommender.load('reccod.pickle')
    for item in rec.top_rated(234):
        print("%i: %0.3f" % item)