import glob
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_table
new_df = pd.read_csv('DF_Data.csv')
external_stylesheets = ''

selected_name = 'Connor'

params = ['Machine Bench Press', 'Dumbell Row', 'Lat Pulldown', 'Bicep Curl', 'Sit-ups']

user_array = [{'label': "Connor", 'value': 'Connor'}]
workout_options_array = [{'label': i, 'value': i} for i in params]
table_array = [{'id': 'Day', 'name': 'Day'}] + [{'id': i, 'name': i,
                                                 'deletable': True,
                                                 'renamable': True} for i in params]


def check_workout_options(options_array):
    if glob.glob('DF_Data.csv'):
        options_array = [{'label': i, 'value': i} for i in new_df.columns]
        return options_array
    else:
        return options_array


def check_columns_options(options_array):
    if glob.glob('DF_Data.csv'):
        options_array = [{'id': i, 'name': i, 'deletable': True, 'renamable': True} for i in new_df.columns]
        return options_array
    else:
        return options_array


n_rows = 1

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {'background': 'gray', 'text': '#111111'}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Workout Tracker',
            style={'textAlign': 'center', 'color': colors['text'], 'padding-top': '25px'}),

    html.Div(children=[html.Label('User:'),
                       dcc.Dropdown(
                           id='UserDropdown',
                           options=user_array,
                           value=user_array[0]['value']
                       )], style={'width': '40%', 'padding-left': '30%'}),

    html.Button('Add Row', id='AddRowButton', style={'width': '10%', 'margin-left': '45%', 'margin-top': '25px'},
                n_clicks=0),

    html.Div([
        dcc.Input(
            id='editing-columns-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='editing-columns-button', n_clicks=0)
    ], style={'height': 50, 'margin-left': '40%', 'margin-top': '25px'}),

    html.Div(dash_table.DataTable(
        id='DataTable',
        columns=check_columns_options(table_array),
        data=[dict(Day=i, **{param: 0 for param in params}) for i in range(1, n_rows)],
        editable=True,
        style_table={'maxHeight': '300px',
                     'overflowY': 'scroll',
                     'maxWidth': '100%',
                     'overflowX': 'scroll'}
    ), style={'margin-top': '25px', 'margin-bottom': '25px', 'width': '100%'}),

    html.Div(dash_table.DataTable(
        id='DataTableContainer'
    )),

    html.Div([html.Button('Save', id='save_button', style={'width': '5%', 'margin-left': '47.5%'}),
              html.Button('Load', id='load_button', style={'width': '5%', 'margin-left': '5%', 'display': 'none'})]),
    html.P(id='save-button-hidden', style={'display': 'none'}),

    html.Div(children=[html.Label('Workout:'),
                       dcc.Dropdown(
                           id='WorkoutDropdown',
                           options=check_workout_options(workout_options_array),
                           value=workout_options_array[0]['value']
                       )], style={'width': '40%', 'padding-left': '30%'}),

    html.Div([dcc.Graph(
        id='Graph',
        figure={
            'data': [],
            'layout': {}
        },

        style={'width': '50%', 'padding-left': '25%', 'padding-top': '25px', 'padding-bottom': '25px'})])

])


@app.callback(Output('save-button-hidden', ''),
              [Input('DataTable', 'data'),
               Input('DataTable', 'columns'),
               Input('save_button', 'n_clicks')])
def save_datatable_data(rows, columns, n_clicks):
    new_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    if n_clicks != 0:
        new_df.to_csv('DF_Data.csv', index=False)


@app.callback(Output('Graph', 'figure'),
              [Input('DataTable', 'data'),
               Input('DataTable', 'columns'),
               Input('WorkoutDropdown', 'value')])
def display_output(rows, columns, selected_workout):
    new_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return {
        'data': [go.Scatter(x=new_df['Day'],
                            y=new_df[selected_workout],
                            mode='markers+lines')
                 ]
    }


@app.callback(
    Output('DataTable', 'columns'),
    [Input('editing-columns-button', 'n_clicks'),
     Input('load_button', 'n_clicks')],
    [State('editing-columns-name', 'value'),
     State('DataTable', 'columns')])
def update_columns(n_clicks, load_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns


@app.callback(
    Output('WorkoutDropdown', 'options'),
    [Input('editing-columns-button', 'n_clicks')],
    [State('WorkoutDropdown', 'options'),
     State('editing-columns-name', 'value')])
def update_dropdown(n_clicks, options, value):
    if n_clicks > 0:
        options.append({'label': value, 'value': value})
    return options


@app.callback(
    Output('DataTable', 'data'),
    [Input('AddRowButton', 'n_clicks'),
     Input('load_button', 'n_clicks')],
    [State('DataTable', 'data'),
     State('DataTable', 'columns')])
def add_row(n_clicks, load_clicks, rows, columns):
    new_df = pd.read_csv('DF_Data.csv')
    if n_clicks != 0:
        rows.append({c['id']: '' for c in columns})
        return rows
    if load_clicks != 0:
        return new_df.to_dict('rows')


if __name__ == '__main__':
    app.run_server(debug=True)
