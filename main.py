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

consumer_key = "jjS66p3foM29k4Uq0XFpQ"
consumer_secret = "MdTJUsaHvyW3GA1ZEXDIMr2d69eQ0iO4eswjHua42k"
access_key = "362950164-WZgnbHgRRJdvHhCR0wS5aJcZ1oKZ8vc3M7RPQh2W"
access_secret = "gmziqQUWrJ6fOKKD6vC3whatx3QWz2oAgBdPhYYdLYc"

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
