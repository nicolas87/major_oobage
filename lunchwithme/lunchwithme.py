import urllib
import webapp2
import jinja2
import os
import datetime


from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# This part for the front page

class MainPage(webapp2.RequestHandler):
  """ Front page for those logged in """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 
      template = jinja_environment.get_template('home.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)
	  
class Persons(db.Model):
  """Models a person identified by email"""
  email = db.StringProperty()
  
class Freeslots(db.Model):
  """Models a freeslot with free_month, free_day, free_year, free_start_hour, free_start_min, free_end_hour and free_end_min."""
  free_month = db.StringProperty()
  free_day = db.StringProperty()
  free_year = db.StringProperty()
  free_start_hour = db.StringProperty()
  free_start_min = db.StringProperty()
  free_end_hour = db.StringProperty()
  free_end_min = db.StringProperty()
  

class AddFreeSlots(webapp2.RequestHandler):
  """ Add freeslots to the datastore """
  def post(self):
    # Retrieve person
    parent_key = db.Key.from_path('Persons', users.get_current_user().email())
    person = db.get(parent_key)
    if person == None:
      newPerson = Persons(key_name=users.get_current_user().email())
      newPerson.put()
	  
    freeslot = Freeslots(parent=parent_key)
    freeslot.free_month = self.request.get('month')
    freeslot.free_day = self.request.get('day')
    freeslot.free_year = self.request.get('year')
    freeslot.free_start_hour = self.request.get('start_hour')
    freeslot.free_start_min = self.request.get('start_min')
    freeslot.free_end_hour = self.request.get('end_hour')
    freeslot.free_end_min = self.request.get('end_min')
    self.redirect('/myfreeslots')
	
class MyFreeSlots(webapp2.RequestHandler):
  """ Form for getting and displaying wishlist items. """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already

      # Retrieve person
      parent_key = db.Key.from_path('Persons', users.get_current_user().email())

      query = db.GqlQuery("SELECT * "
                          "FROM Freeslots "
                          "WHERE ANCESTOR IS :1 "
                          "ORDER BY date DESC",
                          parent_key)

      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'freeslots': query,
        } 

      template = jinja_environment.get_template('myfreeslots.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class Friends(webapp2.RequestHandler):
  """ Display search page """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 
      template = jinja_environment.get_template('friends.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)
	  
class Display(webapp2.RequestHandler):
  """ Displays search result """
  def post(self):

    target = self.request.get('email').rstrip()
    # Retrieve person
    parent_key = db.Key.from_path('Persons', target)

    query = db.GqlQuery("SELECT * "
                        "FROM Freeslots "
                        "WHERE ANCESTOR IS :1 "
                        "ORDER BY date DESC",
                        parent_key)

    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_mail': target,
      'logout': users.create_logout_url(self.request.host_url),
      'items': query,
      } 
    template = jinja_environment.get_template('display.html')
    self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/lunchwithme', MainPage),
                               ('/friends', Friends),
                               ('/addfreeslots', AddFreeSlots),
                               ('/myfreeslots', MyFreeSlots),
                               ('/display', Display)],
                              debug=True)
