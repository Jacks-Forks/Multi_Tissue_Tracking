import logging
import os

from flask import Flask
from models import db
from routes import routes_for_flask

logging.basicConfig(filename='app.log',
                    format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.warning("New Run Starts Here")

current_directory = os.getcwd()


UPLOAD_FOLDER = current_directory + "/static/uploads"
ALLOWED_EXTENSIONS = {'csv', 'mov', 'mp4'}
video_file_extentions = {'mov', 'mp4'}


def create_app():
    # TODO: move to wsgi??
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #  REVIEW: : where do we wanna save this and name it
    '''
    to connect to my sql droplet not had to create a new user with legacy pass word support as ssl doent seem to be supported
    mysql+pymysql://testUser:xlcr7ds7oy08c0qr@db-mysql-nyc1-39521-do-user-7668124-0.a.db.ondigitalocean.com:25060/defaultdb

    '''
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://newuser:newpassword@localhost:3306/test_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    #  REVIEW: : this needs to be changed
    app.secret_key = 'development key'
    app.register_blueprint(routes_for_flask)
    db.init_app(app)

    return app


#  REVIEW: is having this here correct
app = create_app()
app.app_context().push()
db.create_all()


def check_system():
    if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
        logging.info("no uploads folder")
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if os.path.isdir(current_directory + '/static/img') is False:
        os.mkdir(current_directory + '/static/img')


check_system()
