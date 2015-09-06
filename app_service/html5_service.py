#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import tornado.web
import tornado.httpclient
# import json


class Html5AppHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        signature = self.get_query_argument('signature', None)
        timestamp = self.get_query_argument('timestamp', None)
        nonce = self.get_query_argument('nonce', None)
        echostr = self.get_query_argument('echostr', None)
        self.write(echostr)

    def post(self, *args, **kwargs):
        pass