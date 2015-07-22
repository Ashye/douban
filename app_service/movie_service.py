#!/usr/bin/env python3
# -*- codeing:utf-8 -*-


import tornado.web
import json

import data_loader as MovieLoader


class EventHandler(tornado.web.RequestHandler):
    def get(self, params=None):
        raise tornado.web.HTTPError(405)


class HotMoviesEventHandler(EventHandler):
    def get(self, params=None):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(self.load_hot_movies()))

    def load_hot_movies(self):
        return MovieLoader.load_hot_movies()


class ComingSoonMoviesEventHandler(EventHandler):
    def get(self, param=None):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(self.load_coming_soon_movies()))

    def load_coming_soon_movies(self):
        return MovieLoader.load_coming_soon_movies()

