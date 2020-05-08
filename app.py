import base64
import io
import logging
import os
import urllib.parse

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import peakutils
from dash.dependencies import Input, Output, State
from flask import (Flask, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from scipy.signal import savgol_filter
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


#Dash stuff
dasher = dash.Dash(__name__, server=app, routes_pathname_prefix="/dash/")
dasher.layout = html.Div([
    dcc.Upload(id='upload-data',
               children=html.Div(['Drag and Drop or ',
                                  html.A('Select Files')]),
               style={
                   'width': '100%',
                   'height': '60px',
                   'lineHeight': '60px',
                   'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'boderRadius': '5px',
                   'textAlign': 'center',
                   'margin': '10px'
               },
               multiple=True),
    html.Div('[Polynomial Value, Window]:'),
    dcc.RangeSlider(id='smoothing',
                    min=0,
                    max=31,
                    step=None,
                    value=[3, 13],
                    marks={
                        3: {
                            'label': '3',
                            'style': {
                                'color': '#77b0b1'
                            }
                        },
                        4: {
                            'label': '4'
                        },
                        5: {
                            'label': '5'
                        },
                        6: {
                            'label': '6'
                        },
                        7: {
                            'label': '7'
                        },
                        9: {
                            'label': '9'
                        },
                        11: {
                            'label': '11'
                        },
                        13: {
                            'label': '13'
                        },
                        15: {
                            'label': '15'
                        },
                        17: {
                            'label': '17'
                        },
                        19: {
                            'label': '19'
                        },
                        21: {
                            'label': '21'
                        },
                        23: {
                            'label': '23'
                        }
                    }),
    html.Div(' '),
    html.Div('Graphs:'),
    html.Div(id='graphs', children=[dcc.Graph(id='graph#{}'.format('1'))]),
    html.Div('Threshold:'),
    dcc.Slider(id='thresh', min=0, max=1, step=.1, value=.6),
    html.Div('MinDist:'),
    dcc.Slider(id='dist', min=0, max=10, value=5),
    html.Div('BufferDist:'),
    dcc.Slider(id='buff', min=0, max=10, value=3),
    html.Div(id='hh'),
    html.Button('Submit', id='button'),
    html.Div(id='tri')
])


def dataframecreator(raw):
    dataframes = []
    for i in range(len(raw)):
        content_type, content_string = raw[i].split(',')
        decoded = base64.b64decode(content_string)
        dataframes.append(pd.read_csv(io.StringIO(decoded.decode('utf-8'))))
    return dataframes


@dasher.callback(Output('graphs', 'children'), [
    Input('upload-data', 'contents'),
    Input('smoothing', 'value'),
    Input('thresh', 'value'),
    Input('buff', 'value'),
    Input('dist', 'value')
], [State('upload-data', 'filename'),
    State('upload-data', 'last_modified')])
def update_output(list_of_contents, smoothvalues, thresh, buff, mindist,
                  list_of_names, list_of_dates):
    #dataframes = []
    buffer = buff
    #thresh = .6
    #mindist = 5
    poly = smoothvalues[0]
    window = smoothvalues[1]
    if list_of_contents is not None:
        global dataframeo, origin, peaks, basepoints
        peaks = []
        basepoints = []
        dataframeo = dataframecreator(list_of_contents)
        origin = dataframecreator(list_of_contents)
        for i in range(len(dataframeo)):
            dataframeo[i]['disp'] = savgol_filter(origin[i]['disp'], window,
                                                  poly)
            dataframeo[i]['disp'] = dataframeo[i]['disp'] * -1
            peaks.append(
                peakutils.indexes(dataframeo[i]['disp'], thresh, mindist))
            peaks[i] = peaks[i][1:-1]
            basepoints.append([])
            for peak in peaks[i]:
                for k in range(peak - buffer, 1, -1):
                    dfdt = (dataframeo[i]['disp'][k] -
                            dataframeo[i]['disp'][k - 1])
                    if dfdt <= 0:
                        basepoints[i].append(k)
                        break
        return ([
            dcc.Graph(id='graph#{}'.format(i),
                      figure={
                          'data': [{
                              'x': dataframeo[i]['time'],
                              'y': dataframeo[i]['disp'],
                              'name': 'Trace 1',
                              'mode': 'line',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': dataframeo[i]['time'][peaks[i]],
                              'y': dataframeo[i]['disp'][peaks[i]],
                              'name': 'Trace 1',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': dataframeo[i]['time'][basepoints[i]],
                              'y': dataframeo[i]['disp'][basepoints[i]],
                              'name': 'Trace 1',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }]
                      }) for i in range(len(list_of_contents))
        ])


if __name__ == "__main__":
    app.run()
