from werkzeug.middleware.dispatcher import DispatcherMiddleware


from app import app as flask_app
from dashboard import dasher as dashapp

application = DispatcherMiddleware(flask_app, {
    '/dash': dashapp.server,
})
