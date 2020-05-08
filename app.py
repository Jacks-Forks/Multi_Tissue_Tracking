import logging
import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

logging.basicConfig(filename='app.log', level=logging.DEBUG)

dirpath = os.getcwd()

logging.info(dirpath)

UPLOAD_FOLDER = dirpath + "/static/uploads"
VID_UPLOAD_FOLDER = UPLOAD_FOLDER + "/video"
CSV_UPLOAD_FOLDER = UPLOAD_FOLDER + "/csvfiles"
ALLOWED_EXTENSIONS = {'csv', 'mov'}



logging.info(UPLOAD_FOLDER)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.info("What does app print" + app.config['UPLOAD_FOLDER'])

@app.route("/")
def main():
    return render_template('index.html')

def file_type_upload_folder(filename):
    VID_UPLOAD_FOLDER = "/video"
    CSV_UPLOAD_FOLDER ="/csvfiles"
    result = ""
    if filename.rsplit('.', 1)[1].lower() == 'csv':
        result = CSV_UPLOAD_FOLDER
    elif filename.rsplit('.', 1)[1].lower() == 'mov':
        result = VID_UPLOAD_FOLDER
    return result

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadFile', methods = [ 'GET', 'POST'])
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
            whitch_file_type = file_type_upload_folder(file.filename)
            where_to_save = app.config['UPLOAD_FOLDER'] + whitch_file_type
            logging.info('Where does it save: ' + where_to_save)
            filename = secure_filename(file.filename)
            file.save(os.path.join(where_to_save, filename))
            return redirect(url_for('uploaded_file', fileType = whitch_file_type, filename = filename))

    return render_template('upload.html')


#this needs to be fixed
@app.route('/uploads/<fileType>/<filename>')
def uploaded_file(fileType, filename):
    path_to_file = fileType + "/" + filename
    logging.info("path: " + path_to_file)
    return send_from_directory(app.config['UPLOAD_FOLDER'], path_to_file)

if __name__ == "__main__":
    app.run()
