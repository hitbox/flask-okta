from flask_login import LoginManager

from .user import OktaUser

def default_login_manager(
    blueprint_name,
    login_view,
    add_context_processor = True,
):
    login_manager = LoginManager(
        add_context_processor = add_context_processor,
    )

    @login_manager.user_loader
    def load_user(user_id):
        return OktaUser.get(user_id)

    login_manager.login_view = login_view

    return login_manager
