#!/usr/bin/env python3
# -*- codeing:utf-8 -*-
'''
__author__ = 'ych'
'''

import tornado.ioloop
import tornado.web

import app_service.movie_service as Movie


def make_app():
    application = tornado.web.Application([
        (r'/movies/hot', Movie.HotMoviesEventHandler),
        (r'/movies/coming', Movie.ComingSoonMoviesEventHandler)
    ], debug=True)
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()


if '__main__' == __name__:
    make_app()