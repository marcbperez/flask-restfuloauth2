from flask import Blueprint
from flask_oauthlib.provider import OAuth2Provider

oauth = Blueprint('oauth', __name__, template_folder='templates',
    static_folder='static')

provider = OAuth2Provider()

from . import views
