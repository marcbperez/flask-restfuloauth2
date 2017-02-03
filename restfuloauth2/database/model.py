from . import db
from .query import Query
from flask_restful import reqparse
from werkzeug.security import gen_salt
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.declarative import declared_attr


class Model(object):
    """Abstract implementation of the REST model."""

    id = db.Column(db.Integer, primary_key=True)
    etag = db.Column(db.String(40), unique=True)
    public = db.Column(db.Boolean())
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime())

    @declared_attr
    def user_id(cls):
        """The owner id."""
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    @declared_attr
    def user(cls):
        """The owner model"""
        return db.relationship('User')

    @classmethod
    def serialize(cls, model):
        """Returns the serialized version of this model."""
        return {
            'id': model.id,
            'etag': model.etag,
            'created': str(model.created),
            'updated': str(model.updated),
            'user_id': model.user_id,
            'public': model.public,
        }

    @classmethod
    def serialize_list(cls, models):
        """Returns the serialized version of a list of models."""
        serialized = []
        for model in models:
            serialized.append(model.serialize())

        return serialized

    @classmethod
    def add_parser_etag(cls, parser):
        """Adds etag to parser validation."""
        parser.add_argument('etag', required=True, help='Model etag.')

    @classmethod
    def add_parser_args(cls, parser):
        """Adds model parameters to parser validation."""
        parser.add_argument('public', required=True, help='Model visibility.')

    @classmethod
    def parse_post_arguments(cls, strict=True):
        """Adds validation for the post method."""
        parser = reqparse.RequestParser()
        cls.add_parser_args(parser)

        return parser.parse_args(strict=strict)

    @classmethod
    def parse_put_arguments(cls, strict=True):
        """Adds validation for the put method."""
        parser = reqparse.RequestParser()
        cls.add_parser_etag(parser)
        cls.add_parser_args(parser)

        return parser.parse_args(strict=strict)

    @classmethod
    def parse_delete_arguments(cls, strict=True):
        """Adds validation for the delete method."""
        parser = reqparse.RequestParser()
        cls.add_parser_etag(parser)

        return parser.parse_args(strict=strict)

    @classmethod
    def get_permitted(cls, id, user):
        """Returns an item if public or if the user is the owner."""
        return cls.query.filter(
            cls.id == id, ((cls.public) | (cls.user_id == user.id))).first()

    @classmethod
    def get_permitted_models(
            cls, user, sort_direction, page, max_results, search):
        """Returns a list of items if public or if the user is the owner."""
        models = cls.query.filter((cls.public) | (cls.user_id == user.id))
        # Generate and filter by text query if search contains JSON string.
        if search:
            text_search = Query.from_json_or_abort(search)
            models = models.filter(text(text_search))
        # Sort and paginate result.
        return models.order_by(sort_direction).paginate(
            int(page), int(max_results), error_out=False).items

    @classmethod
    def delete(cls, model, etag):
        """Deletes a model if the etag matches."""
        if model.etag != etag:
            return False

        db.session.delete(model)
        db.session.commit()

        return True

    @classmethod
    def update(cls, model, etag, public):
        """Updates a model if the etag matches."""
        if model.etag != etag:
            return False

        model.etag = gen_salt(40)
        model.updated = datetime.utcnow()
        model.public = public == '1'
        db.session.commit()

        return model

    @classmethod
    def create(cls, user, public):
        """Creates a model owned by the provided user."""
        model = cls()
        model.user_id = user.id
        model.etag = gen_salt(40)
        model.created = model.updated = datetime.utcnow()
        model.public = public == '1'
        db.session.add(model)
        db.session.commit()

        return model
