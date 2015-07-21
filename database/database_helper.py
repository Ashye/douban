#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
__author__ = 'Administrator'
'''

import json


movie_hot = 'hot'
movie_coming_soon = 'coming_soon'

movie_db_path = dict(
    hot=r'./database/hot_movies.db',
    coming_soon=r'./database/coming_soon_movies.db'
)


def save_hot_movies(movies):
    override_local_database(movies, movie_hot)


def save_coming_soon_movies(movies):
    override_local_database(movies, movie_coming_soon)


def override_local_database(movies, movie_type):
    write_obj_to_database_in_json(movies, movie_type)


def write_obj_to_database_in_json(data, movie_type):
    file_obj = open(movie_db_path[movie_type], 'w')
    file_obj.truncate(0)
    json.dump(data, file_obj, ensure_ascii=False)
    file_obj.close()


def load_hot_movies():
    return load_movies_from_database_in_json(movie_hot)


def load_coming_soon_movies():
    return load_movies_from_database_in_json(movie_coming_soon)


def load_movies_from_database_in_json(movie_type):
    movies_json = None
    try:
        file_obj = open(movie_db_path[movie_type], 'r')
        movies_json = json.load(file_obj)
        # print(type(movies_json))
        file_obj.close()
    except:
        print('read json data from file error...')
    return movies_json
