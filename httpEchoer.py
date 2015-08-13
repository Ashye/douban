#!/usr/bin/env python3
# -*- codeing:utf-8 -*-
'''
__author__ = 'ych'
'''

import tornado.ioloop
import tornado.web


class HttpEchoer(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        response_data = dict()
        response_data["method"] = "POST"
        response_data["header"] = self.request.headers
        response_data["post_data"] = str(self.request.body, encoding="utf-8")
        self.write(response_data)

    def get(self, *args, **kwargs):
        response_data = dict()
        response_data["method"] = "GET"
        response_data["header"] = self.request.headers
        response_data["parameters"] = self.get_parameters()
        self.write(response_data)

    def get_parameters(self):
        param = dict()
        args = self.request.arguments
        for a in args:
            param[a] = self.get_argument(a)
        return param


def make_app():
    application = tornado.web.Application([
        (r'/echo', HttpEchoer)
    ], debug=True)
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()


if '__main__' == __name__:
    make_app()
