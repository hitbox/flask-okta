from dash import Dash
from dash import html
from flask import Flask

from flask_okta import OktaManager

dash_app = Dash(__name__)

dash_app.layout = html.Div('Hello Dash App')

app = dash_app.server
okta = OktaManager(app)
