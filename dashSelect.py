import glob

import dash
import dash_core_components as dcc
import dash_html_components as html

folders = glob.glob('static/uploads/videofiles/*')

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
    html.Div(id='fileselected')
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
        return 'You selected "{}"'.format(file)
