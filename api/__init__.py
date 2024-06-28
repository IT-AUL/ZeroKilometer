import uuid

from dotenv import load_dotenv, dotenv_values
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

SECRET_KEY = "6329580650:AAFy9JCT62aHwTVqHJDFCwfG9skvw_MEiEw"
BOT_USERNAME = 'kazan_game_bot'

db = SQLAlchemy()
app = Flask(__name__)

uuid = uuid


def create_app():
    app.config.from_mapping(dotenv_values())
    db.init_app(app)

    # from . import models
    # from . import routes
    @app.route('/')
    def index():
        return "hello"

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app
