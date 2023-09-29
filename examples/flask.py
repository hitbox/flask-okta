import logging

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import url_for
from flask_login import LoginManager
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from flask_okta import OktaManager
from flask_okta.dash import User

# configure logging ASAP. before app creation preferred by Flask docs.
logging.basicConfig()

# get logging from `requests` backend transfers
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

okta = OktaManager(app)

@login_manager.user_loader
def user_loader(user_id):
    # required for flask-login
    # user objects normally come from a database of some kind
    return User.get(user_id)

@okta.after_authorization
def after_authorization(userinfo):
    """
    Callback after Okta authentication. Collect some user info into a User
    instance and log the user object in with flask-login. Finally redirect to
    the greeting endpoint.
    """
    user_id = userinfo['sub']
    user = User.get(user_id)
    if not user:
        # create user taking some of the user info data from Okta
        user = User(user_id, userinfo['email'], userinfo['name'])
        # update "database"
        USERS[user_id] = user
    # login our user object with flask-login
    login_user(user)
    return redirect(url_for('hello'))

@app.route('/okta-logout')
@login_required
def okta_logout():
    """
    Logout of Okta and redirect back here to logout session user object.
    """
    # logout our user object with flask-login
    logout_user()
    # logout of Okta
    # post_logout_redirect_uri must also be configured in Okta to work
    post_logout_redirect_url = url_for(
        'post_okta_logout', # endpoint to our own app
        _external = True, # flag to get full url
    )
    # construct url and args to logout of Okta and redirect back here
    okta_logout_redirect_url = okta.logout_url(post_logout_redirect_url)
    return redirect(okta_logout_redirect_url)

@app.route(okta.post_logout_redirect_rule)
def post_okta_logout():
    """
    Okta redirects back here after logout, according to
    post_logout_redirect_rule. OKTA_POST_LOGOUT_REDIRECT_URI in config. This
    attribute is set to a reasonable default if not specified.
    """
    # simple example just goes back to the hello endpoint which requires login,
    # which means it will redirect to the login page we set up.
    return redirect(url_for('hello'))

@app.route('/userinfo')
@login_required
def userinfo():
    """
    Info from Okta about currently logged in user.
    """
    return jsonify(okta.userinfo())

@app.route('/')
@login_required
def hello():
    """
    Greeting and link to user information and logout.
    """
    html = [f'<p>Hello {current_user.name}!</p>']
    html.append(f'''<p><a href="{ url_for('userinfo') }">userinfo</a></p>''')
    html.append(f'''<p><a href="{ url_for('okta_logout') }">logout</a></p>''')
    return ''.join(html)
