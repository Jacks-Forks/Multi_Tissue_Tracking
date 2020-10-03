import logging
import os

import models
from dotenv import load_dotenv
from flask import Flask
from models import db
from routes import csrf, routes_for_flask

logging.basicConfig(filename='app.log',
                    format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.warning("New Run Starts Here")

current_directory = os.getcwd()
ALLOWED_EXTENSIONS = {'csv', 'mov', 'mp4'}
video_file_extentions = {'mov', 'mp4'}


def create_app():
    load_dotenv('.env')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    location = os.getenv('DB_LOCATION')
    dbname = os.getenv('DB_NAME')
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = models.UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{location}:3306/{dbname}?charset=utf8mb4"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Shows sql querys being made if having database issue set to true
    app.config['SQLALCHEMY_ECHO'] = False
    #  REVIEW:  this needs to be changed
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.secret_key = os.getenv('SECRET_KEY')
    app.register_blueprint(routes_for_flask)
    db.init_app(app)
    csrf.init_app(app)

    return app


# REVIEW: is having this here correct
app = create_app()
app.app_context().push()
db.create_all()
models.populate()


def check_system():
    models.check_path_exisits(app.config['UPLOAD_FOLDER'])
    models.check_path_exisits(models.IMG_FOLDER)


check_system()
