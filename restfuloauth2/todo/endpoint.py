from flask import request
from flask_restful import abort, Resource, reqparse
from . import Todo
from ..database import db
from ..oauth.models import Token, User


def get_todo_or_abort(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if not todo:
        abort(404, message="Todo {} doesn't exist".format(todo_id))
    return todo


def parse_todo_arguments():
    parser = reqparse.RequestParser()
    parser.add_argument('public', required=True, help='The todo visibility.')
    parser.add_argument('description', required=True, help='What to do.')
    parser.add_argument('done', required=True, help='If is completed or not.')
    return parser.parse_args(strict=True)


def serialize_todo(todo):
    return {
        'id': todo.id,
        'user_id': todo.user_id,
        'public': todo.public,
        'description': todo.description,
        'done': todo.done,
    }


def serialize_todos(todos):
    _todos = []
    for todo in todos:
        _todos.append(serialize_todo(todo))
    return _todos


def get_current_user():
    access_token = request.oauth.headers.get('Authorization').split(' ')[1]
    token = Token.find(access_token)
    return token.user


def is_permitted_or_abort(todo, user):
    if todo.public or (todo.user_id == user.id):
        return True
    abort(401, message="Unauthorized request")


class TodoItem(Resource):
    def get(self, todo_id):
        todo = get_todo_or_abort(todo_id)
        user = get_current_user()
        is_permitted_or_abort(todo, user)
        return serialize_todo(todo)

    def delete(self, todo_id):
        todo = get_todo_or_abort(todo_id)
        user = get_current_user()
        is_permitted_or_abort(todo, user)
        db.session.delete(todo)
        db.session.commit()
        return '', 204

    def put(self, todo_id):
        todo = get_todo_or_abort(todo_id)
        user = get_current_user()
        is_permitted_or_abort(todo, user)
        args = parse_todo_arguments()
        todo.public = args['public'] == '1'
        todo.description = args['description']
        todo.done = args['done'] == '1'
        db.session.commit()
        return serialize_todo(todo), 201


class TodoIndex(Resource):
    def get(self):
        max_results = request.args.get('max_results', '10')
        page = request.args.get('page', '1')
        sort_column = request.args.get('sort', 'id-asc').split('-')[0]
        sort_direction = request.args.get('sort', 'id-asc').split('-')[1]
        sort_attr = getattr(Todo, sort_column)
        sort_direction_attr = getattr(sort_attr, sort_direction)()
        todos = Todo.query.order_by(sort_direction_attr).paginate(int(page),
            int(max_results), error_out=False).items
        user = get_current_user()
        permitted_todos = []

        for todo in todos:
            if todo.public or (todo.user_id == user.id):
                permitted_todos.append(todo)

        return serialize_todos(permitted_todos)

    def post(self):
        todo = Todo()
        user = get_current_user()
        args = parse_todo_arguments()
        todo.user_id = user.id
        todo.public = args['public'] == '1'
        todo.description = args['description']
        todo.done = args['done'] == '1'
        db.session.add(todo)
        db.session.commit()
        return serialize_todo(todo), 201
