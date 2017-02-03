import os


class base_config(object):
    """Base configuration object."""
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'


class dev_config(base_config):
    """Development configuration object, extends base."""
    DEBUG = True
    ASSETS_DEBUG = True
    WTF_CSRF_ENABLED = False


class test_config(base_config):
    """Testing configuration objecet, extends base."""
    TESTING = True
    WTF_CSRF_ENABLED = False
