import unittest
import os

import webapp2
import webtest
from google.appengine.ext import testbed
import ConfigParser

#from boilerplate.lib import utils
from test_tools import test_helpers
# setting HTTP_HOST in extra_environ parameter for TestApp is not enough for taskqueue stub
from test_tools import config, routes

from ebay_items import EbayItems
from settings import InstallRecord

os.environ['HTTP_HOST'] = 'localhost'
EBAY_API_SETTINGS_FILE = "ebay_api_credentials.ini"

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
        self.testbed.init_modules_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.testbed.init_user_stub()

        cfg = ConfigParser.ConfigParser(allow_no_value=True)
        cfg.read(EBAY_API_SETTINGS_FILE)

        InstallRecord(DeveloperKey=cfg.get("keys", "dev_name") or "",
                      ApplicationKey=cfg.get("keys", "app_name") or "",
                      CertificateKey=cfg.get("keys", "cert_name") or "",
                      Token=cfg.get("auth", "token") or "",
                      Zip=cfg.get("settings", "zip") or "").put()

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
        self.assertIn('eBay Items', response)

    def test_item_search(self):
        search_term = 'iphone'
        category = 'default'
        condition = 'Used'
        max_price = '1000'
        Zip = '27104'
        data = EbayItems.search_items(search_term=search_term,
                                     category=category,
                                     condition=condition,
                                     max_price=max_price,
                                     Zip=Zip)
        self.assertIn(search_term, str(data))

        
if __name__ == "__main__":
    unittest.main()
