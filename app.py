
import logging
import os

from flask import (Flask, flash, redirect, render_template, request,
                   send_from_directory, url_for)

from werkzeug.utils import secure_filename

logging.basicConfig(filename='app.log', level=logging.DEBUG)

#file system set up


def check_system():
    if os.path.isdir('./static/uploads') == False:
        logging.info("no uploads folder")
        os.mkdir('./static/uploads')
    if os.path.isdir('./static/uploads/csvfiles') == False:
        os.mkdir('./static/uploads/csvfiles')
    if os.path.isdir('./static/uploads/videofiles') == False:
        os.mkdir('./static/uploads/videofiles')


check_system()

current_directory = os.getcwd()

UPLOAD_FOLDER = current_directory + "/static/uploads"
VIDEO_UPLOAD_FOLDER = UPLOAD_FOLDER + "/videofiles"
CSV_UPLOAD_FOLDER = UPLOAD_FOLDER + "/csvfiles"

ALLOWED_EXTENSIONS = {'csv', 'mov'}


def where_to_upload(filename):
    result = ""
    if filename.rsplit('.', 1)[1].lower() == 'csv':
        result = app.config['CSV_FOLDER']
    elif filename.rsplit('.', 1)[1].lower() == 'mov':
        result = app.config['VIDEO_FOLDER']
    return result


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS

    #flask stuff


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_UPLOAD_FOLDER
app.config['CSV_FOLDER'] = CSV_UPLOAD_FOLDER


@app.route("/")
def main():
    return render_template('index.html')


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


@app.route('/uploads/<filefolder>')
def view_upload_folder(filefolder):
    list_of_files = []

    for filename in os.listdir(app.config[filefolder]):
        list_of_files.append(filename)

    return render_template('viewUploads.html', value=list_of_files)
