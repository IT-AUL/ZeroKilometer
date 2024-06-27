import hashlib
import hmac
import uuid

from dotenv import load_dotenv, dotenv_values
from flask import Flask, render_template, request, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

from api.config import Config
from api.models import Quest, User

load_dotenv()

SECRET_KEY = "6329580650:AAFy9JCT62aHwTVqHJDFCwfG9skvw_MEiEw"
BOT_USERNAME = 'kazan_game_bot'

db = SQLAlchemy()

uuid = uuid


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_mapping(dotenv_values())
    db.init_app(app)

    from api import models

    with app.app_context():
        db.drop_all()
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/auth', methods=['POST'])
    def auth():
        data = request.json
        if data and check_auth(data):

            user = User.query.get(data['id'])
            if not user:
                user = User(data['id'], data['username'])
                db.session.add(user)
                db.session.commit()

            session['auth'] = data['id']
            response = {
                "message": "Authentication Successful",
                "status": "success"
            }
            return make_response(jsonify(response), 200)
        else:
            session['auth'] = False
            response = {
                "message": "Authentication Failed",
                "status": "error"
            }
            return make_response(jsonify(response), 401)

    @app.route("/quest_list")
    def quest_list():
        if 'auth' in session:
            quest_data = {}
            quests = Quest.query.all()
            for quest in quests:
                quest_data[quest.id] = quest.name
            response = {
                "quests": quest_data,
                "status": "success"
            }
            return make_response(jsonify(response), 200)
        return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)

    @app.route("/quest_uuid")
    def quest_uuid():
        if 'auth' in session:
            response = {
                "uuid": str(uuid.uuid4()),
                "status": "success"
            }
            return make_response(jsonify(response), 200)
        return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)

    @app.route("/quest_add", methods=['POST'])
    def quest_add():
        if 'auth' in session:
            user_id = session['auth']
            quest_id = request.json['quest_id']
            name = request.json['name']
            plot = request.json['plot']
            if not Quest.query.get(quest_id):
                quest = Quest(quest_id, name, plot)
                db.session.add(quest)
                db.session.commit()

                user = User.query.get(user_id)
                user.quests.append(quest.id)
                db.session.commit()
            else:
                if quest_id in User.query.get(user_id).quests:
                    quest = Quest.query.get(quest_id)
                    quest.name = name
                    quest.plot = plot
                    db.session.commit()
                    return make_response(jsonify({"message": "Quest is already registered", "status": "success"}), 200)
                else:
                    return make_response(
                        jsonify({"message": "You do not have the rights to edit this quest", "status": "error"}), 403)
        return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)

    @app.route("/quest_delete", methods=['POST'])
    def quest_delete():
        if 'auth' in session:
            user_id = str(session['auth'])
            quest_id = request.json['quest_id']

            user = User.query.get(user_id)
            quest = Quest.query.get(quest_id)

            if not user or not quest:
                return make_response(
                    jsonify({"message": "The user is not specified or the quest is not found", "status": "error"}), 404)
            if quest_id not in user.quests:
                return make_response(
                    jsonify({"message": "You do not have the rights to delete this quest", "status": "error"}), 403)

            db.session.delete(quest)
            user.quests.remove(quest_id)
            db.session.commit()

            return make_response(jsonify({"message": "Quest is deleted", "status": "success"}), 200)
        return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)

    @app.route("/quest_get", methods=['POST'])
    def quest_get():
        if 'auth' in session:
            quest_id = request.json['quest_id']
            quest = Quest.query.get(quest_id)
            if not quest:
                return make_response(jsonify({"message": "The quest is not found", "status": "error"}), 404)
            return make_response(jsonify({"quest": quest.to_dict(), "status": "success"}), 200)
        return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)

    return app


def check_auth(data):
    hash_str = data.pop('hash')
    sorted_data = sorted(data.items())
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])
    secret_key = hashlib.sha256(SECRET_KEY.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
    return h.hexdigest() == hash_str
