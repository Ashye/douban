#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import tornado.web
import tornado.httpclient
import json

from bs4 import BeautifulSoup

import app_service.data_loader as MovieLoader



contentTypeName = r'Content-Type'
contentTypeValue = r'application/json;charset=utf-8'

class EventHandler(tornado.web.RequestHandler):
    def get(self, params=None):
        raise tornado.web.HTTPError(405)


class HotMoviesEventHandler(EventHandler):
    def get(self, params=None):
        self.set_header(contentTypeName, contentTypeValue)
        self.write(json.dumps(self.load_hot_movies()))

    def load_hot_movies(self):
        return MovieLoader.load_hot_movies()


class ComingSoonMoviesEventHandler(EventHandler):
    def get(self, param=None):
        self.set_header(contentTypeName, contentTypeValue)
        self.write(json.dumps(self.load_coming_soon_movies()))

    def load_coming_soon_movies(self):
        return MovieLoader.load_coming_soon_movies()


class SearchEventHandler(EventHandler):
    baseUrl = r'http://www.verycd.com/'
    queryUrl = r'http://www.verycd.com/search/entries/'
    support_type = ['tv', 'movie']

    @tornado.web.asynchronous
    def get(self, params=None):
        query = self.get_query_argument("query", None)
        self.set_header(contentTypeName, contentTypeValue)
        if query:
            async_client = tornado.httpclient.AsyncHTTPClient()
            async_client.fetch(self.queryUrl + query, self.asyncHandler)
        else:
            self.write('{"result":"error", "reason":"no query keyword"}')
            self.finish()

    def asyncHandler(self, resonpse):
        data = self.extractSearchResultData(resonpse)
        ret = dict()
        ret['result'] = "ok"
        ret['data'] = data
        self.write(ret)
        self.finish()

    def extractSearchResultData(self, response):
        html = response.body.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        entry_list = soup.find("div", class_='entries_list')
        entry_items = entry_list.find_all('li', class_='entry_item')
        # print(len(entry_items))

        item_data = []
        for item in entry_items:
            title_div = item.find('div', class_='item_title')

            cat_col = title_div.find('span', class_='cat')
            cat_type = cat_col.a['href']

            data = None
            for type_support in self.support_type:
                if type_support in cat_type:
                    # cat_name = cat_col.a['title']
                    name_col = title_div.find('strong', class_='cname')
                    item_url = self.baseUrl + name_col.a['href']
                    item_name = name_col.a['title']

                    update_col = title_div.find('span', class_='update')
                    item_update = update_col.text.strip()
                    # print(item_update)

                    data = dict()
                    data['type'] = type_support
                    data['name'] = item_name
                    data['homeUrl'] = item_url
                    data['updated'] = item_update

                    content_div = item.find('div', class_='item_content')
                    cover_a = content_div.find('div', class_='entry_cover')
                    if cover_a:
                        cover_img = cover_a.find('img', class_='cover_img')
                        # print(cover_img)
                        cover_url = cover_img['_src']
                        if cover_url is None:
                            cover_url = cover_img['src']

                        if cover_url:
                            data['cover'] = cover_url

                    text_div = content_div.find('div', class_='text')
                    text_ps = text_div.find_all('p')
                    for text_p in text_ps:
                        text = text_p.text
                        if text:
                            if "演员" in text:
                                data['actor'] = text.strip()
                            elif "简介" in text:
                                data['description'] = text.strip()
                    break

            if data:
                item_data.append(data)
            else:
                print("not support type: \'", cat_type, "\'")

        return item_data
