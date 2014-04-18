import os
import json
import urllib
import logging
from google.appengine.api import users
import webapp2
import jinja2
import models

# *** for production
FRONTEND_DIR = 'dist'
FRONTEND_INDEX_FILE = 'index.html'
# *** for local development
# FRONTEND_DIR = 'app'
# FRONTEND_INDEX_FILE = 'index.html'
# *** for old non-yeoman version
# FRONTEND_DIR = 'templates'
# FRONTEND_INDEX_FILE = 'app.html'


JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=True, extensions=['jinja2.ext.autoescape'],
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), FRONTEND_DIR)))

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        is_current_user_admin = users.is_current_user_admin()
        logging.info(user)
        logging.info(is_current_user_admin)
        logging.info("referer: " + str(self.request.referer))
        
        template_values = {
                           'keyword': self.request.get("keyword"),
                           'condition': self.request.get("condition"),
                           'user': user,
                           'is_current_user_admin': is_current_user_admin,
                           'logout_url':  users.create_logout_url('/'),
                           'login_url': users.create_login_url('/'),
        }
        path = FRONTEND_INDEX_FILE
        template = JINJA_ENVIRONMENT.get_template(path)
        self.response.write(template.render(template_values))


class PersonActions(webapp2.RequestHandler):
    def get(self):
        try:
            keyword = urllib.unquote(self.request.get("keyword", ""))
            category = urllib.unquote(self.request.get("category", ""))
            condition = urllib.unquote(self.request.get("condition", ""))
            start_index = int(self.request.get("StartIndex", "0"))
            page_size = int(self.request.get("PageSize", "0"))
            sorting = self.request.get("Sorting")
            sorting_type = None
            sorting_field = None
            if sorting:
                sorting_type = sorting.split()[1]
                sorting_field = sorting.split()[0]
            logging.info("sorting=" + str(sorting) + 
                         "; sorting_type=" + str(sorting_type) + 
                         "; sorting_field=" + str(sorting_field))
            if sorting_field == 'price':
                sorting_field = 'percent'
            if sorting_type == "ASC":
                order_type = -(getattr(models.Item, sorting_field)) #-Item.percent 
            elif sorting_type == "DESC":
                order_type = getattr(models.Item, sorting_field) #Item.percent
            else:
                order_type =  None
            [data_items,count] = models.Item.get_items(StartIndex=start_index,
                                                          PageSize=page_size,
                                                          category=category,
                                                          search_term=keyword,
                                                          condition=condition,
                                                          order_type=order_type)
            terms = models.Filter.get_all_filters()
            template_values = {
                'Records': data_items,
                'TotalRecordCount': str(count),
                'Result': 'OK',
                'Terms': terms
            }
        except Exception as e:
            logging.info(e)
            template_values = {
                'Records': [],
                'TotalRecordCount': '0',
                'Result': 'ERROR',
                'Terms': []
            }
        self.response.write(json.dumps(template_values))

    def post(self):
        try:
            models.Item.delete_item(self.request.get("itemID"))
            template_values = {
                'Result': 'OK'
            }
        except Exception as e:
            logging.debug(e)
            template_values = {
                'Result': 'ERROR'
            }
        self.response.write(json.dumps(template_values))


class Update(webapp2.RequestHandler):
    def get(self):
        try:
            models.Item.update_items()
            logging.info('updated')
        except Exception as e:
            logging.debug(str(e))
        self.redirect('/')


class CreateFilters(webapp2.RequestHandler):
    def get(self):
        try:
            models.Filter(category='auto',
                          condition='New',
                          max_price='50000',
                          search_term='mercedes'
                          ).put()
            models.Filter(category='auto',
                          condition='New',
                          max_price='50000',
                          search_term='audi'
                          ).put()
            models.Filter(category='phones',
                          condition='New',
                          max_price='5000',
                          search_term='iphone'
                          ).put()
            logging.info('created')
        except Exception as e:
            logging.debug(str(e))
        self.redirect('/')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/PersonActions', PersonActions),
                               ('/update', Update),
                               ('/createfilters', CreateFilters)], debug=True)

