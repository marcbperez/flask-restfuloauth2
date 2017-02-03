from flask import Flask, redirect, url_for
from flask_cors import CORS, cross_origin
from . import config
from database import db
from oauth import provider
from oauth.validator import RequestValidator
from oauth import oauth
from flask_restful import Api
from dummy.endpoint import DummyIndex, DummyItem


def register_extensions(app):
    """Registers application extensions."""
    # Register and initialize the database.
    db.init_app(app)
    db.create_all(app=app)
    # Register Oauth2/REST provider.
    provider.init_app(app)
    provider._validator = RequestValidator()


def register_blueprints(app):
    """Registers application blueprints."""
    # Register OAuth2 blueprint.
    app.register_blueprint(oauth, url_prefix='/v1/oauth')
    # Register REST model endpoints.
    api = Api(app, decorators=[provider.require_oauth()])
    api.add_resource(DummyIndex, '/v1/dummy')
    api.add_resource(DummyItem, '/v1/dummy/<dummy_id>')


def create_app(config=config.base_config):
    """Configure and return the main app."""
    app = Flask(__name__)
    # Setup with the provided configuration object.
    app.config.from_object(config)
    # Register extensions and blueprints.
    register_extensions(app)
    register_blueprints(app)
    # Apply CORS to app.
    CORS(app)

    return app


app = create_app()
"""Main program app."""


@app.route('/')
def default():
    """Default route, redirects to management module."""
    return redirect(url_for('oauth.management'))
