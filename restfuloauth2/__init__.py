from flask import Flask
from flask_cors import CORS
from . import config
from database import db
from oauth import oauth, provider
from oauth.validator import RequestValidator
from flask_migrate import Migrate
from flask_restful import Api
from flasgger import Swagger
from dummy.endpoint import DummyIndex, DummyItem


def register_extensions(app):
    """Registers application extensions."""
    # Register and initialize the database.
    db.init_app(app)
    # Register and initialize the database migrations.
    Migrate(app, db)
    # Register Oauth2/REST provider.
    provider.init_app(app)
    provider._validator = RequestValidator()


def register_blueprints(app):
    """Registers application blueprints."""
    # Register OAuth2 blueprint.
    app.register_blueprint(oauth, url_prefix='/v1/oauth')
    # Register REST model endpoints.
    api = Api(app, decorators=[provider.require_oauth()])
    # Dummy REST endpoints.
    api.add_resource(DummyIndex, '/v1/dummy')
    api.add_resource(DummyItem, '/v1/dummy/<dummy_id>')
    # Register Swagger API docs.
    Swagger(
        app, config=app.config['SWAGGER_CONFIG'],
        template=app.config['SWAGGER_TEMPLATE'])


def create_app(config=config.BaseConfig):
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
