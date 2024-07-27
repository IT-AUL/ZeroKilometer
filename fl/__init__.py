import logging

from flask import Flask
from flask.logging import default_handler
from flask_jwt_extended import JWTManager

from .quests_route import quest_bp
from .user_routes import user_bp
from .location_route import location_bp
from .line_route import line_bp
from flask_cors import CORS


def create_app():
    # logging.basicConfig(filename='flask.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = Flask(__name__)

    # file_handler = logging.FileHandler('flask.log')
    # file_handler.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # file_handler.setFormatter(formatter)
    # app.logger.addHandler(file_handler)

    CORS(app, origins=["https://zero-kilometer.ru", "https://kilometr-zero.netlify.app"])
    app.register_blueprint(user_bp)
    app.register_blueprint(quest_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(line_bp)
    jwt = JWTManager(app)

    return app
