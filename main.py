#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import re
import tweepy
import ConfigParser

CONFIG_FILE = 'config.ini'
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

consumer_key    = config.get('env','consumer_key')
consumer_secret = config.get('env','consumer_secret')
access_key      = config.get('env','access_key')
access_secret   = config.get('env','access_secret')

class Tweet(db.Model):
    id =  db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    content = db.StringProperty(multiline=True)
    url = db.StringProperty(multiline=True)

class MainHandler(webapp.RequestHandler):
    def get(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth_handler=auth)

        for tweets in tweepy.Cursor(api.list_timeline,owner='meganii',slug='lifehacks').items(100):
            result = db.GqlQuery("SELECT * FROM Tweet WHERE id=:1", tweets.id)
            if result.get() == None:
                self.response.out.write("none")         
                m = re.search("(http://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)", tweets.text)
                if m:
                    tweet = Tweet()
                    tweet.id = tweets.id
                    tweet.content = tweets.text
                    tweet.save()
                    self.response.out.write(tweets.text)
            else:
                self.response.out.write(tweets.id)
                self.response.out.write("\n")



class Show(webapp.RequestHandler):
    def get(self):
        self.response.out.write('show')
        tweets = db.GqlQuery("SELECT * FROM Tweet ORDER BY date")
        self.response.out.write(tweets)
        for tweet in tweets:
            self.response.out.write(tweet.content)

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/show',Show)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
