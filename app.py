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

@app.route("/")
def main():
    return render_template('index.html')

def whitchFileType(filename):
    VID_UPLOAD_FOLDER = UPLOAD_FOLDER + "/video"
    CSV_UPLOAD_FOLDER = UPLOAD_FOLDER + "/csvfiles"
    result = ""
    if filename.rsplit('.', 1)[1].lower() == 'csv':
        #UPLOAD_FOLDER = CSV_UPLOAD_FOLDER
        result = CSV_UPLOAD_FOLDER
    elif filename.rsplit('.', 1)[1].lower() == 'mov':
        result = VID_UPLOAD_FOLDER
    return result
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadFile', methods = [ 'GET', 'POST'])
def upload_file():
    if request.method == 'POST':
    # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            where_to_save = whitchFileType(file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(where_to_save, filename))
            logging.info("here" + whitchFileType(file.filename))
            return redirect(url_for('main'))
            #return redirect(url_for(fileType=where_to_save, filename=filename))

    return render_template('upload.html')


#this needs to be fixed    
@app.route('/<fileType>/<filename>')
def uploaded_file(fileType, filename):
    logging.info("hell" + fileType)
    return send_from_directory(fileType, filename)

if __name__ == "__main__":
    app.run()
