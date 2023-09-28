import requests

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask_login import login_user

from . import html
from .okta import authenticated_userinfo
from .okta import exchange_for_userinfo
from .okta import prepare_redirect_authentication

def get_okta_extension():
    return current_app.extensions['okta']

def get_okta_debug():
    return current_app.config.get('OKTA_DEBUG', False)

def abort_for_debug():
    """
    Abort if not in debugging mode.
    """
    if not get_okta_debug():
        abort(404)

def abort_for_callback(code, state):
    """
    abort for invalid values from Okta.
    """
    if not code:
        abort(403, 'code not returned')

    if state != session['_okta_state']:
        abort(400, f'states do not match.')

def create_okta_blueprint(
    blueprint_name,
    import_name,
    okta_redirect_rule,
):
    """
    Blueprint to redirect for login and respond to callback.
    """
    okta_bp = Blueprint(
        name = blueprint_name,
        import_name = import_name,
    )
    _init_routes(okta_bp, okta_redirect_rule)
    return okta_bp

def _init_routes(okta_bp, okta_redirect_rule):
    """
    Add okta routes to blueprint.

    :param okta_bp:
        Flask blueprint to add routes to.
    :param okta_redirect_rule:
        URL Rule used by a view function to redirect to okta with
        authentication query parameters.
    """

    @okta_bp.route('/redirect-for-okta-login')
    def redirect_for_okta_login():
        """
        Redirect to Okta for authentication using configured values.
        """
        redirect_authentication = prepare_redirect_authentication()

        if get_okta_debug():
            # debugging preview before redirect with link to continue
            return html.preview_redirect(redirect_authentication)

        # if auth with Okta succeeds it will redirect
        # to the callback view function
        return redirect(redirect_authentication.url)

    @okta_bp.route('/redirect-for-okta-logout')
    def redirect_for_okta_logout():
        """
        Logout redirect for Okta.
        """

    @okta_bp.route(okta_redirect_rule)
    def authorization_code_callback():
        """
        Check response from Okta and use access token to login a user.
        """
        # code and state from url query args
        code = request.args.get('code')
        state = request.args.get('state')
        # validate
        abort_for_callback(code, state)
        # backend exchange process for userinfo
        userinfo = exchange_for_userinfo(code, state)
        # callback to code using this extension for logging in user from
        # userinfo data
        okta = get_okta_extension()
        return okta.login_userinfo(userinfo)

    @okta_bp.route('/userinfo')
    def userinfo():
        """
        Debugging userinfo endpoint.
        """
        # guessing this is not normally presented to the user
        # trying to find where to get the id_token for the okta logout endpoint
        abort_for_debug()
        userinfo = authenticated_userinfo()
        return jsonify(userinfo)

    @okta_bp.route('/introspect')
    def introspect():
        """
        """
        abort_for_debug()

        url = current_app.config['OKTA_TOKEN_INTROSPECTION_URI']
        client_secret = current_app.config['OKTA_CLIENT_SECRET']
        client_id = current_app.config['OKTA_CLIENT_ID']

        response = requests.post(
            url,
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data = dict(
                client_id = client_id,
            ),
            auth = (
                client_id,
                client_secret,
            ),
        )
        response.raise_for_status()

        return jsonify(response.json())

    @okta_bp.route('/test-callback')
    def test_callback():
        """
        Debugging callback to display faked Okta callback redirect.
        """
        abort_for_debug()

        # NOTE
        # - the code key was just passed back in as is.
        code = request.args.get('code')
        state = request.args.get('state')
        abort_for_callback(code, state)
        return html.display_callback()
