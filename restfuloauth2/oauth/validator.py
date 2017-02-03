from flask_oauthlib.provider import OAuth2RequestValidator
from flask_oauthlib.utils import decode_base64
from oauthlib.common import to_unicode
from models import User, Client, Token


class RequestValidator(OAuth2RequestValidator):
    """Validates the OAuth2 request by getting the client, user and token."""

    def __init__(self):
        self._clientgetter = Client.find
        self._usergetter = User.find_with_password
        self._tokengetter = Token.find
        self._tokensetter = Token.save
