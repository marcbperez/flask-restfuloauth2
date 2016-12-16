from flask_oauthlib.provider import OAuth2RequestValidator
from flask_oauthlib.utils import decode_base64
from oauthlib.common import to_unicode
from models import User, Client, Token


class RequestValidator(OAuth2RequestValidator):
    def __init__(self):
        self._clientgetter = Client.find
        self._usergetter = User.find_with_password
        self._tokengetter = Token.find
        self._tokensetter = Token.save

    def authenticate_client(self, request, *args, **kwargs):
        auth = request.headers.get('Authorization', None)

        if auth:
            try:
                _, s = auth.split(' ')
                client_id, client_secret = decode_base64(s).split(':')
                client_id = to_unicode(client_id, 'utf-8')
            except Exception as e:
                return False
        else:
            client_id = request.client_id

        client = self._clientgetter(client_id)

        if not client:
            return False

        if client.client_type == 'public':
            return self.authenticate_client_id(client_id, request)
        else:
            return OAuth2RequestValidator.authenticate_client(
                self, request, *args, **kwargs)
