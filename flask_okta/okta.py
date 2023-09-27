import secrets

from urllib.parse import urlencode

import requests

from flask import abort
from flask import current_app
from flask import request
from flask import session

from .oauth import generate_code_verifier
from .oauth import generate_state_token
from .oauth import get_code_challenge

# Required Query Parameters for /authenticate:

# - client_id
# - redirect_uri
# - response_type
#   - space separated list
#   - Any combination of code, token, id_token, or none.
# - scope
#   - space separated list
#   - "openid" is required
#   - profile, email, address, phone, offline_access, groups
# - state
#   - a value returned in token for application use

class RedirectAuthentication:
    """
    Convenience object for redirect authentication.
    """

    def __init__(self, query):
        self.query = query

    @property
    def url(self):
        """
        URL to Okta with query paramaters for redirect authentication.
        """
        auth_uri = current_app.config['OKTA_AUTH_URI']
        url = f'{ auth_uri }?{ urlencode(self.query) }'
        return url


def prepare_redirect_authentication(
    scope = 'openid email profile',
    response_type = 'code',
    response_mode = 'query',
    code_challenge_method = 'S256',
):
    """
    Prepare session and return object with url for redirect authentication with
    query parameters.
    """
    # NOTE
    # - leaving room for growth with kwargs but nothing else is supported yet.
    assert response_type == 'code', \
        'Only response type "code" supported.'
    assert response_mode == 'query', \
        'Only response mode "query" supported.'
    assert code_challenge_method == 'S256', \
        'Only code challenge method "S256" supported.'
    assert 'openid' in scope.split(), \
        '"openid" is required in scope list.'

    state = generate_state_token()
    code_verifier = generate_code_verifier()

    session['_okta_state'] = state
    session['_okta_code_verifier'] = code_verifier

    client_id = current_app.config['OKTA_CLIENT_ID']
    client_secret = current_app.config['OKTA_CLIENT_SECRET']
    redirect_uri = current_app.config['OKTA_REDIRECT_URI']

    code_challenge = get_code_challenge(code_verifier)

    query_params = dict(
        client_id = client_id,
        redirect_uri = redirect_uri,
        response_type = response_type,
        response_mode = response_mode,
        scope = scope,
        state = state,
        code_challenge = code_challenge,
        code_challenge_method = code_challenge_method,
    )

    redirect_authentication = RedirectAuthentication(query_params)
    return redirect_authentication

def post_for_access_code(code, state):
    """
    post request for access code after return from redirect authentication.
    """
    exchange_response = requests.post(
        current_app.config['OKTA_TOKEN_URI'],
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data = dict(
            grant_type = 'authorization_code',
            code = code,
            redirect_uri = request.base_url,
            code_verifier = session['_okta_code_verifier'],
        ),
        auth = (
            current_app.config['OKTA_CLIENT_ID'],
            current_app.config['OKTA_CLIENT_SECRET'],
        ),
    )
    exchange_response.raise_for_status()
    exchange = exchange_response.json()
    return exchange

def exchange_for_userinfo(code, state):
    """
    Post for access code and use it to get userinfo data.
    """
    # post request for access token
    exchange = post_for_access_code(code, state)

    if not exchange.get('token_type'):
        abort(403, 'Unsupported token type.')

    # authorization successful
    access_token = exchange['access_token']

    # docs don't show saving this anywhere but it is necessary for other endpoints
    session['_okta_access_token'] = access_token

    userinfo_response = requests.get(
        current_app.config['OKTA_USERINFO_URI'],
        headers = {
            'Authorization': f'Bearer {access_token}',
        },
    )
    userinfo_response.raise_for_status()

    userinfo = userinfo_response.json()
    return userinfo

def authenticated_userinfo():
    """
    User information from /userinfo for current authenticated user.
    """
    access_token = session['_okta_access_token']
    userinfo_response = requests.get(
        current_app.config['OKTA_USERINFO_URI'],
        headers = {
            'Authorization': f'Bearer {access_token}',
        },
    )
    userinfo_response.raise_for_status()
    userinfo = userinfo_response.json()
    return userinfo
