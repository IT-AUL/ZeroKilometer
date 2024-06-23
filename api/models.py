from sqlalchemy.ext.mutable import MutableDict, MutableList

from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    progress = db.Column(MutableList.as_mutable(db.JSON), default=list)

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.id
