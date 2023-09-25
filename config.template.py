# Usually put in instance folder, outside of source control.
SECRET_KEY = 'Result of secrets.token_hex()'

# flask-okta settings
# work in progress
OKTA_CLIENT_ID = 'client id from Okta'
OKTA_CLIENT_SECRET = 'client secrect from Okta'

okta_domain = 'Okta domain'
redirect_domain = 'app domain'

# 
OKTA_AUTH_URI = f'https://{okta_domain}/oauth2/default/v1/authorize'

# should be able to build this with `url_for`
OKTA_REDIRECT_URI = f'http://{redirect_domain}/authorization-code/callback'

#OKTA_ISSUER = f'https://{okta_domain}/oauth2/default'
#OKTA_TOKEN_URI = f'https://{okta_domain}/oauth2/default/v1/token'
#OKTA_TOKEN_INTROSPECTION_URI = f'https://{okta_domain}/oauth2/default/v1/introspect'
#OKTA_USERINFO_URI = f'https://{okta_domain}/oauth2/default/v1/userinfo'

# OKTA_DEBUG
# Preview before redirect to Okta
# Default False
OKTA_DEBUG = True

