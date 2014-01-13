from webapp2_extras.routes import RedirectRoute
import apphandlers

secure_scheme = 'https'

_routes = [
    RedirectRoute('/', apphandlers.MainPage, name='MainPage', strict_slash=True),
#     RedirectRoute('/database', database.MainPage, name='database', strict_slash=True),
#     RedirectRoute('/settings', settings.MainPage, name='settings', strict_slash=True),
#     RedirectRoute('/stopwordlist', stoplist.MainPage, name='stopwordlist', strict_slash=True),
    RedirectRoute('/PersonActions', apphandlers.PersonActionsFull, name='PersonActions', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
