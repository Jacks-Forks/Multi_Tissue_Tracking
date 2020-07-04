import json
import logging
import os
import threading
from datetime import datetime

import cv2
import models
import tracking
from flask import Blueprint, jsonify, redirect, render_template, request
from forms import PickVid, upload_to_a_form, upload_to_b_form
from werkzeug.utils import secure_filename

current_directory = os.getcwd()


UPLOAD_FOLDER = current_directory + "/static/uploads"


def save_video_file(form_passed):
    date_string = form_passed.date_recorded.data.strftime('%m_%d_%Y')
    # gets saves in experment folder
    experiment_num = str(form_passed.experiment_num.data)
    bio_reactor_num = form_passed.bio_reactor_num.data

    # gets save loaction uploadfolder/expermentnum/date/vid
    where_to_save = os.path.join(
        UPLOAD_FOLDER, experiment_num, date_string, 'videoFiles')

    # cheacks to make sure the save location exists if not exists
    if not os.path.exists(where_to_save):
        os.makedirs(where_to_save)

    orginal_filename = form_passed.file.data.filename
    extenstion = orginal_filename.rsplit('.', 1)[1].lower()

    # makes new file name for the vid format date_frewnum_bionum.ext
    new_filename = date_string + "_" + \
        "Freq" + str(form_passed.frequency.data) + "_" + \
        "Bio" + str(bio_reactor_num) + "." + extenstion

    # makes sure file name is crrect formats
    safe_filename = secure_filename(new_filename)

    # creates path to file
    path_to_file = os.path.join(where_to_save, safe_filename)

    # saves the file
    form_passed.file.data.save(path_to_file)

    # records vid rto databse
    vid_id = models.insert_video(form_passed.date_recorded.data,
                                 form_passed.experiment_num.data, bio_reactor_num, form_passed.frequency.data, path_to_file)
    return vid_id

# REVIEW: check allowed


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    video_object = models.get_video(vid_id)
    file_path = video_object.save_location
    number_of_tisues = len(video_object.tissues)
    logging.info(number_of_tisues)
    videostream = cv2.VideoCapture(file_path)
    image = videostream.read()[1]
    image_path = 'static/img/' + str(vid_id) + '.jpg'
    cv2.imwrite(image_path, image)
    return (image_path, number_of_tisues)
    # return render_template("selectPosts.html", path=image_path)


routes_for_flask = Blueprint(
    'routes_for_flask', __name__, template_folder='templates')


@ routes_for_flask.route('/')
def main():
    return render_template('home.html')


@ routes_for_flask.route("/boxCoordinates", methods=['GET', 'POST'])
def boxcoordinates():
    # TODO: comment all of this so it makes tissue_number_passed
    # TODO: delete image
    if request.method == "POST":
        from_js = request.get_data()
        data = json.loads(from_js)
        box_coords = data['boxes']
        video_id = int(data['video_id'])

        video_object = models.get_video(video_id)

        file_path = video_object.save_location
        date_recorded = video_object.date_recorded
        frequency = video_object.frequency
        experiment_num = video_object.experiment_num

        # list of tissue objecjs that are childeren of the vid
        tissues_object_list = video_object.tissues
        li_tissues_numbers = [
            tissue.tissue_number for tissue in tissues_object_list]
        logging.info(tissues_object_list)
        logging.info(li_tissues_numbers)

        tracking_thread = threading.Thread(
            target=tracking.start_trackig, args=(box_coords, file_path, experiment_num, date_recorded, frequency, li_tissues_numbers))
        tracking_thread.start()
        return jsonify({'status': 'OK', 'data': box_coords})


@ routes_for_flask.route('/uploadFile', methods=['GET', 'POST'])
def upload_file():
    return render_template('uploadFile.html')


@ routes_for_flask.route('/uploadFile/reactorA',  methods=['GET', 'POST'])
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

            # TODO:  where do we want to redirect to
            return
    elif request.method == 'GET':
        return render_template('uploadToA.html', form=form)


@ routes_for_flask.route('/uploadFile/reactorB',  methods=['GET', 'POST'])
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
            #where_it_saved = save_file(form)

            # save_video_file(form)

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

            # TODO: if uplad a csv

            new_video_id = save_video_file(form)

            add_tissues(li_of_post_info, experiment_num,
                        bio_reactor_num, new_video_id)

            return redirect('/pick_video')
    else:
        return render_template('uploadToB.html', form=form)

# REVIEW:  this works well but no without slections first


@routes_for_flask.route('/pick_video', methods=['GET', 'POST'])
def pick_video():
    form = PickVid()
    form.experiment.choices = [(row.num, row.num)
                               for row in models.Experiment.query.all()]
    if request.method == 'GET':
        return render_template('pick_video.html', form=form)

    if request.method == 'POST':
        video_id = form.vids.data
        tup_path_numTissues = get_post_locations(video_id)

        image_path = tup_path_numTissues[0]
        num_tissues = tup_path_numTissues[1]

        return (render_template("selectPosts.html", path=image_path, vid_id=video_id, number_tissues=num_tissues))

    return redirect('/get_dates')


@ routes_for_flask.route('/get_dates')
def get_dates():

    experiment = request.args.get('experiment', '01', type=str)
    dates = []
    for row in models.Video.query.filter_by(experiment_num=experiment).all():
        date_as_string = row.date_recorded.strftime('%m/%d/%Y')
        next_choice = (date_as_string, date_as_string)
        if next_choice not in dates:
            dates.append(next_choice)

    return jsonify(dates)


@ routes_for_flask.route('/get_video')
def get_video():

    date = request.args.get('dates', '01', type=str)
    experiment = request.args.get('experiment', '01', type=str)
    date = datetime.strptime(date, '%m/%d/%Y')
    date = date.date()

    vids = [(row.id, "bio" + str(row.bio_reactor_num) + " " + 'freq:' + str(row.frequency))
            for row in models.Video.query.filter_by(date_recorded=date, experiment_num=experiment).all()]

    return jsonify(vids)
