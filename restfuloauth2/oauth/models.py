from flask import request
from datetime import datetime, timedelta
from werkzeug.security import gen_salt
from ..database import db
import bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    hashpw = db.Column(db.String(80))

    @staticmethod
    def find_with_password(username, password, *args, **kwargs):
        user = User.query.filter_by(username=username).first()
        if user and password:
            encodedpw = password.encode('utf-8')
            userhash = user.hashpw.encode('utf-8')
            return User.query.filter(
                User.username == username,
                User.hashpw == bcrypt.hashpw(encodedpw, userhash)
            ).first()
        else:
            return user

    @staticmethod
    def save(username, password):
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        user = User(username=username, hashpw=hash)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def all():
        return User.query.all()

    @staticmethod
    def get_authorized():
        access_token = request.oauth.headers.get('Authorization').split(' ')[1]
        token = Token.find(access_token)
        return token.user

class Client(db.Model):
    client_id = db.Column(db.String(40), primary_key=True)
    client_type = db.Column(db.String(40))

    @property
    def allowed_grant_types(self):
        return ['password']

    @property
    def default_scopes(self):
        return []

    @staticmethod
    def find(id):
        return Client.query.filter_by(client_id=id).first()

    @staticmethod
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @staticmethod
    def generate():
        client = Client(client_id=gen_salt(40), client_type='public')
        db.session.add(client)
        db.session.commit()

    @staticmethod
    def all():
        return Client.query.all()

    def default_redirect_uri():
        return ''


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(40), db.ForeignKey('client.client_id'),
        nullable=False)
    client = db.relationship('Client')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    scopes = ['']

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def all():
        return Token.query.all()

    @staticmethod
    def find(access_token=None, refresh_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        elif refresh_token:
            return Token.query.filter_by(refresh_token=refresh_token).first()

    @staticmethod
    def save(token, request, *args, **kwargs):
        toks = Token.query.filter_by(
            client_id=request.client.client_id,
            user_id=request.user.id)

        # Make sure there is only one grant token for every client and user.
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
