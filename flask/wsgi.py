from analysisFolder.dashboard import dasher as dashapp
from app import app as flask_app
from models import db
from werkzeug.middleware.dispatcher import DispatcherMiddleware

application = DispatcherMiddleware(flask_app, {

    '/dash': dashapp.server,

})
