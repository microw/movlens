#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-03-24 13:43:22
# @Author  : chen (fpchen@outlook.com)
# @Link    : https://github.com/fpChan
# @Version : $Id$

import os


def relative_path(path):
    '''
    Return a path relative from file
    :param path: 文件路径
    :return: 文件路径
    '''
    dirname = os.path.dirname(os.path.realpath('__file__'))
    path = os.path.join(dirname, path)
    return os.path.normpath(path)
