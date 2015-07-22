#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
__author__ = 'Administrator'
'''


import json
import sys
import os
curr_file_dir = os.path.dirname(__file__)
database_dir= curr_file_dir.replace('database_data_server', 'database')
sys.path.append(database_dir)
import database_helper as db_helper


def save_hot_movies(movies):
    db_helper.save_hot_movies(movies)


def save_coming_soon_movies(movies):
    db_helper.save_coming_soon_movies(movies)
