#!/usr/bin/env python3
# -*- codeing:utf-8 -*-
'''
__author__ = 'ych'
'''

import tornado.ioloop
import tornado.web


import movie.hot_movies


def make_app():
    application = tornado.web.Application([
        (r'/movies/hot', movie.hot_movies.HotMoviesEventHandler),
    ], debug=True)
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()


if '__main__' == __name__:
    make_app()