
import logging
import os


from flask import (Flask, flash, redirect, render_template, request,
                   send_from_directory, url_for, abort, send_file)
from flask_autoindex import AutoIndex
from werkzeug.utils import secure_filename

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.warning("New Run Starts Here")

current_directory = os.getcwd()

# change to where things should be stored
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


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_UPLOAD_FOLDER
app.config['CSV_FOLDER'] = CSV_UPLOAD_FOLDER


def check_system():
    if os.path.isdir(app.config['UPLOAD_FOLDER']) == False:
        logging.info("no uploads folder")
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if os.path.isdir(app.config['VIDEO_FOLDER']) == False:
        os.mkdir(app.config['VIDEO_FOLDER'])
    if os.path.isdir(app.config['CSV_FOLDER']) == False:
        os.mkdir(app.config['CSV_FOLDER'])


check_system()


@app.route("/")
def main():
    return render_template('index.html')


'''
@app.route('/showFiles', defaults={'passedFolder': "", 'fileName': ""},  methods=['GET', 'POST'])
@app.route("/showFiles/<path:passedFolder>", methods=['GET', 'POST'])
@app.route("/showFiles/<path:passedFolder>/<path:fileName>", methods=['GET', 'POST'])
def showFiles(passedFolder, filesName):

    select = request.form.get('comp_select')

    if select != None:
        abs_path = os.path.join(
            app.config['VIDEO_FOLDER'], passedFolder, select)
        redirect(showFiles(passedFolder, select))
    else:
        abs_path = os.path.join(app.config['VIDEO_FOLDER'], passedFolder)

    logging.info("new: " + abs_path)

    if not os.path.exists(abs_path):
        logging.warning(abs_path)
        return abort(404)

    if os.path.isfile(abs_path):
        logging.info("is a file")
        return send_file(abs_path)

    files = os.listdir(abs_path)
    return render_template('viewUploads.html', files=files, path=abs_path)


@app.route("/test", methods=['GET', 'POST'])
def test():
    select = request.form.get('comp_select')
    return redirect('/showFiles/' + select)
'''

upload_index = AutoIndex(app, browse_root=app.config['UPLOAD_FOLDER'])


@app.route('/files')
@app.route('/files/<path:path>')
def browseFiles(path="."):
    if os.path.isfile(path):
        logging.info("is a file")
        return send_file(path)
    return upload_index.render_autoindex(path)


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
