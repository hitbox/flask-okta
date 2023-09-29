from flask_login import login_required

def wrap_view_functions(flask_app, wrapper):
    """
    Wrap the view functions of a flask instance.
    """
    view_functions = flask_app.view_functions
    for endpoint in list(view_functions):
        func = view_functions[endpoint]
        view_functions[endpoint] = wrapper(func)

def wrap_app_login_required(flask_app):
    """
    Wrap existing Flask view function with login_required. Usually for
    initialized Dash application with existing Flask instance.
    """
    wrap_view_functions(flask_app, login_required)
