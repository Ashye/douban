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
    support_type = ['tv', 'movie']

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
#区分电影影视搜索解析
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
                    name_col = title_div.find('strong', class_='cname')
                    item_url = self.get_url_from_host_and_page(self.baseUrl, name_col.a['href'])
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
    filter_mask = ["在看", "看过", "想看", "观看预告片", "别名", "IMDb号"]
    formal_property_name = {"类型":"category", "地区":"area", "导演":"director", "编剧":"writer", "演员":"actor", "上映日期":"releasedDate", "首播时间":"releasedDate", "集数":"episodes","电视台":"TVStation"}


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
        html = response.body.decode("utf-8")
        page_type = self.task_cache["type"]
        ret_data = None
        if self.support_type[0] == page_type:
            ret_data = self.extract_tv_detail_data_from_html(html)
        elif self.support_type[1] == page_type:
            ret_data = self.extract_movie_detail_data_from_html(html)
        if ret_data:
            ret_data = self.filter_out_useless_item(ret_data)
        return ret_data

    def extract_movie_detail_data_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # extract title
        title_div = soup.find("div", class_="titleDiv")
        detail_data = dict()
        if title_div:
            detail_data["name"] = title_div.h1.get_text()
        del title_div
        # cover
        cover_li = soup.find("li", class_="imgdiv")
        if cover_li:
            detail_data["cover"] = self.extract_image_src_data(cover_li.div.img)
        del cover_li
        # little property
        info_li = soup.find("li", class_="infodiv")
        if info_li:
            item_spans = info_li.find_all("span")
            for item_span in item_spans:
                item_span_text = item_span.get_text()
                if item_span_text:
                    item_span_text_parts = item_span_text.split("：")
                    property_formal_name = item_span_text_parts[0].strip()
                    if len(item_span_text_parts) == 1:
                        item_span_text_parts.append("")
                    if property_formal_name in self.formal_property_name:
                        property_formal_name = self.formal_property_name[property_formal_name]
                    detail_data[property_formal_name] = item_span_text_parts[1]
            del item_spans
            del item_span
            actor = detail_data["actor"]
            indx = actor.find("更多»")
            if indx != -1:
                detail_data["actor"] = actor[0:indx]
        del info_li
        # summary
        content_more_div = soup.find("div", id="contents_more")
        if content_more_div:
            detail_data["summary"] = content_more_div.get_text()
        del content_more_div
        # picture
        poster_ul = soup.find("ul", id="entry_image_div")
        if poster_ul:
            poster_lis = poster_ul.find_all("li")
            poster_data = []
            for poster_li in poster_lis:
                poster_img = poster_li.find("img")
                if poster_img:
                    poster_data.append(self.extract_image_src_data(poster_img))
            del poster_lis
            del poster_img
            del poster_li
            detail_data["poster"] = poster_data
        del poster_ul
        return detail_data

    def extract_tv_detail_data_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # extract title
        title_div = soup.find("div", class_="titleDiv")
        detail_data = dict()
        if title_div:
            detail_data["name"] = title_div.h1.get_text()
        del title_div
        # cover
        cover_li = soup.find("li", class_="imgdiv")
        if cover_li:
            detail_data["cover"] = self.extract_image_src_data(cover_li.div.img)
        del cover_li
        # little property
        info_li = soup.find("li", class_="infodiv")
        if info_li:
            item_spans = info_li.find_all("span")
            for item_span in item_spans:
                item_span_text = item_span.get_text()
                if item_span_text:
                    item_span_text_parts = item_span_text.split("：")
                    property_formal_name = item_span_text_parts[0].strip()
                    if len(item_span_text_parts) == 1:
                        item_span_text_parts.append("")
                    if property_formal_name in self.formal_property_name:
                        property_formal_name = self.formal_property_name[property_formal_name]
                    detail_data[property_formal_name] = item_span_text_parts[1]
            del item_spans
            del item_span
            actor = detail_data["actor"]
            indx = actor.find("更多»")
            if indx != -1:
                detail_data["actor"] = actor[0:indx]
        del info_li
        # updated
        watch_place_div = soup.find_all("div", class_="entry_video_1")
        if watch_place_div:
            watch_platform = []
            for place in watch_place_div:
                if place.get("name") == "playlist":
                    place_type = place.get("id")
                    indx = place_type.find("_")
                    if indx != -1:
                        play_place_name = place_type[indx+1:]
                        item_lis = place.find_all("li")
                        tmp = dict()
                        tmp[play_place_name] = len(item_lis)
                        watch_platform.append(tmp)
                    else:
                        continue
            detail_data["platform"] = watch_platform
            del place
            del item_lis
        del watch_place_div
        # summary
        content_more_div = soup.find("div", id="contents_more")
        if content_more_div:
            detail_data["summary"] = content_more_div.get_text()
        del content_more_div
        # picture
        poster_ul = soup.find("ul", id="entry_image_div")
        if poster_ul:
            poster_lis = poster_ul.find_all("li")
            poster_data = []
            for poster_li in poster_lis:
                poster_img = poster_li.find("img")
                if poster_img:
                    poster_data.append(self.extract_image_src_data(poster_img))
            del poster_lis
            del poster_img
            del poster_li
            detail_data["poster"] = poster_data
        del poster_ul
        return detail_data

    @staticmethod
    def extract_image_src_data(img):
        src_data = img.get("_src")
        if src_data is None:
            src_data = img.get("src")
        return src_data

    def filter_out_useless_item(self, data):
        for key in self.filter_mask:
            if key in data:
                del data[key]
        return data
