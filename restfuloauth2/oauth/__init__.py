from flask import Blueprint
from flask_oauthlib.provider import OAuth2Provider


oauth = Blueprint(
    'oauth', __name__, template_folder='templates', static_folder='static')
"""OAuth2 provider blueprint."""

provider = OAuth2Provider()
"""OAuth2 provider."""

from . import views  # nopep8
