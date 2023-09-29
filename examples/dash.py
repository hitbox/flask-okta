from dash import Dash
from dash import Input
from dash import Output
from dash import dcc
from dash import html
from flask import current_app
from flask_login import current_user
from flask_login import login_user

from flask_okta import init_dash_for_okta
from flask_okta.dash import User

dash_app = Dash(__name__)

dash_app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),
    html.P(id='current_user-output'),
])

@dash_app.callback(
    Output(component_id='my-output', component_property='children'),
    Output(component_id='current_user-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    # NOTE
    # - this is a modified version of:
    #   https://dash.plotly.com/basic-callbacks#simple-interactive-dash-app
    passthrough = html.Div([
        html.Div(f'Output from server: {input_value}'),
    ])
    return (
        passthrough,
        f'Hello { current_user.name }!',
    )

# configure Flask extensions, flask-login and flask-okta, with the usual Flask
# configuration machinery.
dash_app.server.config.from_envvar('FLASK_OKTA_EXAMPLE_CONFIG')

# add login_required to view functions
init_dash_for_okta(dash_app)

flask_app = dash_app.server

@flask_app.before_request
def before_request():
    is_authenticated = current_user.is_authenticated
    is_bypass_okta = current_app.config.get('BYPASS_OKTA', False)
    if not is_authenticated and is_bypass_okta:
        login_user(User('test123', 'test123@email.com', 'Test User'))
