#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
__author__ = 'Administrator'
'''


import json
import os
import sys

curr_file_dir = os.path.dirname(__file__)
database_dir= curr_file_dir.replace('app_service', 'database')
sys.path.append(database_dir)


import database_helper as DBHelper




def load_hot_movies():
    return DBHelper.load_hot_movies()

def load_coming_soon_movies():
    return DBHelper.load_coming_soon_movies()


