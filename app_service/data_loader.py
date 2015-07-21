#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
__author__ = 'Administrator'
'''


import json
import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.curdir), 'database'))
import database_helper as db_helper


def load_hot_movies():
    return db_helper.load_hot_movies()

def load_coming_soon_movies():
    return db_helper.load_coming_soon_movies()


