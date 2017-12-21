# -*- coding: utf-8 -*-
'''
10 Aug 2017
svakulenko

Simple Twitter stream filter
'''
from tweepy.streaming import StreamListener
from tweepy import Stream, API, OAuthHandler

from elasticsearch import Elasticsearch

from settings import *
from all_settings import *

# set up Twitter connection
auth_handler = OAuthHandler(APP_KEY, APP_SECRET)
auth_handler.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter_client = API(auth_handler)

# set up ES connection
es = Elasticsearch()


def search_duplicate_tweets(query, threshold=13, index=INDEX):
    results = es.search(index=index, body={"query": {"match": {"tweet": query}}}, doc_type='tweets')['hits']
    if results['max_score']:
        if results['max_score'] > threshold:
            return results['hits'][0]
    return None


def store_tweet(topic_id, tweet_text, index=INDEX):
    es.index(index=index, doc_type='tweets', id=topic_id,
             body={'tweet': tweet_text})


class TopicListener(StreamListener):
    '''
    Overrides Tweepy class for Twitter Streaming API
    '''

    def on_status(self, status):
        # ignore retweets
        if not hasattr(status,'retweeted_status') and status.in_reply_to_status_id == None:
            tweet_text = status.text
            # check duplicates
            # duplicates = search_duplicate_tweets(tweet_text)
            # if not duplicates:
            tweet_id = status.id
            print(tweet_text)
            # retweet
            twitter_client.retweet(id=tweet_id)
                # store tweets that have been reported to ES
                # store_tweet(tweet_id, tweet_text)

    def on_error(self, status_code):
        print (status_code, 'error code')


def stream_tweets():
    '''
    Connect to Twitter API and fetch relevant tweets from the stream
    '''
    listener = TopicListener()

    # start streaming
    while True:
        try:
            stream = Stream(auth_handler, listener)
            print ('Listening...')
            print [SEED] + KEYWORDS
            stream.filter(track=[SEED]+KEYWORDS)
        except Exception as e:
            # reconnect on exceptions
            print (e)
            continue


if __name__ == '__main__':
    stream_tweets()
