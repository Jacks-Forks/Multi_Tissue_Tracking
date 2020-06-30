from analysisFolder.dashboard import dasher as dashapp
from app import app as flask_app
from dashSelect import app as vidSelect
from models import db
from werkzeug.middleware.dispatcher import DispatcherMiddleware

db.create_all()

application = DispatcherMiddleware(flask_app, {
    '/dash': dashapp.server,
    '/vidSelect': vidSelect.server,
})
