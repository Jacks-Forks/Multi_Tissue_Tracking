
import glob
import os

import cv2
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, Response, make_response, render_template

folders = glob.glob('static/uploads/videofiles/*')
# TODO: delete this file
filer = videostream = None

app = dash.Dash(__name__, requests_pathname_prefix='/vidSelect/')
app.layout = html.Div([
    html.Button('Reload', id='button'),
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
    dash.dependencies.Output('folder', 'options'),
    [dash.dependencies.Input('button', 'n_clicks')]
)
def reload(button):
    folders = glob.glob('static/uploads/videofiles/*')
    return [{'label': i, 'value': i} for i in folders]


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
    # get the first frame of vid and pass that to JS select posts
    global filer, videostream

    splits = filer.split('/')
    base = splits[4].split('.')[0]

    # puts as opencs
    # filer needs to be the location of the vid
    videostream = cv2.VideoCapture(filer)
    # gets the first frame of image
    # REVIEW: : check spot zero
    images = videostream.read()[1]
    # creates folder to save img and write the first frame as image
    # can we do this in mem
    if not os.path.exists('static/img/' + splits[3]):
        os.mkdir('static/img/' + splits[3])
    cv2.imwrite('static/img/' + splits
                [3] + '/' + base + '.jpg', images)

    return render_template("selectPosts.html", path='static/img/' + splits[3] + '/' + base + '.jpg')
