from webapp2_extras.routes import RedirectRoute
import apphandlers

secure_scheme = 'https'

_routes = [
    RedirectRoute('/', apphandlers.MainPage, name='MainPage', strict_slash=True),
    RedirectRoute('/PersonActions', apphandlers.PersonActions, name='PersonActions', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
