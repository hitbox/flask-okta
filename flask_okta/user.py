from flask import session
from flask_login import UserMixin

class OktaUser(UserMixin):

    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

    @staticmethod
    def get_from_session(user_id):
        if 'OKTA_USERS' not in session:
            session['OKTA_USERS'] = {}
        return session['OKTA_USERS'].get(user_id)

    def update_session(self):
        """
        Add this User instance to session.
        """
        if 'OKTA_USERS' not in session:
            session['OKTA_USERS'] = {}
        session['OKTA_USERS'][self.id] = self
