import os


class base_config(object):
    try:
        SECRET_KEY = os.environ['SECRET_KEY']
    except Exception as e:
        pass
     
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'


class dev_config(base_config):
    DEBUG = True
    ASSETS_DEBUG = True
    WTF_CSRF_ENABLED = False


class test_config(base_config):
    TESTING = True
    WTF_CSRF_ENABLED = False
