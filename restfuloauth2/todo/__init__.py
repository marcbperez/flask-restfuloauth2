from ..database import db
from ..oauth.models import User


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public = db.Column(db.Boolean())
    description = db.Column(db.String(150))
    done = db.Column(db.Boolean())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
