import dash
import dash_html_components as html
import dash_core_components as dcc
import glob

folders = glob.glob('static/uploads/videofiles/*')

app = dash.Dash(__name__, requests_pathname_prefix='/vidSelect/')
app.layout = html.Div([
    html.Div('I Hate Atom Beutify'),
    dcc.Dropdown(
        id='folder',
        options=[
            {'label': i, 'value': i} for i in folders
        ],
        value=folders[0]
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
    files = glob.glob(folder + '/*')
    return [{'label': i, 'value': i} for i in files]

@app.callback(
    dash.dependencies.Output('fileselected', 'children'),
    [dash.dependencies.Input('file', 'value')])
def selected_file(file):
    return 'You selected "{}"'.format(file)
