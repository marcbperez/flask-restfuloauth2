from ..database import db
from ..oauth.models import User
from flask_restful import reqparse, abort
from werkzeug.security import gen_salt
from datetime import datetime
from sqlalchemy import text
import json


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etag = db.Column(db.String(40), unique=True)
    public = db.Column(db.Boolean())
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    description = db.Column(db.String(150))
    done = db.Column(db.Boolean())

    def serialize(self):
        return {
            'id': self.id,
            'etag': self.etag,
            'created': str(self.created),
            'updated': str(self.updated),
            'user_id': self.user_id,
            'public': self.public,
            'description': self.description,
            'done': self.done,
        }

    @staticmethod
    def serialize_list(todos):
        serialized = []
        for todo in todos:
            serialized.append(todo.serialize())

        return serialized

    @staticmethod
    def add_parser_etag(parser):
        parser.add_argument('etag', required=True, help='The todo etag.')

    @staticmethod
    def add_parser_args(parser):
        parser.add_argument('public', required=True, help='The todo visibility.')
        parser.add_argument('description', required=True, help='What to do.')
        parser.add_argument('done', required=True, help='If completed or not.')

    @staticmethod
    def parse_post_arguments(strict=True):
        parser = reqparse.RequestParser()
        Todo.add_parser_args(parser)

        return parser.parse_args(strict=strict)

    @staticmethod
    def parse_put_arguments(strict=True):
        parser = reqparse.RequestParser()
        Todo.add_parser_etag(parser)
        Todo.add_parser_args(parser)

        return parser.parse_args(strict=strict)

    @staticmethod
    def parse_delete_arguments(strict=True):
        parser = reqparse.RequestParser()
        Todo.add_parser_etag(parser)

        return parser.parse_args(strict=strict)

    @staticmethod
    def get_permitted_todo(todo_id, user):
        return Todo.query.filter(Todo.id == todo_id, ((Todo.public) |
            (Todo.user_id == user.id))).first()

    @staticmethod
    def get_permitted_todos(user, sort_direction, page, max_results, query):
        items = Todo.query.filter((Todo.public) | (Todo.user_id == user.id))

        if query:
            text_query = Todo.query_from_json(json.loads(query))
            items.filter(text(text_query))

        return items.order_by(sort_direction).paginate(int(page), \
            int(max_results), error_out=False).items

    @staticmethod
    def valid_condition_operator(operator):
        return operator in ['and', 'or']

    @staticmethod
    def valid_column_operator(operator):
        return operator in ['=', '!=', '<', '<=', '>', '>=', 'like']

    @staticmethod
    def query_from_json(data):
        if 'column' in data and 'operator' in data and 'value' in data:
            if not Todo.valid_column_operator(data['operator']):
                abort(401, message="Invalid operator")
            return data['column'] + data['operator'] + str(data['value'])

        elif 'conditions' in data and 'operator' in data:
            if not Todo.valid_condition_operator(data['operator']):
                abort(401, message="Invalid operator")
            if isinstance(data['conditions'], list):
                query = '('

                for i, condition in enumerate(data['conditions']):
                    query += Todo.query_from_json(condition)
                    if len(data['conditions']) > 1 and i != \
                        len(data['conditions'])-1:
                        query += ' ' + data['operator'] + ' '

                query += ')'
                return query

    @staticmethod
    def delete(todo, etag):
        if todo.etag != etag:
            return False

        db.session.delete(todo)
        db.session.commit()

        return True

    @staticmethod
    def update(todo, etag, public, description, done):
        if todo.etag != etag:
            return False

        todo.etag = gen_salt(40)
        todo.updated = datetime.utcnow()
        todo.public = public == '1'
        todo.description = description
        todo.done = done == '1'

        db.session.commit()
        return todo

    @staticmethod
    def create(user, public, description, done):
        todo = Todo()
        todo.user_id = user.id
        todo.etag = gen_salt(40)
        todo.created = todo.updated = datetime.utcnow()
        todo.public = public == '1'
        todo.description = description
        todo.done = done == '1'

        db.session.add(todo)
        db.session.commit()
        return todo
