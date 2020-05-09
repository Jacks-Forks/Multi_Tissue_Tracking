import urllib.parse
import base64
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import glob
from dash.dependencies import Input, Output, State

import analysisFolder.analysis as analysis

dates = glob.glob('static/uploads/csvfiles/*')

dasher = dash.Dash(__name__, requests_pathname_prefix='/dash/')
dasher.layout = html.Div([
    dcc.Link('Go to Upload', href='/uploadFile', refresh=True),
    dcc.Dropdown(
        id="files",
        options=[
            {'label': i, 'value': i} for i in dates
        ]
    ),
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
    html.Div('Graphs:'),
    html.Div(id='graphs', children=[dcc.Graph(id='graph#{}'.format('1'))])
])


@dasher.callback(Output('graphs', 'children'), [
    Input('files', 'value'),
    Input('smoothing', 'value'),
    Input('thresh', 'value'),
    Input('buff', 'value'),
    Input('dist', 'value')
])
def storedFiles(folder, smooth, thresh, buff, dist):
    dataframes = []
    if folder is not None:
        files = glob.glob(folder + '/*')
        for file in files:
            dataframes.append(pd.read_csv(file))
        poly = smooth[0]
        window = smooth[1]

        dataframeo, peaks, basepoints, frontpoints = analysis.findpoints(dataframes, buff, poly,
                                                                         window, thresh, dist)
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
                          }]
            }) for i in range(len(files))
        ])
