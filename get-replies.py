import json,sys
import logging
import os
import threading
import time
from datetime import datetime
import requests

from transfer_api import get_transfer
from tweater import TwEater, TwOrder, TwChef


logging.basicConfig(level=logging.DEBUG)

_log_ = logging.getLogger()


if __name__ == "__main__":
    _log_.info("\n " + str(datetime.now()))
    # Initialize the parameters

    basic_path = os.path.split(os.path.realpath(__file__))[0]
    _log_.info(basic_path)
    TwOrder.order(f'{basic_path}/order.conf')
    sess = requests.Session()
    
    inFile = open('questions.json','r')
    outFile = open("questions-replies-1.json","w")
    
    outFile.write("[\n")
    
    for wi in inFile:
        
        try:
            tweet_dict = json.loads(' '.join(wi.strip()[:-1].split()))
        except json.decoder.JSONDecodeError as e:
            sys.stderr.write(wi.strip()[:-1])
            sys.exit(e.message)
            
            
        q_tweet_id = str(tweet_dict["tweet_id"])
        q_screen_name = tweet_dict["screen_name"]
        q_tweet_text = tweet_dict["tweet_text"].replace('\n', ' ').replace('\\', '\\\\').replace('"', '\\"')
           
        answers = False
        
        answers = TwChef.shopComments(q_screen_name, q_tweet_id, 20, sess)
                
        if answers != False and len(answers[1]) > 0:
            outFile.write("\t{ \"q_tweet_id\": " + q_tweet_id +  ", \"q_screen_name\": \"" + q_screen_name + "\", \"q_tweet_text\": \"" + q_tweet_text + "\", \"answers\": [")
                    
            answer_list = answers[1]
            for answer in answer_list:
                a_tweet_id = str(answer['id'])
                a_screen_name = answer['user']
                a_tweet_text = answer['text'].replace('\n', ' ').replace('\\', '\\\\').replace('"', '\\"')
                outFile.write("{ \"a_tweet_id\": " + a_tweet_id +  ", \"a_screen_name\": \"" + a_screen_name + "\", \"a_tweet_text\": \"" + a_tweet_text + "\" }, ")
            
            outFile.write("]},\n")    

    _log_.info(f" {str(datetime.now())}")
    _log_.info(" Done!")
