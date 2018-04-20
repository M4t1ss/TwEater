#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'luo_dao_yi'
__date__ = '2018/3/30 14:39'
import pymysql
from sqlalchemy import Column, String, Integer, create_engine, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ref_page_anas import ana

pymysql.install_as_MySQLdb()
# 创建对象的基类:
BaseModel = declarative_base()


class TwitterMessage(BaseModel):
    __tablename__ = 'twitter_message_ref'
    id = Column(String(30), primary_key=True)
    user = Column(String(100))
    replies = Column(Integer)
    retweets = Column(Integer)
    favorites = Column(Integer)
    timestamp = Column(Integer)
    permalink = Column(String(500))
    textUrl = Column(String(500))
    text = Column(String(4096))
    text_transfer = Column(String(4096))
    reference_source = Column(TEXT())
    reference_text = Column(TEXT())


# 初始化数据库连接:
engine = create_engine("mysql+pymysql://root:root@127.0.0.1:3306/twitter_data?charset=utf8mb4", max_overflow=5)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


def init_db():
    BaseModel.metadata.create_all(engine)


def drop_db():
    BaseModel.metadata.drop_all(engine)


def get_twitter_message(tweet):
    message = TwitterMessage()
    if 'id' in tweet:
        message.id = tweet['id']
    else:
        return None
    if 'text' in tweet:
        message.text = tweet['text']
    else:
        return None

    if 'user' in tweet:
        message.user = tweet['user']
    if 'replies' in tweet:
        message.replies = tweet['replies']
    if 'retweets' in tweet:
        message.retweets = tweet['retweets']
    if 'favorites' in tweet:
        message.favorites = tweet['favorites']
    if 'timestamp' in tweet:
        message.timestamp = tweet['timestamp']
    if 'permalink' in tweet:
        message.permalink = tweet['permalink']
    if 'textUrl' in tweet:
        message.textUrl = tweet['textUrl']
    if 'reference_source' in tweet:
        # url = tweet["reference_source"]
        url = tweet["textUrl"]
        if url:
            source, text = ana(url)
            message.reference_source = source
            message.reference_text = text

    return message
