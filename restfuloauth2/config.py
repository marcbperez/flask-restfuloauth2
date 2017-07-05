import os


class BaseConfig(object):
    """Base configuration object."""
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SWAGGER = {
        'title': 'RestfulOauth2 Service API documentation',
        'uiversion': 3,
    }

    SWAGGER_TEMPLATE = {
        'info': {
            'title': 'RestfulOauth2',
            'description': 'Service API documentation',
            'version': '0.1.2',
        },
        'basePath': '/',
    }

    SWAGGER_CONFIG = {
        'headers': [],
        'specs': [
            {
                'endpoint': 'RestfulOauth2',
                'route': '/',
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/api/',
    }
