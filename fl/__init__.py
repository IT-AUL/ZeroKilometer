from flask import Flask
from flask_jwt_extended import JWTManager

from .quests_route import quest_bp
from .auth import user_bp
from .geopoints_route import geopoint_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    app.register_blueprint(quest_bp)
    app.register_blueprint(geopoint_bp)
    jwt = JWTManager(app)

    return app
