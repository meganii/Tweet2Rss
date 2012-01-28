#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import feedgenerator
import os
import re
import urllib2
import tweepy
import ConfigParser

CONFIG_FILE = 'config.ini'
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

consumer_key    = config.get('env','consumer_key')
consumer_secret = config.get('env','consumer_secret')
access_key      = config.get('env','access_key')
access_secret   = config.get('env','access_secret')

OWNER = 'meganii'
SLUG  = 'lifehacks'

class Tweet(db.Model):
    id =  db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    content = db.StringProperty(multiline=True)
    urls = db.StringListProperty()

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("index")

class Get(webapp.RequestHandler):
    def get(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth_handler=auth)

        result = db.GqlQuery("SELECT * FROM Tweet ORDER BY id DESC")
        lasttweet = result.get() # get 1 object

        if lasttweet != None:
            cursor = tweepy.Cursor(api.list_timeline,owner=OWNER,slug=SLUG,since_id=lasttweet.id,include_entities='true').items(100)
        else:
            cursor = tweepy.Cursor(api.list_timeline,owner=OWNER,slug=SLUG,include_entities='true').items(100)

        for tweets in cursor:
            tweeturls = []
            for e in tweets.entities['urls']:
                tweeturls.append(e['expanded_url'])

            if len(tweeturls) > 0:
                if lasttweet != None:
                    if tweets.id > lasttweet.id:
                        tweet = Tweet()
                        tweet.id = tweets.id
                        tweet.urls = tweeturls
                        tweet.content = tweets.text
                        tweet.save()
                        self.response.out.write(tweets.text)
                else:
                    tweet = Tweet()
                    tweet.id = tweets.id
                    tweet.urls = tweeturls
                    tweet.content = tweets.text
                    tweet.save()
                    self.response.out.write(tweets.text)

class Show(webapp.RequestHandler):
    def get(self):
        self.response.out.write('show')
        tweets = db.GqlQuery("SELECT * FROM Tweet ORDER BY date")
        self.response.out.write(tweets)
        for tweet in tweets:
            self.response.out.write(tweet.urls)

class Rss(webapp.RequestHandler):
    def get(self):
        # フィード作成
        feed = feedgenerator.Rss201rev2Feed(
            title = "extweet",
            link = "RSSのURL",
            description = "RSSの説明",
            language = u"ja")

        tweets = db.GqlQuery("SELECT * FROM Tweet ORDER BY date DESC")
        for tweet in tweets:
            feed.add_item(
                title = tweet.content,
                link = tweet.urls[0],
                description = tweet.content,
                pubdate = tweet.date)
    
        # RSS 文字列にする
        rss = feed.writeString("utf-8")
        self.response.headers['Content-Type']='text/xml; charset=utf-8'
        self.response.out.write(rss)

class Delete(webapp.RequestHandler):
    def get(self):
        q = db.GqlQuery("SELECT * FROM Tweet ORDER BY date DESC")
        res = q.fetch(1)
        db.delete(q.fetch(q.count()))
        db.put(res)

class DeleteAll(webapp.RequestHandler):
    def get(self):
        q = Tweet.all()
        db.delete(q.fetch(q.count()))

class Expand(webapp.RequestHandler):
    def get(self):
        q = db.GqlQuery("SELECT * FROM Tweet ORDER BY date DESC")
        res = q.fetch(10)
        for t in res:
            for u in t.urls:
                url = urllib2.urlopen(u).geturl()
                self.response.out.write(url)
                self.response.out.write("\n")

class Meganii(webapp.RequestHandler):
    def get(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth_handler=auth)

        cursor = tweepy.Cursor(api.home_timeline,include_entities='true').items(100)


        tweetlist = []
        for tweets in cursor:
            tweeturls = []
            for e in tweets.entities['urls']:
                tweeturls << e['expanded_url']

            if len(tweeturls) > 0:
                tweet = Tweet()
                tweet.urls = tweeturls
                tweet.content = tweets.text
                tweetlist.append(tweet)

        template_values = {
            'tweetlist': tweetlist,
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class Meganiicom(webapp.RequestHandler):
    def get(self):
        u = 'http://meganii.com'
        url = urllib2.urlopen(u).geturl()
        self.response.out.write(url)

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/get',Get),
                                          ('/show',Show),
                                          ('/rss',Rss),
                                          ('/delete',Delete),
                                          ('/deleteall',DeleteAll),
                                          ('/expand',Expand),
                                          ('/meganii',Meganii),
                                          ('/meganiicom', Meganiicom)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
