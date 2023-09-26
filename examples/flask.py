import logging

import requests

from flask import Flask
from flask import redirect
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user

from flask_okta import OktaManager

logging.basicConfig()

requests_logger = logging.getLogger('urllib3')
requests_logger.setLevel(logging.DEBUG)
requests_logger.propagate = True

app = Flask(__name__)
app.config.from_pyfile('../instance/config.py')

okta = OktaManager(app, redirect_login_endpoint='hello')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello'))

@app.route('/')
@login_required
def hello():
    return f'Hello {current_user.name}!'
