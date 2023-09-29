import base64
import hashlib
import secrets

# NOTE
# generate_code_verifier and generate_state_token are generated as url safe in
# Okta examples and there were problems not using url safe in development. If
# we wait, and make their values url safe when the url is created, we get
# different values in the session to compare to, and the checks fail.

# nbytes was made 64 because Okta examples were.
DEFAULT_NBYTES = 64

def generate_code_verifier(nbytes=DEFAULT_NBYTES):
    """
    Value checked by Okta and the application.
    """
    code_verifier = secrets.token_urlsafe(nbytes)
    return code_verifier

def generate_state_token(nbytes=DEFAULT_NBYTES):
    """
    Pass-through app state value for use by client application.
    """
    state = secrets.token_urlsafe(nbytes)
    return state

def get_code_challenge(code_verifier):
    """
    :param code_verifier:
        Value that is specially hashed and checked by server and client.
    """
    hash_ = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(hash_)
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    # oauth/okta required changes to base 64 encoding
    # change + to -, / to _, and strip trailing =
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    code_challenge = code_challenge.decode('ascii').rstrip('=')
    return code_challenge
