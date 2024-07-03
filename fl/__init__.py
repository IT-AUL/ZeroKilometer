from flask import Flask
from flask_jwt_extended import JWTManager

from .routes import main


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    jwt = JWTManager(app)

    return app
