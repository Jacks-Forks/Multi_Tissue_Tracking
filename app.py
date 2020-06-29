import json
import logging
import os
import threading
from datetime import datetime

import models
import tracking
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, url_for)
#from flask_sqlalchemy import SQLAlchemy
from forms import upload_to_a_form, upload_to_b_form
from models import db
#from models import Bio_reactor_B_sample, db
from werkzeug.utils import secure_filename

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.warning("New Run Starts Here")

current_directory = os.getcwd()

# TODO: change to where things should be stored
UPLOAD_FOLDER = current_directory + "/static/uploads"
VIDEO_UPLOAD_FOLDER = UPLOAD_FOLDER + "/videofiles"
CSV_UPLOAD_FOLDER = UPLOAD_FOLDER + "/csvfiles"

ALLOWED_EXTENSIONS = {'csv', 'mov', 'mp4'}
video_file_extentions = {'mov', 'mp4'}


def where_to_upload(filename, date_recorded):
    result = ""
    date_string = date_recorded.strftime('%m_%d_%Y')
    logging.info(date_string)
    if filename.rsplit('.', 1)[1].lower() == 'csv':
        result = os.path.join(app.config['CSV_FOLDER'], date_string)
    elif filename.rsplit('.', 1)[1].lower() in video_file_extentions:
        result = os.path.join(app.config['VIDEO_FOLDER'], date_string)
    if os.path.isdir(result) is False:
        logging.info("no date folder")
        os.mkdir(result)
    return result


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(form):
    where_to_save = where_to_upload(
        form.file.data.filename, form.date_recorded.data)
    filename = secure_filename(form.file.data.filename)
    form.file.data.save(os.path.join(where_to_save, filename))
    return where_to_save


def get_post_info(wtforms_list):
    count = 0
    li = []
    for entry in wtforms_list:
        if entry.data['post_in_use'] is True:
            count = count + 1
            li.append(
                entry.data['tissue_num'] + "," + entry.data['type_of_tissue'])
        else:
            li.append("empty")
    return (count, li)


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['VIDEO_FOLDER'] = VIDEO_UPLOAD_FOLDER
    app.config['CSV_FOLDER'] = CSV_UPLOAD_FOLDER
    # TODO: where do we wanna save this and name it
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # TODO: this needs to be changed
    app.secret_key = 'development key'
    db.init_app(app)
    return app


app = create_app()
app.app_context().push()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])


"""
  TODO: would idelly like to have these classes in separe file
  having problem with circulare import
"""


def check_system():
    if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
        logging.info("no uploads folder")
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if os.path.isdir(app.config['VIDEO_FOLDER']) is False:
        os.mkdir(app.config['VIDEO_FOLDER'])
    if os.path.isdir(app.config['CSV_FOLDER']) is False:
        os.mkdir(app.config['CSV_FOLDER'])


check_system()


@ app.route("/")
def main():
    logging.info(Bio_reactor_B_sample.query.all())
    return render_template('home.html')


@ app.route("/boxCoordinates", methods=['GET', 'POST'])
def boxCoordinates():
    if request.method == "POST":
        from_js = request.get_data()
        logging.info(from_js)
        data = json.loads(from_js)
        logging.info(data)
        tracking_thread = threading.Thread(
            target=tracking.start_trackig, args=(data,))
        tracking_thread.start()
        return jsonify({'status': 'OK', 'data': data})


@ app.route('/uploadFile', methods=['GET', 'POST'])
def upload_file():
    return render_template('uploadFile.html')


@ app.route('/uploadFile/reactorA',  methods=['GET', 'POST'])
def upload_to_a():
    form = upload_to_a_form()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('uploadToA.html', form=form)
        else:
            where_it_saved = save_file(form)

            new_upload = models.Bio_reactor_A_sample(date_recorded=form.date_recorded.data, date_uploaded=datetime.now(
            ), num_tissues=form.num_tissues.data, file_location=where_it_saved)

            models.insert_bio_sample(new_upload)
            '''
            db.session.add(new_upload)
            db.session.commit()
            '''
            # TODO:  where do we want to redirect to
            return '''
                    <!DOCTYPE html >
                    <h1> uploaded </h1 >
                    '''
    elif request.method == 'GET':
        return render_template('uploadToA.html', form=form)


@ app.route('/uploadFile/reactorB',  methods=['GET', 'POST'])
def upload_to_b():
    form = upload_to_b_form()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('uploadToB.html', form=form)
        else:
            #  TODO: clean up and comment this its confusing
            where_it_saved = save_file(form)
            tup_post_info = get_post_info(form.post.entries)
            li_of_post_info = tup_post_info[1]
            logging.info(li_of_post_info)

            new_upload = models.Bio_reactor_B_sample(date_recorded=form.date_recorded.data, date_uploaded=datetime.now(
            ), num_tissues=tup_post_info[0], post_zero=li_of_post_info[0], post_one=li_of_post_info[1], post_two=li_of_post_info[2], post_three=li_of_post_info[3], post_four=li_of_post_info[4], post_five=li_of_post_info[5], file_location=where_it_saved)

            models.insert_bio_sample(new_upload)

            # TODO:  where do we want to redirect to
            return '''
                    <!DOCTYPE html >
                    <h1> uploaded </h1 >
                    '''
    else:
        return render_template('uploadToB.html', form=form)
