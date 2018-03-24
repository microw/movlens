#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-24 13:42:44
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$
import pickle
import numpy as np
import csv
import sys
import time
import heapq
from operator import itemgetter

sys.path.append(r'load_reviews')
sys.path.append(r'SVD')

from load_reviews import *
from SVD import *


class Recommender(object):

    @classmethod
    def load(klass, pickle_path):
        with open(pickle_path, 'rb') as pkl:
            return pickle.load(pkl)

    def __init__(self, udata, description=None):
        self.udata = udata
        self.users = None
        self.movies = None
        self.reviews = None

        self.build_start = None
        self.build_finish = None
        self.description = None

        self.model = None
        self.features = 2
        self.steps = 5000
        self.alpha = 0.0002
        self.beta = 0.02

        self.load_dataset()

    def dump(self, pickle_path):
        with open(pickle_path, 'wb') as pkl:
            pickle.dump(self, pkl)

    def load_dataset(self):
        self.users = set([])
        self.movies = set([])
        for review in load_reviews(self.udata):
            self.users.add(review['userid'])
            self.movies.add(review['movieid'])

        self.users = sorted(self.users)
        self.movies = sorted(self.movies)

        self.reviews = np.zeros(shape=(len(self.users), len(self.movies)))

        for review in load_reviews(self.udata):
            mid = self.movies.index(review['movieid'])
            uid = self.users.index(review['userid'])
            self.reviews[uid, mid] = review['rating']

    def sparsity(self):
        return 1 - self.density()

    def density(self):
        nonzero = float(np.count_nonzero(self.reviews))
        return nonzero / self.reviews.size

    def build(self, output=None):
        options = {
            'K': self.features,
            'steps': self.steps,
            'alpha': self.alpha,
            'beta': self.beta,
        }
        self.build_start = time.time()
        self.P, self.Q = factor(self.reviews, **options)
        self.model = np.dot(self.P, self.Q.T)
        self.build_finish = time.time()
        if output:
            self.dump(output)


    def predict_ranking(self, user, movie):
        #user对movie的可能评分
        uidx = self.users.index(user)
        midx = self.movies.index(movie)
        if self.reviews[uidx, midx] > 0:
            return None
        return self.model[uidx, midx]

    def top_rated(self, user, n=12):
        #user 对电影评分排名前ｎ的可能结果
        movies = [(mid, self.predict_ranking(user, mid)) for mid in self.movies if self.predict_ranking(user, mid)]
        return heapq.nlargest(n, movies, key=itemgetter(1))
