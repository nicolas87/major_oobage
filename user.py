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
import urllib
import webapp2
import jinja2
import os
import datetime


from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment( loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class LoggedIn(webapp2.RequestHandler):
    def get(self):
		user=users.get_current_user()
		if user:
			template_values= {
				'user_mail': users.get_current_user().email(),
				'logout': users.create_logout_url(self.request.host_url)
			}
			template=jinja_environment.get_template('front_user.html')
			self.response.out.write(template.render(template_values))
		else:
			self.redirect(self.request.host_url)





app = webapp2.WSGIApplication([
    ('/logged_in', LoggedIn)
], debug=True)
