import unittest
import os

import webapp2
import webtest
from google.appengine.ext import testbed

#from boilerplate.lib import utils
from test_tools import test_helpers
# setting HTTP_HOST in extra_environ parameter for TestApp is not enough for taskqueue stub
from test_tools import config, routes

from ebay_items import EbayItems


os.environ['HTTP_HOST'] = 'localhost'


class AppTest(unittest.TestCase, test_helpers.HandlerHelpers):
    def setUp(self):
        webapp2_config = config.config

        # create a WSGI application.
        self.app = webapp2.WSGIApplication(config=webapp2_config)
        routes.add_routes(self.app)
#        boilerplate_routes.add_routes(self.app)
        self.testapp = webtest.TestApp(self.app, extra_environ={'REMOTE_ADDR': '127.0.0.1'})

        # activate GAE stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_taskqueue_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.testbed.init_user_stub()

        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) Version/6.0 Safari/536.25',
                        'Accept-Language': 'en_US'}

        # fix configuration if this is still a raw boilerplate code - required by test with mails
        # if not utils.is_email_valid(self.app.config.get('contact_sender')):
        #     self.app.config['contact_sender'] = "noreply-testapp@example.com"
        # if not utils.is_email_valid(self.app.config.get('contact_recipient')):
        #     self.app.config['contact_recipient'] = "support-testapp@example.com"

    def tearDown(self):
        self.testbed.deactivate()

    def test_homepage(self):
        response = self.get('/')
        self.assertIn('JTABLE VERSION OF THE TABLE START', response)

#     def test_products_db_page(self):
#         response = self.get('/database')
#         self.assertIn('Product Database', response)

    def test_item_search(self):
        search_term = 'iphone'
        category = 'default'
        condition = None
        max_price = '1000'
        Zip = '27104'
        data = EbayItems.item_search(item_search=search_term,
                                     category=category,
                                     condition=condition,
                                     max_price=max_price,
                                     Zip=Zip)
        self.assertIn(search_term, str(data))



    # def test_jtable(self):
    #     value = {'action': 'list',
    #              'category': 'default',
    #              'jtStartIndex': '0',
    #              'jtPageSize': '20',
    #              'jtSorting': 'price%20ASC'}
    #     response = self.post('/PersonActions', value)
    #     self.assertIn('Current Bid', response)


        
if __name__ == "__main__":
    unittest.main()