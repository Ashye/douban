#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''

__author__ = 'ych'
'''


from bs4 import BeautifulSoup
import http_fetcher
import tornado.web


hot_movies_url = 'http://movie.douban.com/nowplaying/shenzhen/'
coming_soon_movies_url = ''


def update_movie_library():
    update_hot_movies()
    update_coming_soon_movies()


def update_hot_movies():
    # update_movies_data_from(hot_movies_url)
    html = fetch_movies_html_page(hot_movies_url)
    hot_movies = extract_hot_movie_data(html)
    save_hot_movie_data(hot_movies)


def fetch_movies_html_page(url):
    print('fetch hot movie html page...')
    return http_fetcher.fetch_html_by(url)


def extract_hot_movie_data(html):
    # print(html)
    print('extract hot moves...')
    movie_data = parse_html_and_extract_hot_movies_data_with_bs4(html)
    return movie_data


def parse_html_and_extract_hot_movies_data_with_bs4(html):
    print('parse hot movies html page...')

    soup = BeautifulSoup(html, 'html.parser')
    # print(soup.name)
    now_playing_movies_html_items = extract_now_playing_movie_html_items(soup)
    hot_movies_data = extract_now_playing_movie_data(now_playing_movies_html_items)
    return hot_movies_data


def extract_now_playing_movie_html_items(document):
    now_playing_div = document.find('div', id='nowplaying')
    now_playing_ul_lis = now_playing_div.find_all('li', {'data-category':'nowplaying'})
    # print(len(now_playing_ul_lis))
    return now_playing_ul_lis


def extract_now_playing_movie_data(movie_html_items):
    data = []
    for item in movie_html_items:
        poster_html = item.find('li', class_='poster')
        image_html = poster_html.img
        movie_poster = dict(alt=image_html['alt'], url=image_html['src'])
        # print(movie_poster)
        title_html = item.find('li', class_='stitle')
        movie_title = title_html.a['title']
        # print(movie_title)
        rating_html = item.find('li', class_='srating')
        score_html = rating_html.find('span', class_='subject-rate')
        movie_rating = score_html.get_text()

        movie = dict(poster=movie_poster, title=movie_title, rating=movie_rating)
        # print(movie)
        data.append(movie)
    return data


def save_hot_movie_data(movies):
    print('save hot movie data...')


def update_coming_soon_movies():
    pass



if '__main__' == __name__:
    update_movie_library()