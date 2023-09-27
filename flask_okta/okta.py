import secrets

from urllib.parse import urlencode

from flask import current_app
from flask import session

from .oath import generate_code_verifier
from .oath import get_code_challenge

# Required Query Parameters:

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
#   - a value return in token for application use

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
    Prepare session and return object with url for redirect authentication.
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

    state = secrets.token_hex()
    code_verifier = generate_code_verifier()

    session['OKTA_STATE'] = state
    session['OKTA_CODE_VERIFIER'] = code_verifier

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
