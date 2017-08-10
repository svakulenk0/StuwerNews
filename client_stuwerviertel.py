# -*- coding: utf-8 -*-
'''
10 Aug 2017
svakulenko

Simple Twitter stream filter
'''
from tweepy.streaming import StreamListener
from tweepy import Stream, API, OAuthHandler

from settings import *

# set up Twitter connection
auth_handler = OAuthHandler(APP_KEY, APP_SECRET)
auth_handler.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter_client = API(auth_handler)


class TopicListener(StreamListener):
    '''
    Overrides Tweepy class for Twitter Streaming API
    '''

    def on_status(self, status):
        # ignore retweets
        if not hasattr(status,'retweeted_status') and status.in_reply_to_status_id == None:
            print(status.text)
            # retweet
            twitter_client.retweet(id=status.id)

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
            stream.filter(track=['stuwerviertel'])
        except Exception as e:
            # reconnect on exceptions
            print (e)
            continue


if __name__ == '__main__':
    stream_tweets()
