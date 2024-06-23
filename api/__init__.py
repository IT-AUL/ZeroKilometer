from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from api.config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from api import models

    with app.app_context():
        db.drop_all()
        db.create_all()

    api = Api(app)

    from api.resource import UserResource
    api.add_resource(UserResource, "/api/user")
    return app
