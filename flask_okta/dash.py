from flask import current_app
from flask import redirect
from flask import url_for
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from .extension import OktaManager
from .wrappers import wrap_app_login_required

# normally endpoints are named with words but dash
# names them the same as the path
DASH_ROOT_ENDPOINT = '/'
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


def init_dash_for_okta(
    dash_app,
    login_manager = None,
    login_view = None,
    user_class = None,
):
    """
    :param dash_app:
        Dash application instance.
    :param login_manager:
        Defaults to `flask_login.LoginManager`.
    :param login_view:
        Defaults to Flask-Okta builtin blueprint view,
        `redirect_for_okta_login`.
    :param user_class:
        Defaults to `flask_okta.dash.User` class.
    """
    if login_view is None:
        # flask-okta built in view function endpoint
        login_view = 'okta.redirect_for_okta_login'

    if user_class is None:
        user_class = User

    if login_manager is None:
        login_manager = LoginManager(dash_app.server)

    if login_manager.login_view is None:
        login_manager.login_view = login_view

    @login_manager.user_loader
    def user_loader(user_id):
        # required for flask-login
        # user objects normally comes from a database of some kind
        return user_class.get(user_id)

    # wrap before adding blueprint routes
    wrap_app_login_required(dash_app.server)

    # Flask-Okta extension, flask app instance required here and enforced by
    # this function's arguments.
    okta = OktaManager(dash_app.server)

    @okta.after_authorization
    def after_authorization(userinfo):
        """
        View function decorated to respond after Okta authenticated.
        """
        user_id = userinfo['sub']
        user = user_class.get(user_id)
        if not user:
            # create user taking some of the user info data from Okta
            user = user_class(user_id, userinfo['email'], userinfo['name'])
            # update "database"
            USERS[user_id] = user
        login_user(user)
        return redirect(url_for(DASH_ROOT_ENDPOINT))

    @dash_app.server.route('/okta-logout')
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
        okta = current_app.extensions['okta']
        okta_logout_redirect_url = okta.logout_url(post_logout_redirect_url)
        return redirect(okta_logout_redirect_url)

    @dash_app.server.route(okta.post_logout_redirect_rule)
    def post_okta_logout():
        """
        Okta redirects back here after logout, according to
        post_logout_redirect_rule. OKTA_POST_LOGOUT_REDIRECT_URI in config. This
        attribute is set to a reasonable default if not specified.
        """
        return redirect(url_for(DASH_ROOT_ENDPOINT))

    return okta
