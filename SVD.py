#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-24 13:44:25
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$

import numpy as np
'''
矩阵分解（奇异值分解）：对基础的基于最近邻相似性评分的协同过滤进行优化的方法
'''
def initialize(R, K):
    N, M = R.shape
    P = np.random.rand(N, K)
    Q = np.random.rand(M, K)
    return P, Q


def factor(R, P=None, Q=None, K=2, steps=5000, alpha=0.0002, beta=0.02):
    if not P or not Q:
        P, Q = initialize(R, K)
    Q = Q.T

    rows, cols = R.shape
    for step in range(steps):
        for i in range(rows):
            for j in range(cols):
                if R[i, j] > 0:
                    eij = R[i, j] - np.dot(P[i, :], Q[:, j])
                    for k in range(K):
                        P[i, k] = P[i, k] + alpha * (2 * eij * Q[k, j] - beta * P[i, k])
                        Q[k, j] = Q[k, j] + alpha * (2 * eij * P[i, k] - beta * Q[k, j])

        eR = np.dot(P, Q)  # Compute dot product only once
        e = 0
        for i in range(rows):
            for j in range(cols):
                if R[i, j] > 0:
                    e = e + pow((R[i, j] - eR[i, j]), 2)
                    for k in range(K):
                        e = e + (beta / 2) * (pow(P[i, k], 2) + pow(Q[k, j], 2))
        if e < 0.001:
            break

    return P, Q.T