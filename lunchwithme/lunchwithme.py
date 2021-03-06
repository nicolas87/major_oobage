import urllib
import webapp2
import jinja2
import os
import datetime
import time

import logging

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
  #key is email
  email=db.StringProperty()
  name=db.StringProperty()
  description=db.StringProperty()
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
  name = db.StringProperty()

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
    
    myKey=db.Key.from_path('ProfileDB',users.get_current_user().email())
    profile=db.get(myKey)
    if not profile: #redirect person to profile page so that ProfileDB.name entry exists.
      self.redirect('/profile')
    else:
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
      freeslot.email = users.get_current_user().email()
      freeslot.name=profile.name
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
      #get present time
      today=datetime.datetime.now()
      today=today.replace(hour=0, minute=0,second=0,microsecond=0)
      logging.info(today)
      #delete all entries which are less than today's date
      for entity in Freeslots.all().filter("email =",users.get_current_user().email()).fetch(100):
        #logging.info(entity.free_date)
        if entity.free_date < today.date():
          entity.delete()
          #logging.info("removing date %s",entity.free_date)
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
    #delete his old dates
    #delete all entries which are less than today's date
    today_date=datetime.datetime.now()
    today_date=today_date.replace(hour=0,minute=0,second=0,microsecond=0)
    today_date=today_date.date()
    for entity in Freeslots.all().filter("email =",target).fetch(100):
      logging.info(entity.free_date)
      if entity.free_date < today_date:
        entity.delete()
        logging.info("removing date %s",entity.free_date)
    # Retrieve person
    parent_key = db.Key.from_path('Persons', target)

    query = db.GqlQuery("SELECT * "
                        "FROM Freeslots "
                        "WHERE ANCESTOR IS :1 ",
                        parent_key)

    img_url = '/img?img_id=' + target

    #get his name and description
    myKey=db.Key.from_path('ProfileDB',target)
    rec=db.get(myKey)
    target_name=rec.name
    target_description=rec.description


    template_values = {
      'target_name': target_name,
      'target_description': target_description,
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
    for querys in query:
      myKey=db.Key.from_path('ProfileDB',querys.email)
      rec=db.get(myKey)
      querys.name=rec.name

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
        myKey=db.Key.from_path('ProfileDB',img_id)
        rec=db.get(myKey)
        result = rec.data
        if result:
          self.response.headers['Content-Type'] = 'image/jpeg'
          self.response.out.write(result)
        else:
          self.redirect('/images/profile.png')
class Profile(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      #check if profile already created:
      db_key=db.Key.from_path('ProfileDB',users.get_current_user().email())
      profile=db.get(db_key)
      if not profile:
        profile=ProfileDB(key_name=users.get_current_user().email())
        profile.email=users.get_current_user().email()
        profile.name=profile.email
        profile.description="none"
        profile.put()
      if profile.description=="none":
        description="Enter your profile description..."
      else:
        description=profile.description
      if profile.name != profile.email:
        username=profile.name
      else:
        username="Enter your name..."
      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'user_name': username,
        'user_description' :description,
      }

      template = jinja_environment.get_template('profile.html')
      self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)
  def post(self):
      myKey=db.Key.from_path('ProfileDB',users.get_current_user().email())
      rec=db.get(myKey)
      img=self.request.get('picfile')
      rec.data=db.Blob(img)
      rec.put()
      self.redirect('/profile')

class saveProfile(webapp2.RequestHandler):
  def post(self):
    myKey=db.Key.from_path('ProfileDB',users.get_current_user().email())
    uname=self.request.get('name')
    description=self.request.get('description')
    if description:
      rec=db.get(myKey)
      rec.description=description
      rec.put()
    if uname:
      rec=db.get(myKey)
      rec.name=uname
      rec.put()
      #now we try to update name in freeslots:
      updated = []
      for entity in Freeslots.all().filter("email =", users.get_current_user().email()).fetch(100):
        entity.name = uname
        updated.append(entity)
      db.put(updated)
    self.redirect('/profile')
class displayDateProfile(webapp2.RequestHandler):
  def get(self):
    target_email=self.request.get('email')
    myKey=db.Key.from_path('ProfileDB',target_email)
    rec=db.get(myKey)
    template_values = {
      'user_mail': users.get_current_user().email(),
      'logout': users.create_logout_url(self.request.host_url),
      'target_name' : rec.name,
      'target_description' : rec.description,
      'target_email': target_email,

    }
    template = jinja_environment.get_template('displaydate_profile.html')
    self.response.out.write(template.render(template_values))



app = webapp2.WSGIApplication([('/lunchwithme', MainPage),
                               ('/friends', FriendsSearch),
                               ('/date', DateSearch),
                               ('/addfreeslots', AddFreeSlots),
                               ('/delfreeslots', DelFreeSlots),                
                               ('/myfreeslots', MyFreeSlots),
                               ('/displayfriend', DisplayFriends),
                               ('/displaydate', DisplayDate),
                               ('/img', Image),
                               ('/saveProfile', saveProfile),
                               ('/displaydateprofile', displayDateProfile),
                               ('/profile', Profile)],
                              debug=True)
