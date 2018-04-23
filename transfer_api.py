#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'luo_dao_yi'
__date__ = '2018/3/30 15:47'

import logging

import requests

from sql_db import DBSession, TwitterMessage

end_point = '******'
_log_ = logging.getLogger()

session = requests.session()


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


def get_transfer(tweets):
    _log_.info(f'获取翻译 {len(tweets)} 条')
    source_text = [x['text'] for x in tweets]
    post_data = \
        {
            "qs": source_text,
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
    db_session = DBSession()
    for t in range(len(source_text)):
        id_value = tweets[t]['id']
        transfer_text_value = transfer_text[t]
        _log_.debug(id_value)
        _log_.debug(tweets[t]['text'])
        _log_.debug(transfer_text_value)
        _log_.info('-' * 100)
        db_session.query(TwitterMessage).filter_by(id=id_value).update(dict(text_transfer=transfer_text_value, ))
    db_session.commit()
    db_session.close()
