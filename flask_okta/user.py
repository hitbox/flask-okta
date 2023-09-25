from flask import session
from flask_login import UserMixin

class OktaUser(UserMixin):

    def get_from_session(self, user_id):
        if 'OKTA_USERS' not in session:
            session['OKTA_USERS'] = {}
        return session['OKTA_USERS'].get(user_id)
