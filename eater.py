import json
import os
import time
from pymongo import MongoClient
from datetime import datetime
import logging;logging.basicConfig(level=logging.DEBUG)
from tweater import TwEater, TwOrder


# Write tweets batch to a file in folder dir
def digest_2_file(tweets, dir):
    base_path = os.getcwd()
    fn_dir = os.path.join(base_path, dir)
    if not os.path.exists(fn_dir):
        os.mkdir(fn_dir)
    fn = os.path.join(fn_dir, f'{int(round(time.time() * 1000))}.json')
    print(' ------ Saved to file: ' + fn + ' ------')
    with open(fn, 'w') as f:
        json.dump(tweets, f)


# Write file to MongoDB collection
def digest_2_mongo(tweets, col):
    """
    :param tweets: data
    :param col: col_name
    :return:
    """
    print(' ------ Save to MongoDB ------')
    col.insert_many(tweets)


if __name__ == "__main__":
    print("\n " + str(datetime.now()))
    # Initialize the parameters

    basic_path = os.path.split(os.path.realpath(__file__))[0]
    print(basic_path)
    TwOrder.order(f'{basic_path}/order.conf')
    # to.TwOrder.order(user='BarackObama')

    # Write tweets to json file
    # TwEater.eatTweets(digest_2_file, 'test')

    # Collect replies of specific tweet_id of a user, username is case-sensitive
    # print tc.TwChef.shopComments('BarackObama', '876456804305252353')

    # Write tweets to Mongo Collection
    connection = MongoClient('localhost', 27017)
    tdb = connection.tweets
    with open(f'{basic_path}/twitter_user.txt', 'r') as f:
        for line in f:
            name = line.split('/')[-1]
            if not name:
                continue
            name = name.strip()
            TwOrder.conf['user'] = name
            TwEater.eatTweets(digest_2_mongo, tdb.test)
            print(name.strip())
    print(f" {str(datetime.now())}")
    print(" Done!")
