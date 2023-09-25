from urllib.parse import urlencode

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for
from markupsafe import Markup

def query_from_config():
    client_id = current_app.config['OKTA_CLIENT_ID']
    client_secret = current_app.config['OKTA_CLIENT_SECRET']
    redirect_uri = current_app.config['OKTA_REDIRECT_URI']
    query = dict(
        client_id = client_id,
        redirect_uri = redirect_uri,
        response_type = 'code',
        response_mode = 'query',
    )
    return query

def preview_redirect_html(auth_uri, query, url):
    html = []

    # styling
    html.append('<style>')
    html.append('dd code {')
    html.append('  padding: 4px;')
    html.append('  line-height: 1.25rem;')
    html.append('}')
    html.append('</style>')

    html.append('<h1>Okta Debug</h1>')
    html.append('<h2>Preview Redirect</h2>')

    items_list = [
        ('auth_uri', auth_uri),
        ('url', url),
    ]
    items_list += query.items()

    html.append('<dl>')
    for key, value in items_list:
        html.append(f'<dt><code>{ key }</code></dt>')
        html.append(f'<dd><code>{ value }</code></dd>')
    html.append('</dl>')

    # link to redirect url
    html.append(f'<a href="{ url }">Continue to Okta</a>')
    return Markup(''.join(html))

def create_okta_blueprint(
    blueprint_name,
    import_name,
    okta_redirect_rule,
):
    """
    """
    okta_bp = Blueprint(
        name = blueprint_name,
        import_name = import_name,
    )

    @okta_bp.route('/login')
    def login():
        """
        Redirect to Okta for authentication using configured values.
        """
        auth_uri = current_app.config['OKTA_AUTH_URI']
        query = query_from_config()
        url = f'{auth_uri}?{urlencode(query)}'

        if current_app.config.get('OKTA_DEBUG', False):
            # debugging preview before redirect with link to continue
            return preview_redirect_html(auth_uri, query, url)

        return redirect(url)

    @okta_bp.route(okta_redirect_rule)
    def authorization_code_callback():
        return str(request)

    return okta_bp
