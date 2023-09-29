from flask import current_app

from flask import request
from flask import session
from flask import url_for
from markupsafe import Markup
from markupsafe import escape

def preview_redirect(redirect_authentication):
    """
    Debugging html preview before auth request.
    """
    # begin html list and styling
    html = ['<style>']
    html.extend(dd_code_style())
    html.extend(nav_style())
    html.append('</style>')

    html.append(flask_okta_debugging_header())
    html.append('<h2>Preview Redirect</h2>')

    # link to test callback to bypass Okta for development
    test_callback_url = url_for(
        '.test_callback',
        code = session['_okta_code_verifier'],
        **redirect_authentication.query,
    )

    html.append(
        tag('nav',
            ''.join([
                tag('a',
                    'Continue to Okta',
                    href = redirect_authentication.url,
                    title = 'Signin with Okta and redirect back here.',
                ),
                tag('a',
                    'Test callback',
                    href = test_callback_url,
                    title = 'Bypass Okta for debugging.',
                ),
            ])))

    # display data
    items_list = [
        ('auth_uri', current_app.config['OKTA_AUTH_URI']),
        ('url', redirect_authentication.url),
    ]
    items_list += redirect_authentication.query.items()
    html.extend(dl_for_code(items_list))
    return Markup(''.join(html))

def display_callback():
    """
    Debugging page to show fake response from Okta.
    """
    html = ['<style>']
    html.extend(dd_code_style())
    html.append('</style>')

    html.append(flask_okta_debugging_header())
    html.append('<h2>Success!</h2>')
    html.append('<p>Passed code and state checks.</p>')
    html.extend(dl_for_code(request.args.items()))
    return Markup(''.join(html))

def flask_okta_debugging_header():
    return '<h1>Flask-Okta Debugging Mode On</h1>'

def clean_key(key):
    key = key.rstrip('_')
    if key.startswith(('data_', 'aria_')):
        key = key.replace('_', '-')
    return key

def html_attrs(attributes):
    attrs = []
    for key, value in attributes.items():
        if value is False:
            continue
        key = clean_key(key)
        if value is True:
            attrs.append(key)
        else:
            attrs.append(f'{ key }="{ escape(value) }"')
    return ' '.join(attrs)

def tag(tag_name, _inner=None, **attributes):
    s = f'<{ tag_name }'
    if attributes:
        s += ' '
        s += html_attrs(attributes)
    s += '>'
    if _inner:
        s += str(_inner)
    s += f'</{ tag_name }>'
    return s

def dl_for_code(items):
    html = ['<dl>']
    for key, value in items:
        html.append(f'<dt><code>{ key }</code></dt>')
        html.append(f'<dd><code>{ value }</code></dd>')
    html.append('</dl>')
    return html

def dd_code_style():
    html = ['dd code {']
    html.append('  padding: 4px;')
    html.append('  line-height: 1.25rem;')
    html.append('}')
    return html

def nav_style():
    html = ['nav {']
    html.append('  display: flex;')
    html.append('  justify-content: space-between;')
    html.append('  width: min-content;')
    html.append('}')
    html.append('nav a {')
    html.append('  white-space: nowrap;')
    html.append('}')
    html.append('nav a + a {')
    html.append('  margin-left: 1rem;')
    html.append('}')
    return html
