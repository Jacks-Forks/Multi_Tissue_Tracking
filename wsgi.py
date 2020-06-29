from analysisFolder.dashboard import dasher as dashapp
from app import app as flask_app
from app import db
from dashSelect import app as vidSelect
from werkzeug.middleware.dispatcher import DispatcherMiddleware

db.create_all()

application = DispatcherMiddleware(flask_app, {
    '/dash': dashapp.server,
    '/vidSelect': vidSelect.server,
})
