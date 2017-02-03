from ..database import db
from ..database.model import Model


class Dummy(db.Model, Model):
    """Minimal implementation of a REST model."""

    __tablename__ = 'dummy'

    def serialize(self):
        """Returns the serialized version of this model."""
        return Model.serialize(self)
