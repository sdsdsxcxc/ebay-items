config = {

# webapp2 sessions
'webapp2_extras.sessions' : {'secret_key': '_PUT_KEY_HERE_YOUR_SECRET_KEY_'},

# webapp2 authentication
'webapp2_extras.auth' : {'user_model': 'models.User',
                         'cookie_name': 'session_name'},

# jinja2 templates
'webapp2_extras.jinja2' : {'template_path': ['/templates',"/"],
                           'environment_args': {'extensions': ['jinja2.ext.i18n']}},

# application name
'app_name' : "auction-items",

# the default language code for the application.
# should match whatever language the site uses when i18n is disabled
'app_lang' : 'en',

# Enable Federated login (OpenID and OAuth)
# Google App Engine Settings must be set to Authentication Options: Federated Login
'enable_federated_login' : True,

# jinja2 base layout template
'base_layout' : 'app.html',
}
