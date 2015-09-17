#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import tornado.web
import tornado.httpclient
import json
import urllib.parse

from bs4 import BeautifulSoup

import app_service.data_loader as MovieLoader


contentTypeName = r'Content-Type'
contentTypeValue = r'application/json;charset=utf-8'


class EventHandler(tornado.web.RequestHandler):

    def get(self, params=None):
        raise tornado.web.HTTPError(405)

    def extract_data_from_html(self, response):
        return dict()

    def get_response_extra_data(self):
        return None

    def async_handler(self, response):
        data = self.extract_data_from_html(response)
        ret = dict()
        ret['result'] = "ok"
        ret['data'] = data
        extra_data = self.get_response_extra_data()
        if extra_data:
            ret["extra"] = extra_data
        self.write(ret)
        self.finish()

    def error_reply(self, message):
        data = dict()
        data["result"] = "error"
        data["data"] = message
        return data

    def set_default_content_type(self):
        self.set_header(contentTypeName, contentTypeValue)


class HotMoviesEventHandler(EventHandler):
    def get(self, params=None):
        self.set_default_content_type()
        self.write(json.dumps(self.load_hot_movies()))

    def load_hot_movies(self):
        return MovieLoader.load_hot_movies()


class ComingSoonMoviesEventHandler(EventHandler):
    def get(self, param=None):
        self.set_default_content_type()
        self.write(json.dumps(self.load_coming_soon_movies()))

    def load_coming_soon_movies(self):
        return MovieLoader.load_coming_soon_movies()


class SearchEventHandler(EventHandler):
    baseUrl = r'http://www.verycd.com'
    queryUrl = r'http://www.verycd.com/search/entries/'
    support_type = ['tv', 'movie']

    @tornado.web.asynchronous
    def get(self, params=None):
        query = self.get_query_argument("query", None)
        self.set_default_content_type()
        if query:
            async_client = tornado.httpclient.AsyncHTTPClient()
            async_client.fetch(self.queryUrl + query, self.async_handler)
        else:
            # self.write('{"result":"error", "reason":"no query keyword"}')
            self.write(self.error_reply("no query keyword"))
            self.finish()

    def extract_data_from_html(self, response):
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
                    item_url = self.get_url_from_host_and_page(self.baseUrl, name_col.a['href'])
                     #self.baseUrl + name_col.a['href']
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
                # print("not support type: \'", cat_type, "\'")
                pass
        return item_data

    def get_url_from_host_and_page(self, host, page):
        if host is None:
            return None
        elif page is None:
            return host
        elif host.endswith("/") and page.startswith("/"):
            return host + page[1:]
        else:
            return host + page


class MovieDetailEventHandler(EventHandler):
    task_cache = dict()

    @tornado.web.asynchronous
    def post(self):
        self.task_cache["url"] = self.get_body_argument("url", None)
        self.task_cache["type"] = self.get_body_argument("type", None)
        self.set_default_content_type()
        if self.task_cache["url"]:
            async_client = tornado.httpclient.AsyncHTTPClient()
            async_client.fetch(self.task_cache["url"], self.async_handler)
        else:
            # self.write('{"result":"error", "reason":"bad request"}')
            self.write(self.error_reply("bad request"))
            self.finish()

    def get_response_extra_data(self):
        return self.task_cache

    def extract_data_from_html(self, response):
        html = response.body.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        del html
        ret_data = dict()
        left_div = soup.find("div", class_="leftDiv")
        if left_div:
            del soup
            title_str = self.extract_title(left_div)
            ret_data["title"] = title_str

            info_data_div = left_div.find("div", class_="headinfo_left")
            if info_data_div:
                pic_li = info_data_div.find("li", class_="imgdiv")
                if pic_li:
                    updated_str = pic_li.div.div.get_text()
                    pic_url = pic_li.div.img["src"]
                    # print(updated_str, pic_url)
                    ret_data["cover"] = pic_url
                    ret_data["updated"] = updated_str

                del pic_li

                info_li = info_data_div.find("li", class_="infodiv")
                if info_li:
                    info_lis = info_li.ul.find_all("li")
                    for li_item in info_lis:
                        span_items = li_item.find_all("span")
                        for span in span_items:
                            info_item_text = span.get_text()
                            info_item = info_item_text.split("：")
                            if len(info_item) == 2:
                                ret_data[info_item[0]] = info_item[1]
                del info_li
                del info_lis
            del info_data_div

            watch_place_div = left_div.find_all("div", class_="entry_video_1")
            if watch_place_div:
                watch_platform = []
                for place in watch_place_div:
                    # print(place.name)
                    place_name = place.get("name")
                    if place_name == "playlist":
                        # print(place_name)
                        place_type = place.get("id")
                        place_type_parts = place_type.split("_")
                        if len(place_type_parts) == 2:
                            watch_platform.append(place_type_parts[1])
                ret_data["platform"] = watch_platform
            del watch_place_div

            comment_more = left_div.find("div", id="contents_more")
            if comment_more:
                # print(comment_more.name)
                comment_text = comment_more.div.get_text()
                ret_data["summary"] = comment_text
            del comment_more

            posters_div = left_div.find("ul", id="entry_image_div")
            if posters_div:
                # print(posters_div.name)
                poster_list = []
                posters_lis = posters_div.find_all("li")
                for poster_li in posters_lis:
                    poster_img = poster_li.find("img")
                    poster_url = poster_img.get("_src")
                    if poster_url is None:
                        poster_url = poster_img.get("src")
                    if poster_url:
                        poster_list.append(poster_url)
                ret_data["posters"] = poster_list
                del posters_lis
            del posters_div

        else:
            print("ssssssssssss")
        return ret_data

    def extract_title(self, div):
        title_div = div.find("div", class_="titleDiv")
        if title_div:
            # print(title_div.h1.get_text())
            title = title_div.h1.get_text()
            return title
        else:
            return None
