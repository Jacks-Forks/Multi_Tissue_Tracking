import json
import logging
import os
import threading
from datetime import datetime

import cv2
import models
import tracking
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, url_for)
from forms import PickVid, upload_to_a_form, upload_to_b_form
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
    if filename.rsplit('.', 1)[1].lower() == 'csv':
        result = os.path.join(app.config['CSV_FOLDER'], date_string)
    elif filename.rsplit('.', 1)[1].lower() in video_file_extentions:
        result = os.path.join(app.config['VIDEO_FOLDER'], date_string)
    if os.path.isdir(result) is False:
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
    where_to_save = where_to_save + "/" + filename
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


def get_post_locations(vid_id):
    file_path = models.get_video(vid_id).save_location
    videostream = cv2.VideoCapture(file_path)
    image = videostream.read()[1]
    image_path = 'static/img/' + str(vid_id) + '.jpg'
    cv2.imwrite(image_path, image)
    return image_path
    # return render_template("selectPosts.html", path=image_path)


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
    return render_template('home.html')


@ app.route("/boxCoordinates", methods=['GET', 'POST'])
def boxcoordinates():
    if request.method == "POST":
        from_js = request.get_data()
        logging.info(from_js)
        data = json.loads(from_js)
        logging.info(data)
        logging.info(data['boxes'])
        box_coords = data['boxes']
        video_id = int(data['video_id'])
        file_path = models.get_video(video_id).save_location
        tracking_thread = threading.Thread(
            target=tracking.start_trackig, args=(box_coords, file_path,))
        tracking_thread.start()
        return jsonify({'status': 'OK', 'data': box_coords})


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

            # REVIEW: ideally would like to make these drop downs

            # checks if experiment exsits if it does makes it
            experiment_num = form.experiment_num.data
            if models.get_experiment(experiment_num) is None:
                models.insert_experiment(experiment_num)

            # checks if experiment exsits if it does makes it
            bio_reactor_num = form.bio_reactor_num.data
            if models.get_bio_reactor(bio_reactor_num) is None:
                models.insert_bio_reactor(bio_reactor_num)

            models.insert_video(form.date_recorded.data,
                                experiment_num, bio_reactor_num, form.video_num.data, form.frequency.data, where_it_saved)

            add_tissues(li_of_post_info, experiment_num,
                        bio_reactor_num, form.video_num.data)

            # TODO:  where do we want to redirect to
            return '''
                    <!DOCTYPE html >
                    <h1 > uploaded </h1 >
                    '''
    else:
        return render_template('uploadToB.html', form=form)

# REVIEW:  this works well but no without slections first


@app.route('/pick_video', methods=['GET', 'POST'])
def pick_video():
    form = PickVid()
    form.experiment.choices = [(row.num, row.num)
                               for row in models.Experiment.query.all()]
    if request.method == 'GET':
        return render_template('pick_video.html', form=form)

    if request.method == 'POST':
        # is the vid id
        print(form.vids.data)
        video_id = form.vids.data
        image_path = get_post_locations(video_id)

        return (render_template("selectPosts.html", path=image_path, vid_id=video_id))

    return redirect(url_for('get_dates'))


@ app.route('/get_dates')
def get_dates():

    experiment = request.args.get('experiment', '01', type=str)
    dates = []
    for row in models.Video.query.filter_by(experiment_num=experiment).all():
        date_as_string = row.date_recorded.strftime('%m/%d/%Y')
        next_choice = (date_as_string, date_as_string)
        if next_choice not in dates:
            dates.append(next_choice)

    return jsonify(dates)


@ app.route('/get_video')
def get_video():

    date = request.args.get('dates', '01', type=str)
    experiment = request.args.get('experiment', '01', type=str)
    date = datetime.strptime(date, '%m/%d/%Y')
    date = date.date()

    vids = [(row.id, "bio" + str(row.bio_reactor_num) + " " + 'freq:' + str(row.frequency))
            for row in models.Video.query.filter_by(date_recorded=date, experiment_num=experiment).all()]

    return jsonify(vids)
