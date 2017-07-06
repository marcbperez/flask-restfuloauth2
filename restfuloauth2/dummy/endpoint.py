from . import Dummy
from ..oauth.models import User
from ..database.query import Query
from flask import request
from flask_restful import abort, Resource
from flasgger import swag_from


class DummyItem(Resource):
    """Dummy model item endpoint."""

    @swag_from('item_get.yml')
    def get(self, dummy_id):
        """Gets a model given its id and outputs the serialized version."""
        user = User.get_authorized()
        dummy = Query.get_item_or_abort(Dummy, dummy_id, user)

        return dummy.serialize()

    @swag_from('item_delete.yml')
    def delete(self, dummy_id):
        """Deletes a model given its id."""
        user = User.get_authorized()
        dummy = Query.get_item_or_abort(Dummy, dummy_id, user)
        args = Dummy.parse_delete_arguments()
        delete = Dummy.delete(dummy, args['etag'])

        if not delete:
            abort(401, message=Query.ETAG_NOT_MATCHING)

        return '', 204

    @swag_from('item_put.yml')
    def put(self, dummy_id):
        """Updates a model given its id and outputs the serialized version."""
        user = User.get_authorized()
        dummy = Query.get_item_or_abort(Dummy, dummy_id, user)
        args = Dummy.parse_put_arguments()
        update = Dummy.update(dummy, args['etag'], args['public'])

        if not update:
            abort(401, message=Query.ETAG_NOT_MATCHING)

        return update.serialize(), 201


class DummyIndex(Resource):
    """Dummy model index endpoint."""

    @swag_from('index_get.yml')
    def get(self):
        """Outputs a serialized, paginated collection of models."""
        page = request.args.get('page', Query.DEFAULT_PAGE)
        max_results = request.args.get(
            'max_results', Query.DEFAULT_MAX_RESULTS)
        sort = request.args.get('sort', Query.DEFAULT_SORT)
        sort_direction = Query.get_sort_attribute(Dummy, sort)
        search = request.args.get('search', Query.DEFAULT_SEARCH)

        user = User.get_authorized()
        dummies = Dummy.get_permitted_models(
            user, sort_direction, page, max_results, search)

        return Dummy.serialize_list(dummies)

    @swag_from('index_post.yml')
    def post(self):
        """Adds a model to the colletion and outputs the serialized version."""
        user = User.get_authorized()
        args = Dummy.parse_post_arguments()
        dummy = Dummy.create(user, args['public'])

        return dummy.serialize(), 201
