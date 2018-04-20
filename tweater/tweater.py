# -*- coding: utf-8 -*-
import logging

import requests

from .twchef import TwChef
from .twfarmer import TwFarmer
from .tworder import TwOrder as order

_log_ = logging.getLogger()


class TwEater:
    @staticmethod
    def eatTweets(digester):
        """
        :param digester: 保存回调方法
        :param bpargs: 保存回调参数
        :return:
        """
        # Set default values of parameters.
        max_tweets = 1
        bufferlength = 100
        if 'max_tweets' in order.conf and order.conf['max_tweets'] > 0:
            max_tweets = order.conf['max_tweets']
        if 'bufferlength' in order.conf and order.conf['bufferlength'] > 0:
            bufferlength = order.conf['bufferlength']
        total = 0
        bufferTotal = 0
        bufferall = 0

        cursor = ''
        buffer_tweets = []
        sess = requests.Session()
        cnt_blank = 0
        while total < max_tweets:
            page = TwFarmer.ripStatusPage(cursor, sess)
            if not page:
                continue
            cnt_c, has_more, cursor, page_tweets = TwChef.cookPage(page, isComment=False, session=sess)

            if len(page_tweets) == 0:
                cnt_blank += 1
            if len(page_tweets) > 0:
                cnt_blank = 0
            if cnt_blank > 3:
                _log_.info('Too many blank pages, terminating this search.')
                break
            total += len(page_tweets)
            buffer_tweets.extend(page_tweets)

            bufferTotal += cnt_c + len(page_tweets)
            if bufferTotal >= bufferlength:
                bufferall += bufferTotal
                digester(buffer_tweets)
                _log_.info(
                    f'Total tweets:{str(total)}, this time tweets: {str(len(buffer_tweets))}.\n Total items: {str(bufferall)},this time items: {str(bufferTotal) }。\n')
                buffer_tweets = []
                bufferTotal = 0
        if bufferTotal > 0:
            bufferall += bufferTotal
            digester(buffer_tweets)
            _log_.info(
                f'Total tweets: {str(total)}, this time tweets: {str(len(buffer_tweets))}.\n Total items: {str(bufferall)} , this time items:{str(bufferTotal)} .\n')
            buffer_tweets = []
            buffer_tweets = []
            bufferTotal = 0
        return total
