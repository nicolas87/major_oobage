import urllib
import webapp2
import jinja2
import os
import datetime


from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template #added this! to remove?

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
  
class Date(db.Model):
  """Models date entered by user"""
  search_month = db.StringProperty()
  search_day = db.StringProperty()
  search_year = db.StringProperty()
  
class Freeslots(db.Model):
  """Models a freeslot with free_month, free_day, free_year, free_start_hour, free_start_min, free_end_hour, free_end_min and free_venue."""
  free_month = db.StringProperty()
  free_day = db.StringProperty()
  free_year = db.StringProperty()
  free_start_hour = db.StringProperty()
  free_start_min = db.StringProperty()
  free_end_hour = db.StringProperty()
  free_end_min = db.StringProperty()
  free_venue = db.StringProperty()
  select = db.StringProperty()
  username = db.StringProperty()
  
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
    freeslot.free_venue = self.request.get('venue')
    freeslot.select = self.request.get('select')
    freeslot.username = users.get_current_user().email()
    freeslot.put()
    self.redirect('/myfreeslots')	

class DelFreeSlots(webapp2.RequestHandler):
  """ Del freeslots to the datastore """
  def get(self):	
	# Delete freeslots
    #parent_key = db.Key.from_path('Persons', users.get_current_user().email())
    #delete_freeslots = db.GqlQuery("SELECT * "
    #                              "FROM Freeslots "
    #                             "WHERE freeslot.select='YES'",
    #							   parent_key
    #                             ) 
    #result = delete_freeslots.fetch(10)
    #db.delete(result)
    user = users.get_current_user()
    if user:
     parent_key = db.Key.from_path('Persons', users.get_current_user().email())
     data_id=self.request.get('delid')
     query=Freeslots.get_by_id(int(data_id),parent_key)
     query.delete()
     #template_values = {
     #    'user_mail': users.get_current_user().email(),
     #    'logout': users.create_logout_url(self.request.host_url),
     #    'freeslots': query,
     #} 
     #commented out below. is it necessary?		
     #template = jinja_environment.get_template('myfreeslots.html')
     #self.response.out.write(template.render(template_values))	
     self.redirect('/myfreeslots')
     self.redirect('/myfreeslots')
    else:
     self.redirect(self.request.host_url)
	
class MyFreeSlots(webapp2.RequestHandler):
  """ Form for getting and displaying wishlist items. """
  def get(self):
    user = users.get_current_user()
    if user:  # signed in already

      # Retrieve person
     # parent_key = db.Key.from_path('Persons', users.get_current_user().email())

      query = Freeslots.gql(
                          "WHERE username = :userN ORDER BY free_month DESC",
					      userN=users.get_current_user().email())
						 

      template_values = {
        'user_mail': users.get_current_user().email(),
        'logout': users.create_logout_url(self.request.host_url),
        'freeslots': query,
		
        } 
      self.response.out.write(template.render('templates/myfreeslots.html', template_values))
      #template = jinja_environment.get_template('myfreeslots.html')
      #self.response.out.write(template.render(template_values))
    else:
      self.redirect(self.request.host_url)

class Friends(webapp2.RequestHandler):
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

class Date(webapp2.RequestHandler):
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
                        "WHERE ANCESTOR IS :1 "
                        "ORDER BY date DESC",
                        parent_key)

    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_mail': target,
      'logout': users.create_logout_url(self.request.host_url),
      'freeslots': query,
      } 
    template = jinja_environment.get_template('displayfriend.html')
    self.response.out.write(template.render(template_values))

class DisplayDate(webapp2.RequestHandler):
  """ Displays search date result """
  def post(self):

    target = self.request.get('date').rstrip()
    # Retrieve people with common free date
    parent_key = db.Key.from_path('Date', target)

    query = db.GqlQuery("SELECT * "
                        "FROM Freeslots "
                        "WHERE ANCESTOR IS :1 "
                        "ORDER BY date DESC",
                        parent_key)

    template_values = {
      'user_mail': users.get_current_user().email(),
      'target_date': target,
      'logout': users.create_logout_url(self.request.host_url),
      'freeslots': query,
      } 
    template = jinja_environment.get_template('displaydate.html')
    self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/lunchwithme', MainPage),
                               ('/friends', Friends),
                               ('/date', Date),
                               ('/addfreeslots', AddFreeSlots),
                               ('/delfreeslots', DelFreeSlots),							   
                               ('/myfreeslots', MyFreeSlots),
                               ('/displayfriend', DisplayFriends),
                               ('/displaydate', DisplayDate)],
                              debug=True)
