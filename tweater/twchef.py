# -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime

from pyquery import PyQuery

from .twfarmer import TwFarmer
from .tworder import TwOrder as order

_log_ = logging.getLogger()


class TwChef:


    @staticmethod
    def cookPage(page, session, isComment=False):
        """

        :param page:页面
        :param session: requests的session
        :param isComment:
        :return:
        """

        cursor = ''
        items = []
        # cnt_cp: Number of comments implies by this page
        # if this page is comment page, no 2-order comments will be retured
        # that means cnt_cp = 0
        cnt_cp = 0
        has_more = False

        if 'items_html' in page and len(page['items_html'].strip()) == 0:
            return cnt_cp, has_more, cursor, items
        has_more = page['has_more_items']
        if has_more is False and not isComment:
            time.sleep(4)
        cursor = page['min_position']
        tweets = PyQuery(page['items_html'])('div.js-stream-tweet')

        if len(tweets) == 0:
            return cnt_cp, has_more, cursor, items
        for tweetArea in tweets:
            tweet_pq = PyQuery(tweetArea)
            cnt_c, twe = TwChef.cookTweet(tweet_pq, session, isComment)
            items.append(twe)
            cnt_cp += cnt_c
        return cnt_cp, has_more, cursor, items

    @staticmethod
    def cookTweet(tweetq, session, isComment=False):
        """
        "" Read the document, and parse it with PyQuery
        """
        # Number of Comments needs to be pass back
        # Number of Tweets is 1, don't need to be pass back
        # Will return number of comments, and the tweet itself
        cnt_c = 0
        twe = {}
        twe["user"] = tweetq.attr("data-screen-name")
        twe["reference_source"] = tweetq('div.js-macaw-cards-iframe-container').attr('data-card-url')
        # print(f'引用：{twe["reference_source"]} ')

        # Process attributes of a tweet div
        twe["replies"] = int(tweetq("span.ProfileTweet-action--reply span.ProfileTweet-actionCount").attr(
            "data-tweet-stat-count").replace(",", ""))
        twe["retweets"] = int(tweetq("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr(
            "data-tweet-stat-count").replace(",", ""))
        twe["favorites"] = int(tweetq("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr(
            "data-tweet-stat-count").replace(",", ""))
        twe['timestamp'] = int(tweetq("small.time span.js-short-timestamp").attr("data-time"))
        twe["date"] = datetime.fromtimestamp(twe['timestamp']).strftime("%Y-%m-%d %H:%M")
        twe["id"] = tweetq.attr("data-tweet-id")
        twe["permalink"] = "https://twitter.com" + tweetq.attr("data-permalink-path")

        # Process text area of a tweet div
        textdiv = tweetq("p.js-tweet-text")

        # Process links in a tweet div, including url, hashtags, and mentions contained in the tweet
        links = textdiv('a')
        if len(links) > 0:
            hashtags = []
            mentions = []
            for link in links:
                textUrl = PyQuery(link).attr('data-expanded-url')
                textHashtag = PyQuery(link)('a.twitter-hashtag')('b')
                if len(textHashtag) > 0:
                    hashtags.append('#' + textHashtag.text())
                textMention = PyQuery(link)('a.twitter-atreply')('b')
                if len(textMention) > 0:
                    mentions.append('@' + PyQuery(textMention).text())
            twe['textUrl'] = ''
            if textUrl is not None:
                twe['textUrl'] = textUrl
            twe['hashtags'] = hashtags
            twe['mentions'] = mentions

        # Process Emojis in a tweet Div
        emojis = textdiv('img.Emoji--forText')
        emojilist = []
        if len(emojis) > 0:
            for emo in emojis:
                textEmoji = PyQuery(emo)
                if textEmoji is not None:
                    emoji = {}
                    emoji['face'] = textEmoji.attr('alt')
                    emoji['url'] = textEmoji.attr('src')
                    emoji['title'] = textEmoji.attr('title')
                    emojilist.append(emoji)
        twe['emojis'] = emojilist

        # Process Text in a tweet Div
        textq = textdiv.remove('a').remove('img')
        if textq is not None:
            twe["text"] = textq.text()

        # Process optional Geo area of a tweet
        twe["geo"] = ''
        geoArea = tweetq('span.Tweet-geo')
        if len(geoArea) > 0:
            twe["geo"] = geoArea.attr('title')

        # Process comments area if any
        if not isComment and twe['replies'] > 0:
            cn, twe['comments'] = TwChef.shopComments(twe['user'], twe['id'], twe['replies'], session)
            cnt_c = len(twe['comments'])

        # Finally return a json of a tweet
        return cnt_c, twe

    @staticmethod
    def shopComments(user_name, tweet_id, cnt_replies, session):
        if 'max_comments' in order.conf and order.conf['max_comments'] > 0:
            max_comments = order.conf['max_comments']
        else:
            max_comments = 0
        cnt_c = 0
        cursor = ''
        total = 0
        has_more = True
        comments = []
        lim = max_comments
        if cnt_replies < max_comments:
            lim = cnt_replies
        while has_more is True and total < lim:
            page = TwFarmer.ripCommentPage(user_name, tweet_id, cursor, session)
            if not page:
                continue
            cnt_cp, has_more, cursor, pageTweets = TwChef.cookPage(page, session, isComment=True)
            if len(pageTweets) == 0:
                _log_.info('Weird, no comments!')
                break
            comments.extend(pageTweets)
            total += len(pageTweets)
            cnt_c += cnt_cp
        # cnt_c should be 0
        return cnt_c, comments

    @staticmethod
    def get_rff(page):
        urls = list()
        if 'items_html' in page and len(page['items_html'].strip()) == 0:
            return urls
        has_more = page['items_html']
        if has_more is False:
            return urls
        for div in PyQuery(page['items_html'])('div.js-macaw-cards-iframe-container').items():
            urls.append(div.attr('data-card-url'))
        return urls