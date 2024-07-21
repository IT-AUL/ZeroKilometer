from flask import Flask
from flask_jwt_extended import JWTManager
from .quests_route import quest_bp
from .user_routes import user_bp
from .location_route import location_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    CORS(app, origins=["https://zero-kilometer.ru", "https://kilometr-zero.netlify.app"])
    app.register_blueprint(user_bp)
    app.register_blueprint(quest_bp)
    app.register_blueprint(location_bp)
    jwt = JWTManager(app)

    return app
