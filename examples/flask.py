import logging

from flask import Flask
from flask import redirect
from flask import url_for
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user

from flask_okta import OktaManager

USERS = {}

class User(UserMixin):
    """
    Simple dictionary-backed user model.
    """

    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

    @staticmethod
    def get(user_id):
        return USERS.get(user_id)


# configure logging ASAP. before app creation preferred by Flask docs.
logging.basicConfig()

requests_logger = logging.getLogger('urllib3')
requests_logger.setLevel(logging.DEBUG)
requests_logger.propagate = True

# create app
app = Flask(__name__)
app.config.from_envvar('FLASK_OKTA_EXAMPLE_CONFIG')

# create and initialize extensions
login_manager = LoginManager(app)

# flask-okta login endpoint to redirect to okta
# this is the default endpoint flask-okta for redirect to okta
login_manager.login_view = 'okta.redirect_for_okta_login'

okta = OktaManager(
    app,
    login_userinfo = lambda: login_userinfo,
)

def login_userinfo(userinfo):
    """
    Return view func response after access token exchange and getting userinfo.
    """
    user_id = userinfo['sub']
    user = User.get(user_id)
    if not user:
        # create user
        user = User(user_id, userinfo['email'], userinfo['name'])
        # update "database"
        USERS[user_id] = user
    login_user(user)

    # redirect after login
    url = url_for('hello')
    return redirect(url)

@login_manager.user_loader
def user_loader(user_id):
    # required for flask-login
    # normally comes from a database of some kind
    return User.get(user_id)

@app.route('/logout')
@login_required
def logout():
    # TODO: logout of Okta?
    logout_user()
    return redirect(url_for('hello'))

@app.route('/')
@login_required
def hello():
    return f'Hello {current_user.name}!'
