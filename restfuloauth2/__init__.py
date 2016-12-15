from flask import Flask, redirect, url_for
from . import config
from database import db
from oauth import provider
from oauth.validator import RequestValidator
from oauth import oauth
from flask_restful import Api
from todo.endpoint import TodoIndex, TodoItem


def register_extensions(app):
    db.init_app(app)
    provider.init_app(app)
    provider._validator = RequestValidator()


def register_blueprints(app):
    app.register_blueprint(oauth, url_prefix='/oauth')

    api = Api(app, decorators=[provider.require_oauth()])
    api.add_resource(TodoIndex, '/todo')
    api.add_resource(TodoItem, '/todo/<todo_id>')


def create_app(config=config.base_config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    db.create_all(app=app)

    return app


app = create_app()


@app.route('/')
def default():
    return redirect(url_for('oauth.management'))
