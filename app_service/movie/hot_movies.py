#!/usr/bin/env python3
# -*- codeing:utf-8 -*-


import tornado.web
import json

import data_loader as movie_loader



class HotMoviesEventHandler(tornado.web.RequestHandler):
    def get(self, params=None):
        self.write(json.dumps(self.load_hot_movies(), ensure_ascii=False))
        # self.write('</br>'+str(params))


    def load_hot_movies(self):
        return movie_loader.load_hot_movies()

