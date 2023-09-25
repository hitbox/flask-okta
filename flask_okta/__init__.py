from .login import default_login_manager
from .view import create_okta_blueprint

class OktaManager:
    """
    Authenticate Flask with Okta.
    """

    def __init__(
        self,
        app = None,
        login_manager = None,
        wrap_existing_views = False, # TODO!
    ):
        if app is not None:
            self.init_app(app, login_manager)

    def init_app(self, app, login_manager=None):
        if 'okta' in app.extensions:
            raise RuntimeError('okta extension already registered.')

        app.extensions['okta'] = self

        blueprint_name = app.config.setdefault(
            'OKTA_BLUEPRINT_NAME',
            'okta'
        )

        blueprint_url_prefix = app.config.setdefault(
            'OKTA_BLUEPRINT_URL_PREFIX',
            '/okta'
        )

        okta_redirect_rule = app.config.setdefault(
            'OKTA_REDIRECT_RULE',
            '/authorization-code/callback'
        )

        if login_manager is None:
            login_manager = default_login_manager(
                blueprint_name,
                login_view = f'{blueprint_name}.login',
            )
            login_manager.init_app(app)

        okta_bp = create_okta_blueprint(
            blueprint_name,
            app.name,
            okta_redirect_rule,
        )
        app.register_blueprint(okta_bp)


class DashOktaManager(OktaManager):
    # TODO
    pass
