import datetime
import json
import logging
import os
import threading

import models
import tracking
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, url_for)
from forms import upload_to_a_form, upload_to_b_form
from models import db
from werkzeug.utils import secure_filename

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.warning("New Run Starts Here")

current_directory = os.getcwd()


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

# REVIEW: can proablly combine these too functions


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
    return count, li


def add_tissues(li_of_post_info, experiment_num_passed, bio_reactor_num_passed, video_id_passed):
    for post, info in enumerate(li_of_post_info):
        # check is there is a tissue on post
        if info != 'empty':
            # splits so tissue num is in [0] and type in [1]
            split_list = info.split(',')
            tissue_num = split_list[0]
            tissue_type = split_list[1]
            models.insert_tissue_sample(
                tissue_num, tissue_type, experiment_num_passed, bio_reactor_num_passed, post, video_id_passed)


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['VIDEO_FOLDER'] = VIDEO_UPLOAD_FOLDER
    app.config['CSV_FOLDER'] = CSV_UPLOAD_FOLDER
    #  REVIEW: : where do we wanna save this and name it
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #  REVIEW: : this needs to be changed
    app.secret_key = 'development key'
    db.init_app(app)
    return app


app = create_app()
app.app_context().push()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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
    models.insert_experiment(1)
    models.insert_bio_reactor(1)
    models.insert_video(datetime.datetime.now(), 1, 1)
    models.insert_tissue_sample(42, 'idk', 1, 1, 55, 1)
    return render_template('home.html')


@ app.route("/boxCoordinates", methods=['GET', 'POST'])
def boxcoordinates():
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
                    <h1 > uploaded < /h1 >
                    '''
    elif request.method == 'GET':
        return render_template('uploadToA.html', form=form)


@ app.route('/uploadFile/reactorB',  methods=['GET', 'POST'])
def upload_to_b():
    li = ['0,idk', 'empty', '2,other', 'empty', 'empty', 'empty']
    add_tissues(li, 1, 1, 1)
    form = upload_to_b_form()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('uploadToB.html', form=form)
        else:
            #  TODO: clean up and comment this its confusing
            #  TODO: get expirment number, bio reactior is and vid id
            # tissie num and type are recored and place in list can be converted to type
            where_it_saved = save_file(form)
            tup_post_info = get_post_info(form.post.entries)
            li_of_post_info = tup_post_info[1]
            logging.info(li_of_post_info)
            add_tissues(li_of_post_info, form.experiment_num.data,
                        form.bio_reactor_num.data, form.video_id.data)
            # add_tissues(li_of_post_info, ex)
            # TODO:  where do we want to redirect to
            return '''
                    <!DOCTYPE html >
                    <h1 > uploaded </h1 >
                    '''
    else:
        return render_template('uploadToB.html', form=form)
