import json
import logging
import os
import threading
import time
from datetime import datetime
import requests

from sql_db import DBSession, get_twitter_message, init_db
from transfer_api import get_transfer
from tweater import TwEater, TwOrder, TwChef

# from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)

_log_ = logging.getLogger()


# Write tweets batch to a file in folder dir
def digest_2_file(tweets, dir):
    base_path = os.getcwd()
    fn_dir = os.path.join(base_path, dir)
    if not os.path.exists(fn_dir):
        os.mkdir(fn_dir)
    fn = os.path.join(fn_dir, f'{int(round(time.time() * 1000))}.json')
    _log_.info(' ------ Saved to file: ' + fn + ' ------')
    with open(fn, 'w') as f:
        json.dump(tweets, f)


# Write file to MongoDB collection
def digest_2_mongo(tweets, col):
    """
    :param tweets: data
    :param col: col_name
    :return:
    """
    _log_.info(' ------ Save to MongoDB ------')
    col.insert_many(tweets)


def save_to_mysql(tweets):
    session = DBSession()
    transfer_list = list()
    for tweet in tweets:
        model = get_twitter_message(tweet)
        if model:
            session.merge(model)
            session.commit()
            transfer_list.append({'text': model.text, 'id': model.id})
    session.close()
    _log_.info(f'保存推文 {len(tweets)} 条')
    while threading.active_count() > 100:
        pass
    t = threading.Thread(target=get_transfer, args=(transfer_list,))
    t.start()


if __name__ == "__main__":
    _log_.info("\n " + str(datetime.now()))
    # Initialize the parameters

    basic_path = os.path.split(os.path.realpath(__file__))[0]
    _log_.info(basic_path)
    TwOrder.order(f'{basic_path}/order.conf')
    # to.TwOrder.order(user='BarackObama')

    # Write tweets to json file
    # TwEater.eatTweets(digest_2_file, 'test')

    # Collect replies of specific tweet_id of a user, username is case-sensitive
    # print tc.TwChef.shopComments('BarackObama', '876456804305252353')
    sess = requests.Session()
    
    # answers = TwChef.shopComments('Oljenjka', '426766378549657600', 20, sess)
    answers = TwChef.getTweet('781401543560065024', sess)
    # answers = TwChef.shopComments('Sigita133', '1227663389834596352', 20, sess)
    print ()
    print (answers)
    print ()
    # print (type(answers))

    # print (answers[1])



    # Write tweets to Mongo Collection
    # connection = MongoClient('localhost', 27017)
    # tdb = connection.tweets

    # save with mysql
    # init_db()

    # with open(f'{basic_path}/twitter_user.txt', 'r') as f:
        # for line in f:
            # name = line.split('/')[-1]
            # if not name:
                # continue
            # name = name.strip()
            # TwOrder.conf['user'] = name
            # TwEater.eatTweets(save_to_mysql)
            # _log_.info(name.strip())
    _log_.info(f" {str(datetime.now())}")
    _log_.info(" Done!")
