import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, session, make_response, render_template
from .models import db, User, Quest
import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl
import uuid

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

main = Blueprint('main', __name__)


@main.route('/')
def index():
    quests = Quest.query.all()
    return render_template('index.html', quests=quests)


@main.route('/auth', methods=['POST'])
def auth():
    data = request.json
    res, data = check(TELEGRAM_BOT_TOKEN, data)

    if res:
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


@main.route("/quest_list")
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


@main.route("/quest_uuid")
def quest_uuid():
    if 'auth' in session:
        response = {
            "uuid": str(uuid.uuid4()),
            "status": "success"
        }
        return make_response(jsonify(response), 200)
    return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)


@main.route("/quest_add", methods=['POST'])
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


@main.route("/quest_delete", methods=['POST'])
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

        try:
            os.remove(quest.plot)
            db.session.delete(quest)
            user.quests.remove(quest_id)
            db.session.commit()

            return make_response(jsonify({"message": "Quest is deleted", "status": "success"}), 200)
        except:
            db.session.rollback()
            return make_response(
                jsonify({"message": "An error occurred during the deletion process", "status": "error"}), 500)
    return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)


@main.route("/quest_get", methods=['POST'])
def quest_get():
    if 'auth' in session:
        quest_id = request.json['quest_id']
        quest = Quest.query.get(quest_id)
        if not quest:
            return make_response(jsonify({"message": "The quest is not found", "status": "error"}), 404)
        return make_response(jsonify({"quest": quest.to_dict(), "status": "success"}), 200)
    return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)


def check(token: str, init_data: str):
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        return False, None
    try:
        user_data = json.loads(parsed_data['user'])
    except (ValueError, KeyError):
        return False, None
    if "hash" not in parsed_data:
        return False, None
    hash_ = parsed_data.pop('hash')
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_, user_data
