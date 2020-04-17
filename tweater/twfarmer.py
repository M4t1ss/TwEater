# -*- coding: utf-8 -*-
import logging

import requests

from .tworder import TwOrder as order

_log_ = logging.getLogger()


class TwFarmer:
    @staticmethod
    def ripStatusPage(cursor, sess):
        """

        :param cursor: 附加到 max_position 后的字符串
        :param sess: requests session
        :return:
        """
        url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&l=en&max_position=%s"

        parUrl = ''
        if 'user' not in order.conf and 'query' not in order.conf:
            raise ValueError("User and Query, at least one of them must be specified.")
        else:
            if 'query' in order.conf and len(order.conf['query'].strip()) > 0:
                parUrl += " " + order.conf['query']
            if 'user' in order.conf and len(order.conf['user'].strip()) > 0:
                parUrl += ' from:' + order.conf['user']
            if 'until' in order.conf and len(order.conf['until'].strip()) > 0:
                parUrl += ' until:' + order.conf['until']
            if 'since' in order.conf and len(order.conf['since'].strip()) > 0:
                parUrl += ' since:' + order.conf['since']
            if 'near' in order.conf and len(order.conf['near'].strip()) > 0:
                if 'within' in order.conf and len(order.conf['within'].strip()) > 0:
                    parUrl += " near:\"" + order.conf['near'] + "\" within:" + order.conf['within']
        url = url % (parUrl, cursor)

        _log_.debug(f'爬取url => {url}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
            'Accept-Language': "en-US,en;q=0.8",
            'X-Requested-With': "XMLHttpRequest"
        }
        try:
            r = sess.get(url, headers=headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            _log_.error(f'url: {url}')
            _log_.error(e)

    @staticmethod
    def ripCommentPage(user_name, tweet_id, cursor, sess):
        url = "https://twitter.com/i/%s/conversation/%s?include_available_features=1&include_entities=1&max_position=%s&reset_error_state=false"
        url = url % (user_name, tweet_id, cursor)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
            'Accept-Language': "en-US,en;q=0.8",
            'X-Requested-With': "XMLHttpRequest"
        }
        try:
            r = sess.get(url, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return {"errors": "403"}
        except requests.exceptions.RequestException as e:
            _log_.error(f'url: {url}')
            _log_.error(e)
