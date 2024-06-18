import json

from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    hashed_password = db.Column(db.String(300), nullable=False)
    inventory = db.Column(db.Text, nullable=False, default=json.dumps([{
        "name": "Булат",
        "id": "1",
        "type": "ally"
    }, {
        "name": "Тычкан",
        "id": "13",
        "type": "ally"
    }, {
        "name": "Бака",
        "id": "14",
        "type": "ally"
    }]))

    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password
