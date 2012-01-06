#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import tweepy
import ConfigParser

CONFIG_FILE = 'param.config'
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

consumer_key    = config.get('env','consumer_key')
consumer_secret = config.get('env','consumer_secret')
access_key      = config.get('env','access_key')
access_secret   = config.get('env','access_secret')

class MainHandler(webapp.RequestHandler):
    def get(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth_handler=auth)

        list_tl = api.list_timeline(owner='meganii',slug='lifehacks')
        for tweets in list_tl:
            self.response.out.write(tweets.text)

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
