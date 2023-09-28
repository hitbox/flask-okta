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

# https://developer.okta.com/docs/reference/api/oidc/#reserved-scopes
RESERVED_SCOPES = set([
    'openid',
    'profile',
    'email',
    'address',
    'phone',
    'offline_access',
    'groups',
])

class OktaRedirect:
    """
    Convenience object for redirect authentication.
    """

    def __init__(self, base_url, query):
        self.base_url = base_url
        self.query = query

    @property
    def url(self):
        """
        URL to Okta with query paramaters for redirect operations.
        """
        url = f'{ self.base_url }?{ urlencode(self.query) }'
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
    # validate scope
    scope_set = set(scope.split())
    assert 'openid' in scope_set, \
        'openid is required in scope.'
    unknown_scopes = scope_set.difference(RESERVED_SCOPES)
    assert not unknown_scopes, \
        f'Unknown scope values { unknown_scopes }.'
    # validate remaining:
    assert response_type == 'code', \
        'Only response type "code" supported.'
    assert response_mode == 'query', \
        'Only response mode "query" supported.'
    assert code_challenge_method == 'S256', \
        'Only code challenge method "S256" supported.'

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

    auth_uri = current_app.config['OKTA_AUTH_URI']
    redirect_authentication = OktaRedirect(auth_uri, query_params)
    return redirect_authentication

def prepare_for_logout_redirect(post_logout_redirect_uri=None):
    """
    Prepare session and object with url to logout user in Okta.
    """
    state = generate_state_token()

    session['_okta_state'] = state

    client_id = current_app.config['OKTA_CLIENT_ID']

    query_params = dict(
        id_token_hint = session['_okta_id_token'],
        state = state,
    )

    post_logout_redirect_uri = (
        post_logout_redirect_uri
        or
        current_app.config.get('OKTA_POST_LOGOUT_REDIRECT_URI')
    )
    if post_logout_redirect_uri:
        query_params['post_logout_redirect_uri'] = post_logout_redirect_uri

    logout_uri = current_app.config['OKTA_LOGOUT_URI']
    logout_redirect = OktaRedirect(logout_uri, query_params)
    return logout_redirect

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
    id_token = exchange['id_token']

    # docs don't show saving this anywhere but it is necessary for other endpoints
    session['_okta_access_token'] = access_token
    session['_okta_id_token'] = id_token

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
