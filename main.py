#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from django.utils import feedgenerator
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

OWNER = 'meganii'
SLUG  = 'lifehacks'

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

        result = db.GqlQuery("SELECT * FROM Tweet ORDER BY date DESC")
        s_id = None
        for i, r in enumerate(result):
            if i == 0:
                s_id = r.id

        cursor = None
        if s_id != None:
            cursor = tweepy.Cursor(api.list_timeline,owner=OWNER,slug=SLUG,since_id=s_id).items(100)
        else:
            cursor = tweepy.Cursor(api.list_timeline,owner=OWNER,slug=SLUG).items(100)

        for tweets in cursor:
            result = db.GqlQuery("SELECT * FROM Tweet WHERE id=:1", tweets.id)
            if result.get() == None:
                self.response.out.write("none data")
                m = re.search("(http://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)", tweets.text)
                if m:
                    tweet = Tweet()
                    tweet.id = tweets.id
                    tweet.url = m.group(1)
                    tweet.content = tweets.text
                    tweet.save()
                    self.response.out.write(tweets.text)
                else:
                    self.response.out.write("nothing url")
                    self.response.out.write(tweets.id)
                    self.response.out.write("\n")

class Show(webapp.RequestHandler):
    def get(self):
        self.response.out.write('show')
        tweets = db.GqlQuery("SELECT * FROM Tweet ORDER BY date")
        self.response.out.write(tweets)
        for tweet in tweets:
            self.response.out.write(tweet.content)

class Rss(webapp.RequestHandler):
    def get(self):
        # フィード作成
        feed = feedgenerator.Rss201rev2Feed(
            title = "extweet",
            link = "RSSのURL",
            description = "RSSの説明",
            language = u"ja")

        tweets = db.GqlQuery("SELECT * FROM Tweet ORDER BY date")
        for tweet in tweets:
            feed.add_item(
                title = tweet.content,
                link = tweet.url,
                description = tweet.content)
    
        # RSS 文字列にする
        rss = feed.writeString("utf-8")
        self.response.headers['Content-Type']='text/xml; charset=utf-8'
        self.response.out.write(rss)

class Delete(webapp.RequestHandler):
    def get(self):
        q = Tweet.all(keys_only=True)
        results = q.fetch(q.count())
        db.delete(results)

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/show',Show),
                                          ('/rss',Rss),
                                          ('/delete',Delete)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
