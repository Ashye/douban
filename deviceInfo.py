#!/usr/bin/env python3
# -*- codeing:utf-8 -*-
'''
__author__ = 'ych'
'''


import tornado.ioloop
import tornado.web


class DeviceInfo(tornado.web.RequestHandler):


    def get(self, *args, **kwargs):
        pass



def make_app():
    application = tornado.web.Application([
        (r'/ip', DeviceInfo)
    ], debug=True)
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()


if '__main__' == __name__:
    make_app()