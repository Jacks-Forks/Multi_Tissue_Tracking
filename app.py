import json
import logging
import os
import threading

from werkzeug.utils import secure_filename

import tracking
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, url_for)

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
    # return render_template('upload.html')
    return redirect("/uploadFile")


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
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            where_to_save = where_to_upload(file.filename)
            logging.info('Where does it save: ' + where_to_save)
            filename = secure_filename(file.filename)
            file.save(os.path.join(where_to_save, filename))
            return '''
            <!DOCTYPE html>
            <h1> uploaded </h1>
            '''

    return render_template('upload.html')


# error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('fileNotFound.html'), 404
