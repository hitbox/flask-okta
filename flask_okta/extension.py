from .okta import authenticated_userinfo
from .okta import prepare_for_logout_redirect
from .view import create_okta_blueprint

class OktaManager:
    """
    Authenticate Flask with Okta.
    """

    def __init__(
        self,
        app = None,
        login_userinfo = None,
        wrap_existing_views = False, # TODO!
    ):
        self.login_userinfo = login_userinfo
        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app,
        login_userinfo = None,
    ):
        """
        Redirect authentication for Flask and Okta.

        :param login_userinfo:
            Callable receiving userinfo data from Okta. Taken from here,
            OktaManager initialization, or configuration, OKTA_LOGIN_USERINFO.
        """
        if 'okta' in app.extensions:
            raise RuntimeError('okta extension already registered.')

        app.extensions['okta'] = self

        # resolve func to call for login, after getting userinfo
        login_userinfo = (
            login_userinfo
            or
            self.login_userinfo
            or
            app.config.get('OKTA_LOGIN_USERINFO')
        )
        self.login_userinfo = login_userinfo

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

        # a blueprint to handle redirecting to Okta and requesting data from
        # Okta on the backend.
        okta_bp = create_okta_blueprint(
            blueprint_name,
            app.name,
            okta_redirect_rule,
        )
        app.register_blueprint(okta_bp)

    def userinfo(self):
        """
        Convenience function for extension instance.
        """
        return authenticated_userinfo()

    def get_logout_obj(self, post_logout_redirect_uri=None):
        """
        Prepare session and return object with query params and url for
        redirect logout.
        """
        redirect_authentication = prepare_for_logout_redirect(
            post_logout_redirect_uri
        )
        return redirect_authentication


class DashOktaManager(OktaManager):
    """
    Dash specific Flask-Okta extension that by default adds
    `login_manager.login_required` to existing view functions.
    """
    # TODO
