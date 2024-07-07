from flask import Flask
from flask_jwt_extended import JWTManager

from .quests_route import quest_bp
from .user_routes import user_bp
from .location_route import location_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    app.register_blueprint(quest_bp)
    app.register_blueprint(location_bp)
    jwt = JWTManager(app)

    return app
