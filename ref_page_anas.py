#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'luo_dao_yi'
__date__ = '2018/4/19 15:35'

import logging

import requests

from CxExtractor import CxExtractor

end_point = '***************'
_log_ = logging.getLogger()

session = requests.session()
cx = CxExtractor(threshold=186)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
    'Accept-Language': "en-US,en;q=0.8",
    'X-Requested-With': "XMLHttpRequest"
}


def get_data(json_data, retries=3):
    while retries > 0:
        try:
            with session.post(end_point, json=json_data, timeout=600) as resp:
                json_data = resp.json()
                return json_data['data']['translation']
        except Exception as e:
            _log_.error(e)
            retries -= 1


def get_content_transfer(source_text):
    post_data = \
        {
            "qs": [source_text],
            "source": "en",
            "target": "zh",
            "domain": "technology"  # ,
            # "no_cache": 1
        }
    result_json = get_data(post_data)
    for r in range(3):
        _log_.info('-' * 100)
    values = set(map(lambda x: x['paragraph'], result_json))
    order_list = [[y['translated_text'] for y in result_json if y['paragraph'] == x] for x in values]
    transfer_text = [''.join(x) for x in order_list]
    return transfer_text[-1]


def get_page(url, retries=3):
    while retries > 0:
        try:
            with requests.get(url, allow_redirects=True, timeout=600, headers=headers) as resp:
                return resp.text
        except Exception as e:
            _log_.error(e)
            retries -= 1
    return None


def ana(url):
    test_html = get_page(url)
    if not test_html or test_html.strip() == '':
        return None, None

    test_html = test_html.replace('div > div.group > p:first-child">', '')
    content = cx.filter_tags(test_html)
    s = cx.getText(content)
    if not s or s.strip() == '':
        return None, None
    _log_.debug(f'引用页面：\n {"*" * 100} \n {s} \n{"*" * 100} \n')
    text = get_content_transfer(s)
    _log_.debug(f'引用机翻：\n {"*" * 100} \n {text} \n{"*" * 100} \n')
    return s, text
