import json
import logging
import os
import threading
from datetime import datetime

import cv2
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, url_for)
from forms import PickVid, upload_to_a_form, upload_to_b_form
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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #  REVIEW: : this needs to be changed
    app.secret_key = 'development key'
    app.register_blueprint(routes_for_flask)
    db.init_app(app)
    return app


# TODO: put create in wsgi anf then import to both app.py and tracking and app.push???
app = create_app()
app.app_context().push()


def check_system():
    if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
        logging.info("no uploads folder")
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if os.path.isdir(current_directory + '/static/img') is False:
        os.mkdir(current_directory + '/static/img')


check_system()
