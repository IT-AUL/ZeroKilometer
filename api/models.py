import json
from api import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    username = db.Column(db.String(80), nullable=False)
    progress = db.Column(db.JSON, nullable=True, default=['ch0', 'q0'])
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

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.id
