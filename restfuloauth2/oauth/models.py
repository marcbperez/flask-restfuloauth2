from flask import request
from datetime import datetime, timedelta
from werkzeug.security import gen_salt
from ..database import db
import bcrypt


class User(db.Model):
    """The OAuth2 provider and general application user."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    hashpw = db.Column(db.String(80))

    @staticmethod
    def find_with_password(username, password, *args, **kwargs):
        """Finds a user given his username and plain password."""
        user = User.query.filter_by(username=username).first()
        encodedpw = password.encode('utf-8')
        userhash = user.hashpw.encode('utf-8')
        return User.query.filter(
            User.username == username,
            User.hashpw == bcrypt.hashpw(encodedpw, userhash)
        ).first()

    @staticmethod
    def save(username, password):
        """Finds a user given his username and plain password."""
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        user = User(username=username, hashpw=hash)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def all():
        """Returns all users."""
        return User.query.all()

    @staticmethod
    def get_authorized():
        """Returns the currently authorized user."""
        access_token = request.oauth.headers.get('Authorization').split(' ')[1]
        token = Token.find(access_token)
        return token.user


class Client(db.Model):
    """The OAuth2 application client."""

    client_id = db.Column(db.String(40), primary_key=True)
    client_type = db.Column(db.String(40))

    @property
    def allowed_grant_types(self):
        """Default client grant types."""
        return ['password']

    @property
    def default_scopes(self):
        """Default client scopes."""
        return []

    @staticmethod
    def find(id):
        """Finds a client by its id."""
        return Client.query.filter_by(client_id=id).first()

    @staticmethod
    def generate():
        """Generates a new public client."""
        client = Client(client_id=gen_salt(40), client_type='public')
        db.session.add(client)
        db.session.commit()

    @staticmethod
    def all():
        """Returns all clients."""
        return Client.query.all()

    def default_redirect_uri():  # pragma: no cover
        """Returns the default redirect URI."""
        return ''


class Token(db.Model):
    """The OAuth2 client token."""

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship('Client')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    scopes = ['']

    @staticmethod
    def all():
        """Returns all tokens."""
        return Token.query.all()

    @staticmethod
    def find(access_token):
        """Finds an access token given its identifier."""
        return Token.query.filter_by(access_token=access_token).first()

    @staticmethod
    def save(token, request, *args, **kwargs):
        """Creates a new token per client and user."""
        toks = Token.query.filter_by(
            client_id=request.client.client_id, user_id=request.user.id)

        # Make sure there is only one token for every client and user.
        [db.session.delete(t) for t in toks]

        expires_in = token.pop('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        tok = Token(
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            token_type=token['token_type'],
            expires=expires,
            client_id=request.client.client_id,
            user_id=request.user.id,
        )

        db.session.add(tok)
        db.session.commit()
