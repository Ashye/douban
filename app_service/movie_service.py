#!/usr/bin/env python3
# -*- codeing:utf-8 -*-


import tornado.web
import json

import data_loader as MovieLoader


class HotMoviesEventHandler(tornado.web.RequestHandler):
    def get(self, params=None):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(self.load_hot_movies(), ensure_ascii=False))

    def load_hot_movies(self):
        return MovieLoader.load_hot_movies()


class ComingSoonMoviesEventHandler(tornado.web.RequestHandler):
    def get(self, param=None):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(self.load_coming_soon_movies(), ensure_ascii=False))

    def load_coming_soon_movies(self):
        return MovieLoader.load_coming_soon_movies()
