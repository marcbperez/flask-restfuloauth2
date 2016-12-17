from flask_restful import abort, Resource, reqparse
from . import Todo
from ..database import db


def get_todo_or_abort(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if not todo:
        abort(404, message="Todo {} doesn't exist".format(todo_id))
    return todo


def parse_todo_arguments():
    parser = reqparse.RequestParser()
    parser.add_argument('description', required=True, help='The todo description.')
    return parser.parse_args()


def serialize_todo(todo):
    return {
        'id': todo.id,
        'description': todo.description,
    }


def serialize_todos(todos):
    _todos = []
    for todo in todos:
        _todos.append(serialize_todo(todo))
    return _todos

class TodoItem(Resource):
    def get(self, todo_id):
        todo = get_todo_or_abort(todo_id)
        return serialize_todo(todo)

    def delete(self, todo_id):
        todo = get_todo_or_abort(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return '', 204

    def put(self, todo_id):
        todo = get_todo_or_abort(todo_id)
        args = parse_todo_arguments()
        todo.description = args['description']
        db.session.commit()
        return serialize_todo(todo), 201


class TodoIndex(Resource):
    def get(self):
        todos = Todo.query.all()
        return serialize_todos(todos)

    def post(self):
        args = parse_todo_arguments()
        todo = Todo()
        todo.description = args['description']
        db.session.add(todo)
        db.session.commit()
        return serialize_todo(todo), 201
