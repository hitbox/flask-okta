from .okta import authenticated_userinfo
from .okta import prepare_for_logout_redirect
from .view import create_okta_blueprint
from .wrappers import wrap_app_login_required
from .wrappers import wrap_view_functions

class OktaManager:
    """
    Authenticate Flask with Okta.
    """

    def __init__(
        self,
        app = None,
        after_authorization = None,
    ):
        self._after_authorization = after_authorization
        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app,
        after_authorization = None,
    ):
        """
        Redirect authentication for Flask and Okta.

        :param after_authorization:
            Callable receiving userinfo data from Okta. Taken from here,
            OktaManager initialization, or configuration, OKTA_LOGIN_USERINFO.
        """
        if 'okta' in app.extensions:
            raise RuntimeError('okta extension already registered.')

        app.extensions['okta'] = self

        # resolve func to call for login, after getting userinfo
        after_authorization = (
            after_authorization
            or
            self._after_authorization
            or
            app.config.get('OKTA_AFTER_AUTHORIZATION')
        )
        self._after_authorization = after_authorization

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

        okta_post_logout_redirect_rule = app.config.setdefault(
            'OKTA_POST_LOGOUT_REDIRECT_RULE',
            '/Account/PostLogout',
        )

        self.post_logout_redirect_rule = okta_post_logout_redirect_rule

        # a blueprint to handle redirecting to Okta and requesting data from
        # Okta on the backend.
        okta_bp = create_okta_blueprint(
            blueprint_name,
            app.name,
            okta_redirect_rule,
            okta_post_logout_redirect_rule,
        )
        app.register_blueprint(okta_bp)

    # convenient functions to extension instances

    wrap_view_functions = staticmethod(wrap_view_functions)

    wrap_app_login_required = staticmethod(wrap_app_login_required)

    def after_authorization(self, func):
        """
        Decorator to hook up callback for after Okta authorization.
        """
        self._after_authorization = func
        return func

    def userinfo(self):
        """
        Convenience function for extension instance to get Okta user info.
        """
        return authenticated_userinfo()

    def get_logout_obj(self, post_logout_redirect_uri=None):
        """
        Prepare session and return object with query params and url for
        redirect logout.

        :param post_logout_redirect_uri:
            See `flask_okta.prepare_for_logout_redirect`
        """
        logout_redirect = prepare_for_logout_redirect(
            post_logout_redirect_uri
        )
        return logout_redirect

    def logout_url(self, post_logout_redirect_uri=None):
        """
        Convenient function on extension to prepare session and contruct the
        url with arguments for logging out of Okta.
        """
        logout_redirect = self.get_logout_obj(post_logout_redirect_uri)
        return logout_redirect.url
