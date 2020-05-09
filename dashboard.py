import urllib.parse
import base64
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import peakutils
from dash.dependencies import Input, Output, State
from scipy.signal import savgol_filter

dasher = dash.Dash(__name__, requests_pathname_prefix='/dash/')
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
