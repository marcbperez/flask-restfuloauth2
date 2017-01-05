from flask import request
from flask_restful import abort, Resource
from . import Todo
from ..oauth.models import User


def get_todo_or_abort(todo_id, user):
    todo = Todo.get_permitted_todo(todo_id, user)
    if not todo:
        abort(404, message="Item not found")

    return todo


def operation_or_etag_not_matching(operation):
    if not operation:
        abort(401, message="Etags do not match")


def get_sort_attribute(sort):
    sort_column = sort.split('-')[0]
    sort_direction = sort.split('-')[1]
    sort_attribute = getattr(Todo, sort_column)
    return getattr(sort_attribute, sort_direction)()


class TodoItem(Resource):
    def get(self, todo_id):
        user = User.get_authorized()
        todo = get_todo_or_abort(todo_id, user)

        return todo.serialize()

    def delete(self, todo_id):
        user = User.get_authorized()
        todo = get_todo_or_abort(todo_id, user)
        args = Todo.parse_delete_arguments()
        delete = Todo.delete(todo, args['etag'])
        operation_or_etag_not_matching(delete)

        return '', 204

    def put(self, todo_id):
        user = User.get_authorized()
        todo = get_todo_or_abort(todo_id, user)
        args = Todo.parse_put_arguments()
        update = Todo.update(todo, args['etag'], args['public'],
            args['description'], args['done'])
        operation_or_etag_not_matching(update)

        return update.serialize(), 201


class TodoIndex(Resource):
    def get(self):
        page = request.args.get('page', '1')
        max_results = request.args.get('max_results', '10')
        sort = request.args.get('sort', 'id-asc')
        sort_direction = get_sort_attribute(sort)
        query = request.args.get('query', None)

        user = User.get_authorized()
        todos = Todo.get_permitted_todos(user, sort_direction, page,
            max_results, query)

        return Todo.serialize_list(todos)

    def post(self):
        user = User.get_authorized()
        args = Todo.parse_post_arguments()
        todo = Todo.create(user, args['public'], args['description'],
            args['done'])

        return todo.serialize(), 201
