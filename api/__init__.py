from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from api.quest_modules.quest_manager import load_chapters

db = SQLAlchemy()
CHAPTERS = load_chapters()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from api import models

    with app.app_context():
        db.create_all()

    api = Api(app)
    from api.resource import RegisterUser

    api.add_resource(RegisterUser, "/api/register")
    from api.resource import DeleteUser

    api.add_resource(DeleteUser, "/api/delete")
    from api.resource import ApplyChoice

    api.add_resource(ApplyChoice, "/api/choice")
    return app

# def create_app():
#     app = Flask(__name__)
#
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#     db.init_app(app)
#
#     api = Api(app)
#
#     from api.models import *
#     from api.resource import RegisterUser, DeleteUser, ApplyChoice
#
#     with app.app_context():
#         db.init_app(app)
#         db.create_all()
#
#     api.add_resource(RegisterUser, "/api/register")
#     api.add_resource(DeleteUser, "/api/delete")
#     api.add_resource(ApplyChoice, "/api/choice")
#     return app
