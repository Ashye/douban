#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''

__author__ = 'ych'
'''

import urllib.request



def fetch_html_by(url):
    req = urllib.request.urlopen(url)
    response = req.read().decode('utf-8')
    # print(response)
    return response
