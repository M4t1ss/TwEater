import json, sys, os
from tweater import TwEater, TwOrder, TwChef
import requests

#This script gets full texts for tweets that may have been saved as trimmed 

if __name__ == "__main__":
    
    inFile = open('qr.json','r')
    outFile = open("full-qr.json","w")
    
    basic_path = os.path.split(os.path.realpath(__file__))[0]
    TwOrder.order(f'{basic_path}/order.conf')
    sess = requests.Session()
    
    for wi in inFile:
        text = ' '.join(wi.strip()[:-1].split()).replace('}, ]','} ]')
        
        try:
            tweet_dict = json.loads(text)
        except json.decoder.JSONDecodeError as e:
            sys.stderr.write(wi.strip()[:-1])
            sys.exit(e.message)
            
        if "… h" in tweet_dict["q_tweet_text"]:
            #This tweet may be trimmed
            full_text = TwChef.getTweet(tweet_dict["q_tweet_id"], sess)
            tweet_dict["q_tweet_text"] = full_text.replace("\n@\n\n"," @").replace("\n#\n\n"," #").replace("#\n","#").replace("@\n","@").replace("\n#"," #").replace("\n@"," @")
            
        output = json.dumps(tweet_dict, sort_keys=True, ensure_ascii=False)
        outFile.write(output.strip() + "\n")
        
    outFile.close();
    inFile.close();