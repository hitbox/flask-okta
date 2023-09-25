from flask import Flask
from flask_login import current_user
from flask_login import login_required

from flask_okta import OktaManager

app = Flask(__name__)
app.config.from_pyfile('../instance/config.py')

okta = OktaManager(app)

@app.route('/')
@login_required
def hello():
    return f'Hello {current_user}!'
