import secrets

from urllib.parse import urlencode

import requests

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask_login import login_user

from . import html
from .oath import generate_code_verifier
from .oath import get_code_challenge
from .user import OktaUser

# TODO
# - allow custom user class

def redirect_query(
    state,
    code_verifier,
    scope = 'openid email profile',
    response_type = 'code',
    response_mode = 'query',
    code_challenge_method = 'S256',
):
    """
    Create a dict of parameters required by Okta.

    :param state:
        random string for use by application.
    :param code_verifier:
        the cryptographically random string used to create the code challenge.
    """
    # NOTE
    # - leaving room for growth with kwargs but nothing else is supported yet.
    assert response_type == 'code', \
        'Only response type "code" supported.'
    assert response_mode == 'query', \
        'Only response mode "query" supported.'
    assert code_challenge_method == 'S256', \
        'Only code challenge method "S256" supported.'

    client_id = current_app.config['OKTA_CLIENT_ID']
    client_secret = current_app.config['OKTA_CLIENT_SECRET']
    redirect_uri = current_app.config['OKTA_REDIRECT_URI']

    code_challenge = get_code_challenge(code_verifier)

    query = dict(
        client_id = client_id,
        redirect_uri = redirect_uri,
        response_type = response_type,
        response_mode = response_mode,
        scope = scope,
        state = state,
        code_challenge = code_challenge,
        code_challenge_method = code_challenge_method,
    )
    return query

def get_okta_debug():
    return current_app.config.get('OKTA_DEBUG', False)

def abort_for_callback(code, state):
    """
    abort for invalid values from Okta.
    """
    if not code:
        abort(403, 'code not returned')

    if state != session['OKTA_STATE']:
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
    """

    @okta_bp.route('/login')
    def login():
        """
        Redirect to Okta for authentication using configured values.
        """
        state = secrets.token_hex()
        code_verifier = generate_code_verifier()

        session['OKTA_STATE'] = state
        session['OKTA_CODE_VERIFIER'] = code_verifier

        auth_uri = current_app.config['OKTA_AUTH_URI']
        query = redirect_query(state, code_verifier)
        url = f'{auth_uri}?{urlencode(query)}'

        if get_okta_debug():
            # debugging preview before redirect with link to continue
            return html.preview_redirect(auth_uri, query, url, code_verifier)

        return redirect(url)

    @okta_bp.route('/test-callback')
    def test_callback():
        """
        Debugging callback to display faked Okta callback redirect.
        """
        # abort for debugging not enabled
        if not get_okta_debug():
            abort(404)

        # NOTE
        # - the code key was just passed back in as is.
        code = request.args.get('code')
        state = request.args.get('state')
        abort_for_callback(code, state)
        return html.display_callback()

    @okta_bp.route(okta_redirect_rule)
    def authorization_code_callback():
        """
        Check response from Okta and use access token to login a user.
        """
        code = request.args.get('code')
        state = request.args.get('state')

        abort_for_callback(code, state)

        # post request for access token
        exchange_response = requests.post(
            current_app.config['OKTA_TOKEN_URI'],
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data = dict(
                grant_type = 'authorization_code',
                code = code,
                redirect_uri = request.base_url,
                code_verifier = session['OKTA_CODE_VERIFIER'],
            ),
            auth = (
                current_app.config['OKTA_CLIENT_ID'],
                current_app.config['OKTA_CLIENT_SECRET'],
            ),
        )
        exchange_response.raise_for_status()
        exchange = exchange_response.json()

        if not exchange.get('token_type'):
            abort(403, 'Unsupported token type.')

        # authorization successful
        access_token = exchange['access_token']

        userinfo_response = requests.get(
            current_app.config['OKTA_USERINFO_URI'],
            headers = {
                'Authorization': f'Bearer {access_token}',
            },
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        unique_id = userinfo['sub']
        user_email = userinfo['email']
        user_name = userinfo['given_name']

        user = OktaUser(
            id = unique_id,
            email = user_email,
            name = user_name,
        )
        user.update_session()

        login_user(user)

        # XXX
        # Okta probably provides a "next" argument? Or, one is passed through
        # from flask-login?
        okta = current_app.extensions['okta']
        url = url_for(okta.redirect_login_endpoint)
        return redirect(url)
