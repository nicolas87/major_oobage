import urllib
import webapp2
import jinja2
import os
import datetime
import time

from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.api import users
from datetime import date 

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
  # # data = db.BlobProperty()
  # image_thumbnail = db.BlobProperty()

class ProfileDB(db.Model):
  data=db.BlobProperty() #stores image data

class Freeslots(db.Model):
  """Models a freeslot with free_month, free_day, free_year, free_start_hour, free_start_min, free_end_hour, free_end_min and free_venue."""
  free_day = db.IntegerProperty()
  free_month = db.IntegerProperty()
  free_year = db.IntegerProperty()
  free_start_hour = db.StringProperty()
  free_start_min = db.StringProperty()
  free_end_hour = db.StringProperty()
  free_end_min = db.StringProperty()
  free_venue = db.StringProperty()
  free_date = db.DateProperty()
  free_datep = db.StringProperty()
  email = db.StringProperty()

class SearchDate(db.Model):
  """Models a date input with search_day, search_month, search_year, search_date and search_datep"""
  search_day = db.IntegerProperty()
  search_month = db.IntegerProperty()
  search_year = db.IntegerProperty()
  search_date = db.DateProperty()
  search_datep = db.StringProperty()

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
    freeslot.free_day = int(self.request.get('day'))
    freeslot.free_month = int(self.request.get('month'))
    freeslot.free_year = int(self.request.get('year'))
    freeslot.free_start_hour = self.request.get('start_hour')
    freeslot.free_start_min = self.request.get('start_min')
    freeslot.free_end_hour = self.request.get('end_hour')
    freeslot.free_end_min = self.request.get('end_min')
    freeslot.free_venue = self.request.get('venue')
    freeslot.free_date = datetime.date(freeslot.free_year, freeslot.free_month, freeslot.free_day)
    freeslot.free_datep = date(freeslot.free_year, freeslot.free_month, freeslot.free_day).isoformat()
    freeslot.email = person.key().name()
    freeslot.put()
    self.redirect('/myfreeslots')	

class DelFreeSlots(webapp2.RequestHandler):
  """ Del freeslots to the datastore """
  def get(self):  
    user = users.get_current_user()
    if user:
     parent_key = db.Key.from_path('Persons', users.get_current_user().email())
     data_id=self.request.get('delid')
     query=Freeslots.get_by_id(int(data_id),parent_key)
     query.delete()
     self.redirect('/myfreeslots')
    else:
     self.redirect(self.request.host_url)
	
class MyFreeSlots(webapp2.RequestHandler):
  """ Form for getting and displaying wishlist items. """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already

      # Retrieve person
      parent_key = db.Key.from_path('Persons', users.get_current_user().email())

      query = db.GqlQuery("SELECT * "
                          "FROM Freeslots "
                          "WHERE ANCESTOR IS :1 ",
                          parent_key
						 )

      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'freeslots': query,
        } 

      template = jinja_environment.get_template('myfreeslots.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class FriendsSearch(webapp2.RequestHandler):
  """ Display search friends page """
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

class DateSearch(webapp2.RequestHandler):
  """ Display search date page """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        } 
      template = jinja_environment.get_template('date.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)
	  
class DisplayFriends(webapp2.RequestHandler):
  """ Displays search friends result """
  def post(self):

    target = self.request.get('email').rstrip()
    # Retrieve person
    parent_key = db.Key.from_path('Persons', target)

    query = db.GqlQuery("SELECT * "
                        "FROM Freeslots "
                        "WHERE ANCESTOR IS :1 ",
                        parent_key)

    img_url = '/img?img_id=' + target
    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_mail': target,
      'logout': users.create_logout_url(self.request.host_url),
      'freeslots': query,
      'profile_img': img_url
      } 
    template = jinja_environment.get_template('displayfriend.html')
    self.response.out.write(template.render(template_values))

class DisplayDate(webapp2.RequestHandler):
  """ Displays search date result """
  def post(self):

    search_day = int(self.request.get('day'))
    search_month = int(self.request.get('month'))
    search_year = int(self.request.get('year'))
    search_date = datetime.date(search_year, search_month, search_day)
    search_datep = date(search_year, search_month, search_day).isoformat()
    
    # Retrieve people with common free date
    #parent_key = db.Key.from_path('Freeslots', target)

    query = db.GqlQuery("SELECT * "
                        "FROM Freeslots "
                        "WHERE free_datep = :1",
                        search_datep
                        )

    #query = db.GqlQuery("SELECT * "
    #                    "FROM Persons "
    #                    "WHERE person.free_datep = :1 ",
    #                   target)
  
    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_date': search_datep,
      'freeslots': query,
      'logout': users.create_logout_url(self.request.host_url),
      } 
    template = jinja_environment.get_template('displaydate.html')
    self.response.out.write(template.render(template_values))
class Image(webapp2.RequestHandler):
    """ serves image """
    def get(self):
        
        img_id=self.request.get('img_id')
        parent_key=db.Key.from_path('Persons', img_id)
        
        query = ProfileDB.gql("WHERE ANCESTOR IS :1",parent_key)
        result = query.get()
       

        if result:
          self.response.headers['Content-Type'] = 'image/jpeg'
          self.response.out.write(result.data)
        else:
          self.redirect('/images/profile.png')
class Profile(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
      } 
      template = jinja_environment.get_template('profile.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)
  def post(self):
      parent_key = db.Key.from_path('Persons', users.get_current_user().email())
      person = db.get(parent_key)
      if person == None:
        newPerson = Persons(key_name=users.get_current_user().email())
        newPerson.put()
    
      iDB = ProfileDB(parent=parent_key)
      img = self.request.get('picfile')
      iDB.data=db.Blob(img)
      iDB.put()
      self.redirect('/profile')

app = webapp2.WSGIApplication([('/lunchwithme', MainPage),
                               ('/friends', FriendsSearch),
                               ('/date', DateSearch),
                               ('/addfreeslots', AddFreeSlots),
                               ('/delfreeslots', DelFreeSlots),							   
                               ('/myfreeslots', MyFreeSlots),
                               ('/displayfriend', DisplayFriends),
                               ('/displaydate', DisplayDate),
                               ('/img', Image),
                               ('/profile', Profile)],
                              debug=True)
