import base64
import hashlib
import secrets
import string

def generate_code_verifier(n=128):
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    # https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
    alphabet = string.ascii_letters + string.punctuation
    code_verifier = ''.join(secrets.choice(alphabet) for _ in range(n))
    return code_verifier

def get_code_challenge(code_verifier):
    hash_ = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(hash_)
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    # oath/okta required changes to base 64 encoding
    # change + to -, / to _, and strip =
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    code_challenge = code_challenge.decode('ascii').rstrip('=')
    return code_challenge
