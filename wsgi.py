from werkzeug.middleware.dispatcher import DispatcherMiddleware


from app import app as flask_app
from analysisFolder.dashboard import dasher as dashapp
from dashSelect import app as vidSelect

application = DispatcherMiddleware(flask_app, {
    '/dash': dashapp.server,
    '/vidSelect': vidSelect.server,
})
