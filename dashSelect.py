import glob

import dash
import dash_core_components as dcc
import dash_html_components as html

from flask import render_template
from flask import Flask, make_response, render_template, Response
import os
import cv2

folders = glob.glob('static/uploads/videofiles/*')

filer = videostream = None

app = dash.Dash(__name__, requests_pathname_prefix='/vidSelect/')
app.layout = html.Div([
    html.Div('I Hate Atom Beutify'),
    dcc.Dropdown(
        id='folder',
        options=[
            {'label': i, 'value': i} for i in folders
        ]
    ),
    dcc.Dropdown(
        id='file'
    ),
    html.Div(id='fileselected'),
    dcc.Link('Navigate to "/page-2"', href='/vidSelect/post', refresh=True),
])


@app.callback(
    dash.dependencies.Output('file', 'options'),
    [dash.dependencies.Input('folder', 'value')])
def selected_folder(folder):
    files = []
    if folder is not None:
        files = glob.glob(folder + '/*')
    return [{'label': i, 'value': i} for i in files]


@app.callback(
    dash.dependencies.Output('fileselected', 'children'),
    [dash.dependencies.Input('file', 'value')])
def selected_file(file):
    if file is not None:
        global filer
        filer = file
        postselect()
        return


@app.server.route('/post')
def postselect():
    global filer, videostream

    splits = filer.split('/')
    base = splits[4].split('.')[0]

    videostream = cv2.VideoCapture(filer)
    images = videostream.read()[1]
    if not os.path.exists('static/img/' + splits[3]):
        os.mkdir('static/img/' + splits[3])
    cv2.imwrite('static/img/' + splits
                [3] + '/' + base + '.jpg', images)

    return render_template("index.html", path='static/img/' + splits[3] + '/' + base + '.jpg')
