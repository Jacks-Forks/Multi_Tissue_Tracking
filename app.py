import json
import logging
import os
import threading
from datetime import datetime

import tracking
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, url_for)
from flask_sqlalchemy import SQLAlchemy
from forms import upload_file_form
from werkzeug.utils import secure_filename

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.warning("New Run Starts Here")

current_directory = os.getcwd()

# change to where things should be stored
UPLOAD_FOLDER = current_directory + "/static/uploads"
VIDEO_UPLOAD_FOLDER = UPLOAD_FOLDER + "/videofiles"
CSV_UPLOAD_FOLDER = UPLOAD_FOLDER + "/csvfiles"

ALLOWED_EXTENSIONS = {'csv', 'mov', 'mp4'}
video_file_extentions = {'mov', 'mp4'}


def where_to_upload(filename):
    result = ""
    if filename.rsplit('.', 1)[1].lower() == 'csv':
        result = app.config['CSV_FOLDER']
    elif filename.rsplit('.', 1)[1].lower() in video_file_extentions:
        result = app.config['VIDEO_FOLDER']
    return result


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_UPLOAD_FOLDER
app.config['CSV_FOLDER'] = CSV_UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'development key'


class Uploaded_file(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_recorded = db.Column(db.Date, nullable=False)
    date_uploaded = db.Column(db.Date, nullable=False)
    num_tissues = db.Column(db.Integer)
    bio_reactor = db.Column(db.String(80))
    file_location = db.Column(db.String(120))

    def __repr__(self):
        return '<Uploaded_file %r>' % self.id


def check_system():
    if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
        logging.info("no uploads folder")
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if os.path.isdir(app.config['VIDEO_FOLDER']) is False:
        os.mkdir(app.config['VIDEO_FOLDER'])
    if os.path.isdir(app.config['CSV_FOLDER']) is False:
        os.mkdir(app.config['CSV_FOLDER'])


check_system()


@app.route("/")
def main():
    return render_template('home.html')
    # return redirect("/uploadFile")


@app.route("/boxCoordinates", methods=['GET', 'POST'])
def boxCoordinates():
    if request.method == "POST":
        from_js = request.get_data()
        logging.info(from_js)
        data = json.loads(from_js)
        logging.info(data)
        # tracking.start_trackign(data)
        tracking_thread = threading.Thread(
            target=tracking.start_trackig, args=(data,))
        tracking_thread.start()
        return jsonify({'status': 'OK', 'data': data})


@app.route('/uploadFile', methods=['GET', 'POST'])
def upload_file():
    form = upload_file_form()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            print("Somthing is wrong")
            return render_template('uploadFileWTF.html', form=form)
        else:
            where_to_save = where_to_upload(form.file.data.filename)
            logging.info('Where does it save: ' + where_to_save)
            filename = secure_filename(form.file.data.filename)
            form.file.data.save(os.path.join(where_to_save, filename))
            logging.info("After saved")
            new_upload = Uploaded_file(date_recorded=form.date_recorded.data, date_uploaded=datetime.now(
            ), num_tissues=form.num_tissues.data, bio_reactor=form.bio_reactor.data, file_location=where_to_save)
            db.session.add(new_upload)
            db.session.commit()
            logging.info(Uploaded_file.query.all())
            return '''
            <!DOCTYPE html >
            <h1 > uploaded </h1 >
            '''
    elif request.method == 'GET':
        return render_template('uploadFileWTF.html', form=form)
