import base64
import hashlib
import secrets

# NOTE
# generate_code_verifier and generate_state_token are generated as url safe in
# Okta examples and there were problems not using url safe in development. If
# we wait, and make their values url safe when the url is created, we get
# different values in the session to compare to.
# nbytes was made 64 because Okta examples were.

def generate_code_verifier(nbytes=64):
    code_verifier = secrets.token_urlsafe(nbytes)
    return code_verifier

def generate_state_token(nbytes=64):
    state = secrets.token_urlsafe(nbytes)
    return state

def get_code_challenge(code_verifier):
    hash_ = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(hash_)
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    # oauth/okta required changes to base 64 encoding
    # change + to -, / to _, and strip =
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    code_challenge = code_challenge.decode('ascii').rstrip('=')
    return code_challenge
