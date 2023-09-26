from flask import current_app
from flask import request
from flask import url_for
from markupsafe import Markup

def preview_redirect(auth_uri, query, url, code_verifier):
    """
    Debugging html preview before auth request.
    """
    html = []

    # styling
    html.append('<style>')
    html.append('dd code {')
    html.append('  padding: 4px;')
    html.append('  line-height: 1.25rem;')
    html.append('}')
    html.append('</style>')

    html.append('<h1>Okta Debugging Mode On</h1>')
    html.append('<h2>Preview Redirect</h2>')

    # link to redirect url
    html.append(f'<p><a href="{ url }">Continue to Okta</a></p>')

    test_callback_url = url_for('.test_callback', code=code_verifier, **query)
    html.append(f'<p><a href="{ test_callback_url }">Test callback</a></p>')

    # link to introspection
    introspect_url = current_app.config.get('OKTA_TOKEN_INTROSPECTION_URI')
    if introspect_url:
        html.append(
            f'''<p><a href="{ introspect_url }">Introspect</a></p>'''
        )
    else:
        html.append(
            '<p>Set <code>OKTA_TOKEN_INTROSPECTION_URI</code>'
            ' for link to introspection.</p>'
        )

    # display data
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

    return Markup(''.join(html))

def display_callback():
    """
    Debugging page to show fake response from Okta.
    """
    html = []
    html.append('<h1>Okta Debugging Mode On</h1>')
    html.append('<h2>Success!</h2>')
    html.append('<p>Passed code and state checks.</p>')

    html.append('<dl>')
    for key, value in request.args.items():
        html.append(f'<dt><code>{ key }</code></dt>')
        html.append(f'<dd><code>{ value }</code></dd>')
    html.append('</dl>')

    return Markup(''.join(html))
