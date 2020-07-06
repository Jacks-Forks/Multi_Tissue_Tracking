import base64
import glob
import io
import urllib.parse

import analysisFolder.analysis as analysis
import analysisFolder.calculations as calc
import dash
import dash_core_components as dcc
import dash_html_components as html
import models
import pandas as pd
from app import app
from dash.dependencies import Input, Output, State

# TODO: looks for csv in wrong spot do it from db???
# creates an app context for the database
app.app_context().push()

# just to show models can be acessed
print('tissues')
print(models.Tissue.query.all())

'''
These Should Be User Editable
'''
youngs = 1330000
radius = .0005
l_r = .012
a_r = .0115
l_l = .012
a_l = .0115
count = 0

# Grabs a list of all the dates in csvfiles
# TODO: File Structure
dates = glob.glob('static/uploads/csvfiles/*')
# dates = glob.glob('static/uploads/experiment
# Going to need an extra dropdown

# Finds all the stored bioreactor post heights and stores them in a list of dataframes
summarys = []
bioreactors = sorted(glob.glob('static/bioreactors/*'))
[summarys.append(pd.read_csv(bio)) for bio in bioreactors]

# Create dash app (renders the webpage)
dasher = dash.Dash(__name__, requests_pathname_prefix='/dash/')
dasher.layout = html.Div([
    # Button to take you to upload files
    dcc.Link('Go to Upload', href='/uploadFile', refresh=True),
    # Button to reload the page in case it doesnt see all the files it should
    html.Button('Reload', id='button'),
    # A dropdown of all the dates there are csv files available for
    dcc.Dropdown(
        id="files",
        options=[
            {'label': i, 'value': i} for i in dates
        ]
    ),
    # Curve fitting stuff
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
    html.Div('Threshold:'),
    dcc.Slider(id='thresh', min=0, max=1, step=.1, value=.6),
    html.Div('MinDist:'),
    dcc.Slider(id='dist', min=0, max=10, value=5),
    html.Div('BufferDist:'),
    dcc.Slider(id='buff', min=0, max=10, value=3),
    html.Button(id='reload', n_clicks=0, hidden=True),
    # TODO: Take out youngs I think
    dcc.Input(
        id='young',
        type='number',
        value='1330000'
    ),
    html.Div(id='holder'),
    html.Div('Graphs:'),
    html.Div(id='graphs', children=[dcc.Graph(id='graph#{}'.format('1'))])
])

# Gets called when reload is clicked. Returns a new list of dates
@dasher.callback(
    Output('files', 'options'),
    [Input('button', 'n_clicks')]
)
def reload(button):
    dates = glob.glob('static/uploads/csvfiles/*')
    return [{'label': i, 'value': i} for i in dates]

# Updates youngs
# TODO: Can probably be removed. Store in database or file or something
@dasher.callback(Output('reload', 'n_clicks'), [
    Input('young', 'value')
])
def consts(you):
    global count, youngs
    youngs = you
    count = count + 1
    return count

# The main graphing function. Gets called whenever on of the parameters changes
@dasher.callback(Output('graphs', 'children'), [
    Input('files', 'value'),
    Input('smoothing', 'value'),
    Input('thresh', 'value'),
    Input('buff', 'value'),
    Input('dist', 'value'),
    Input('reload', 'n_clicks')
])
def storedFiles(folder, smooth, thresh, buff, dist, but):
	# Create a list to store the dataframes in.
    dataframes = []

    if folder is not None:
        # Reads the files in the selected folder
        files = glob.glob(folder + '/*')
        for file in files:
            # Reads each file in as a dataframe
            dataframes.append(pd.read_csv(file))
        for i in range(len(dataframes)):
            # Converts time to seconds
            # TODO: Check this conversion
            dataframes[i]['time'] = dataframes[i]['time'] / 1000

        poly = smooth[0]
        window = smooth[1]

        # Calls the findpoints function which returns all the points of interest.
        dataframeo, peaks, basepoints, frontpoints, ten, fifty, ninety = analysis.findpoints(
            dataframes, buff, poly, window, thresh, dist)

        # Create a list for each parameter, can maybe be better handled
        t50 = []
        c50 = []
        r50 = []

        t2rel50 = []
        t2rel90 = []
        t2pks = []

        dfdt = []
        negdfdt = []

        freq = []
        freqCOV = []

        devforce = []
        actforce = []
        pasforce = []

        peakdist = []
        basedist = []
        devdist = []

        # For each dataframe
        for i in range(len(fifty)):
            #For each contraction
            for j in range(len(peaks[i])):
                # Find the distances for sys, dias, and dev force
                # TODO: IMPORTANT, SHOULD THIS BE peakdist[i] etc...
                peakdist.append(7 + dataframeo[i]['disp'][peaks[i][j]])
                basedist.append(7 + dataframeo[i]['disp'][basepoints[i][j]])
                devdist.append(peakdist[j] - basedist[j])

            splitter = files[i].split('_')

			# If it is multi tissue,
            if splitter[2] == 'M':
                # TODO: we need to know whitch csv is selected the id or sothing else to look it up
                # TODO: DATABASE. Need Bioreactor number.
                # TODO: DATABASE. Need tissue location.
                bio = int(splitter[3])
                loc = int(splitter[4])
                # Read in post heights from csv values (imported into database earlier)
                l_r = summarys[bio - 1]['RPostHt'][loc - 1]
                l_l = summarys[bio - 1]['LPostHt'][loc - 1]
                a_r = summarys[bio - 1]['RTissHt'][loc - 1]
                a_l = summarys[bio - 1]['LTissHt'][loc - 1]
            else:
                # If other system, set these as heights
                l_r = .012
                l_l = .012
                a_r = .0115
                a_l = .0115

            # Call functions for each calculation. Functions found in calculations.py
            actforce.append(calc.force(
                youngs, radius, l_r, a_r, l_l, a_l, peakdist))
            pasforce.append(calc.force(
                youngs, radius, l_r, a_r, l_l, a_l, basedist))
            devforce.append(calc.force(
                youngs, radius, l_r, a_r, l_l, a_l, devdist))
            t50.append(calc.t50(fifty[i], dataframeo[i]['time']))
            c50.append(calc.c50(peaks[i], fifty[i], dataframeo[i]['time']))
            r50.append(calc.r50(peaks[i], fifty[i], dataframeo[i]['time']))
            freq.append(calc.beating_freq(dataframeo[i]['time'], peaks[i]))
            freqCOV.append(freq[i][1] / freq[i][0])
            t2rel50.append(calc.time2rel50(
                fifty[i], peaks[i], dataframeo[i]['time']))
            t2rel90.append(calc.time2rel50(
                ten[i], peaks[i], dataframeo[i]['time']))
            t2pks.append(calc.time2pk(ten[i], peaks[i], dataframeo[i]['time']))
            dfdt.append(calc.dfdt(ninety[i], ten[i], dataframeo[i]['time']))
            negdfdt.append(calc.dfdt(ninety[i], ten[i], dataframeo[i]['time']))

            # TODO: clea up these prints

        # Print out calculated values
        # TODO: Change to store and download data

        print(str(t50) + '\n')
        print(str(r50) + '\n')
        print(str(c50) + '\n')

        print(str(t2pks) + '\n')
        print(str(t2rel50) + '\n')
        print(str(t2rel90) + '\n')

        print(str(dfdt) + '\n')
        print(str(negdfdt) + '\n')

        print(str(freq) + '\n')
        print(str(freqCOV) + '\n')

        print(str(actforce) + '\n')
        print(str(pasforce) + '\n')
        print(str(devforce) + '\n')

        #Returns the graph with all the points of interest graphed.
        return ([
            dcc.Graph(id='graph#{}'.format(i),
                      figure={
                          'data': [{
                              'x': dataframeo[i]['time'],
                              'y': dataframeo[i]['disp'],
                              'name': 'Displacement',
                              'mode': 'line',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': dataframeo[i]['time'][peaks[i]],
                              'y': dataframeo[i]['disp'][peaks[i]],
                              'name': 'Peaks',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': dataframeo[i]['time'][basepoints[i]],
                              'y': dataframeo[i]['disp'][basepoints[i]],
                              'name': 'Basepoints',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': dataframeo[i]['time'][frontpoints[i]],
                              'y': dataframeo[i]['disp'][frontpoints[i]],
                              'name': 'Frontpoints',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': ten[i][0],
                              'y': ten[i][1],
                              'name': 'Ten Cont',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': fifty[i][0],
                              'y': fifty[i][1],
                              'name': 'Fifty Cont',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': ninety[i][0],
                              'y': ninety[i][1],
                              'name': 'Ninety Cont',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': ten[i][2],
                              'y': ten[i][3],
                              'name': 'Ten Rel',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': fifty[i][2],
                              'y': fifty[i][3],
                              'name': 'Fifty Ten',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }, {
                              'x': ninety[i][2],
                              'y': ninety[i][3],
                              'name': 'Ninety Rel',
                              'mode': 'markers',
                              'marker': {
                                  'size': 12
                              }
                          }]
            }) for i in range(len(files))
        ])
