#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-24 13:41:41
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$

import sys
import heapq
from collections import defaultdict
from operator import itemgetter
from math import sqrt

sys.path.append(r'load_movies')
sys.path.append(r'load_reviews')
from load_reviews import *
from load_movies import *


class MovieLens(object):
    '''
    udata: 用户对电影的评分
    uitem: 电影信息及其他电影细节
    genre: 类型：动作.探险.动画.儿童.喜剧.犯罪.记录.虚幻.黑丝.恐吓.音乐.推理.浪漫.科幻.惊悚.战争和西部
    movies:以dict存储, 包含url, genre, 电影ID, 名字, 视频, 上映日期
    reviews: 时间戳, 电影ID, 评分, 用户ID
    '''

    def __init__(self, udata, uitem):
        self.udata = udata
        self.uitem = uitem
        self.movies = {}
        self.reviews = defaultdict(dict)
        self.load_dataset()

    def load_dataset(self):
        # 加载数据到内存中，按ID为索引
        for movie in load_movies(self.uitem):
            self.movies[movie['movieid']] = movie
        #每一个人看了多部电影，每一个人对每一部所看电影的评价
        for review in load_reviews(self.udata):
            self.reviews[review['userid']][review['movieid']] = review

    def reviews_for_movie(self, movieid):
        # 返回某部电影的review
        for review in self.reviews.values():
            if movieid in review:
                yield review[movieid]

    def average_reviews(self):
        '''
        计算出某部电影的评分平均值
        生成器函数并yield数据值'''
        for movieid in self.movies:
            reviews = list(r['rating'] for r in self.reviews_for_movie(movieid))
            average = sum(reviews) / float(len(reviews))
            yield (movieid, average, len(reviews))

    def top_rated(self, n=10):
        # yield 前 n 个最高分电影
        return heapq.nlargest(n, self.bayesian_average(), key=itemgetter(1))

    def bayesian_average(self, c=59, m=3):
        '''
        基于贝叶斯的电影评分算法
        :param c: 置信参数：电影评分数量平均数： 59.45303210463734,更高的Ｃ值会平衡掉评分数少的电影（权重减少）
        :param m:
        :return:
        公式　
        '''
        for movieid in self.movies:
            reviews = list(r['rating'] for r in self.reviews_for_movie(movieid))
            average = ((c * m) + sum(reviews)) / float(c + len(reviews))
            yield (movieid, average, len(reviews))

    '''基于用户的协同过滤以及基于物品的协同过滤, 偏好空间：一组用户或者物品的Ｎ维特征空间
    通过比较用户或者物品在向量空间中是否邻近,最近邻推荐系统
    找到一种相似性或者距离的度量标准
    '''
    def shared_preferences(self, criticA, criticB):
        #用户Ａ，Ｂ 对某一部电影的评分
        if criticA not in self.reviews:
            raise KeyError("找不到评论家'%s'" % criticA)
        if criticB not in self.reviews:
            raise KeyError("找不到评论家'%s'" % criticB)
        # set来做交集操作，得出A和B都评分过的电影
        moviesA = set(self.reviews[criticA].keys())
        moviesB = set(self.reviews[criticB].keys())
        shared = moviesA & moviesB
        #print("用户%s和用户%s的交集："%(criticA,criticB),shared)
        # 创建一个评论过的的字典（以电影ID为关键字,以A,B评分的二元组（ratingA, ratingB）为值）
        reviews = {}
        for movieid in shared:
            reviews[movieid] = (self.reviews[criticA][movieid]['rating'],
                                self.reviews[criticB][movieid]['rating'],)
        return reviews

    def shared_critics(self, movieA, movieB):
        #某一个用户对电影Ａ，Ｂ的评分
        if movieA not in self.movies:
            raise KeyError("找不到电影'%s'" % movieA)
        if movieB not in self.movies:
            raise KeyError("找不到电影'%s'" % movieB)
        criticsA = set(critic for critic in self.reviews if movieA in self.reviews[critic])
        criticsB = set(critic for critic in self.reviews if movieB in self.reviews[critic])
        shared = criticsA & criticsB
        reviews = {}
        for critic in shared:
            reviews[critic] = (self.reviews[critic][movieA]['rating'],
                               self.reviews[critic][movieB]['rating'],)
        return reviews

    def euclidean_distance(self, criticA, criticB,prefs='users'):
        '''
          通过两个人的共同偏好作为向量来计算两个用户之间的欧式距离（偏好距离）
        '''
        if prefs == 'movies':
            preferences = self.shared_critics(criticA, criticB)
        else:
            preferences = self.shared_preferences(criticA, criticB)
        # 如果没有共同评论, return 0
        if len(preferences) == 0:
            return 0
        # 求偏差的平方的和
        sum_of_squres = sum([pow(a - b, 2) for a, b in preferences.values()])
        # 修正的欧式距离，返回值的范围为[0,1]，越接近0表示两者越不相同，越接近1，越相似
        return 1 / (1 + sqrt(sum_of_squres))

    def pearson_correlation(self, criticA, criticB,prefs='users'):
        '''
        计算用户A和用户B的皮尔逊相关度
        :param criticA: 用户A
        :param criticB: 用户B
        :return:[0 ～ 1]之间的一个值
        两个变量（a,b）的协方差除以两者标准差的乘积
        皮尔逊相关度：两个变量之间线性相关性度量的一种，返回（-1~1）之间的值: 接近-1, 负相关；接近1, 正相关；接近0, 无关联.
        '''
        if prefs == 'movies':
            preferences = self.shared_critics(criticA, criticB)
        else:
            preferences = self.shared_preferences(criticA, criticB)

        length = len(preferences)
        if length == 0:
            return 0
        sumA = sumB = sumSquareA = sumSquareB = sumProducts = 0
        for a, b in preferences.values():
            sumA += a
            sumB += b
            sumSquareA += pow(a, 2)
            sumSquareB += pow(b, 2)
            sumProducts += a * b
        numerator = (sumProducts * length) - (sumA * sumB)
        denominator = sqrt(((sumSquareA * length) - pow(sumA, 2)) * ((sumSquareB * length) - pow(sumB, 2)))
        if denominator == 0:
            return 0
        return abs(numerator / denominator)

    def similar_critics(self, user, metric='euclidean', n=None):
        '''
        寻找最匹配的用户(为某个用户找到评分相似的别的用户，判断群体喜好)
        :param user: 用户
        :param metric:度量指标：默认欧式距离
        :param n: 返回的结果数：默认是None
        :return: 排序并但返回排名前n的结果
        '''
        # 跳转表 选择使用不同的度量指标（欧氏距离/皮尔逊相关度）
        metrics = {
            'euclidean': self.euclidean_distance,
            'pearson': self.pearson_correlation
        }
        distance = metrics.get(metric, None)
        if user not in self.reviews:
            raise KeyError("没有 %s 用户" % user)
        if not distance or not callable(distance):
            raise KeyError("未知或未编程的距离度量方法 %s" % metric)
        # 计算对用户最合适的影评人
        critics = {}
        #循环遍历所有用户并计算与user的(欧氏距离/皮尔逊相关度)
        for critic in self.reviews:
            # 不能与自己进行比较
            if critic == user:
                continue
            critics[critic] = distance(user, critic)
        if n:
            return heapq.nlargest(n, critics.items(), key=itemgetter(1))
        return critics

    def similar_items(self, movie, metric='euclidean', n=None):
        '''
        基于物品的协同过滤：根据一组物品和另一组物品的相似程度做推荐
        :param movie:
        :param metric:
        :param n:
        :return:
        '''
        metrics = {
            'euclidean': self.euclidean_distance,
            'pearson': self.pearson_correlation
        }
        distance = metrics.get(metric, None)
        if movie not in self.reviews:
            raise KeyError("没有 %s 电影" % movie)
        if not distance or not callable(distance):
            raise KeyError("未知或未编程的距离度量方法 %s" % metric)
        # 计算对电影Ａ最相似的电影
        items = {}
        for item in self.movies:
            # 不能与自己进行比较
            if item == movie:
                continue
            items[item] = distance(item, movie,prefs='movies')
        if n:
            return heapq.nlargest(n, items.items(), key=itemgetter(1))
        return items

    def predict_ranking(self, user, movie, metric='euclidean', critics=None):
        '''
        基于用户的评分预测当前用户对电影的可能评分
        计算所有对电影Ａ的评分相对当前用户的加权平均值，权重为用户的评分，以及用户和当前用户的相似程度
        相似程度＊对电影Ａ的评分 /相似程度
        :param user: 用户
        :param movie: 电影
        :param metric: 距离指标：默认欧氏距离
        :param critics: 对predict_all_rankings的结果优化
        :return:
        '''
        #所有用户和user的相似程度
        critics = critics or self.similar_critics(user, metric=metric)
        total = 0.0
        simsum = 0.0
        for critic, similarity in critics.items():
            if movie in self.reviews[critic]:
                total += similarity * self.reviews[critic][movie]['rating']
                simsum += similarity

        if simsum == 0.0:
            return 0.0
        return total / simsum

    def predict_all_rankings(self, user, metric='euclidean', n=None):
        '''
        预测一个特定用户对所有电影的排名
        :param user:
        :param metric:
        :param n:
        :return: 排名前n的电影
        '''
        # 提前计算好critics而不是每次重新寻找critics来优化性能
        critics = self.similar_critics(user, metric=metric)
        # 对所有电影都进行判分，predict_ranking对某一部电影判分
        movies = {
            movie: self.predict_ranking(user, movie, metric, critics) for movie in self.movies
        }
        if n:
            return heapq.nlargest(n, movies.items(), key=itemgetter(1))
        return movies
