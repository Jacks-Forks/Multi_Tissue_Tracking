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
import analysisFolder.calculations as calc

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

        dataframeo, peaks, basepoints, frontpoints, ten, fifty, ninety = analysis.findpoints(
            dataframes, buff, poly, window, thresh, dist)

        t50 = c50 = r50 = []
        devforce = actforce = pasforce = []
        peakdist = basedist = devdist = []

        for i in range(len(fifty)):
            for j in range(len(peaks[i])):
                peakdist.append(7 + dataframeo[i]['disp'][peaks[i][j]])
                basedist.append(7 + dataframeo[i]['disp'][basepoints[i][j]])
                devdist.append(peakdist[j] - basedist[j])

            actforce.append(calc.force(
                1330000, .0005, .012, .0115, .012, .0115, peakdist))
            pasforce.append(calc.force(
                1330000, .0005, .012, .0115, .012, .0115, basedist))
            devforce.append(calc.force(
                1330000, .0005, .012, .0115, .012, .0115, devdist))
            t50.append(calc.t50(fifty[i], dataframeo[i]['time']))
            c50.append(calc.c50(peaks[i], fifty[i], dataframeo[i]['time']))
            r50.append(calc.r50(peaks[i], fifty[i], dataframeo[i]['time']))

        print(t50)
        print(r50)
        print(c50)
        print(actforce)
        print(pasforce)
        print(devforce)

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
