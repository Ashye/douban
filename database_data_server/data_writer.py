#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
__author__ = 'Administrator'
'''


import json
import sys
import os
sys.path.append(os.path.join(os.path.abspath(os.path.curdir), 'database'))
import database_helper as db_helper


def save_hot_movies(movies):
    db_helper.save_hot_movies(movies)


def save_coming_soon_movies(movies):
    db_helper.save_coming_soon_movies(movies)
