from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .quests_route import quest_bp
from .user_routes import user_bp
from .location_route import location_bp
import logging
from logging.handlers import RotatingFileHandler



def create_app():
    app = Flask(__name__)
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    allowed_origins = [
        "https://zero-kilometer.ru/",
        "https://kilometr-zero.netlify.app/",
        # Add more domains as needed
    ]

    # Configure CORS with the list of allowed origins
    CORS(app)

    @app.before_request
    def log_request_info():
        app.logger.debug('Headers: %s', request.headers)
        app.logger.debug('Origin: %s', request.headers.get('Origin'))

    app.register_blueprint(user_bp)
    app.register_blueprint(quest_bp)
    app.register_blueprint(location_bp)
    jwt = JWTManager(app)

    return app
