import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, session, make_response, render_template
from flask_cors import CORS
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Quest
import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl
import uuid

from .schemas import QuestSchema, UserAuth

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
UPLOAD_FOLDER = os.getenv('PLOT_FOLDER')

quest_schema = QuestSchema()
user_auth = UserAuth()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

main = Blueprint('main', __name__)
CORS(main)


@main.route('/')
def index():
    quests = Quest.query.all()
    return render_template('index.html', quests=quests)


@main.route('/auth', methods=['POST'])
def auth():
    try:
        data = user_auth.load(request.json)
    except ValidationError as e:
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
    res, user_data = check(TELEGRAM_BOT_TOKEN, data["user_data"])

    if res:
        user = User.query.get(user_data['id'])
        if not user:
            user = User(user_data['id'], user_data['username'])
            db.session.add(user)
            db.session.commit()

        session['auth'] = user_data['id']
        access_token = create_access_token(identity=user_data['id'])
        response = {
            "message": "Authentication Successful",
            "status": "success",
            "access_token": access_token
        }
        print(session)
        return make_response(jsonify(response), 200)
    else:
        session['auth'] = False
        response = {
            "message": "Authentication Failed",
            "status": "error"
        }
        return make_response(jsonify(response), 401)


@main.route("/quest_list")
@jwt_required()
def quest_list():
    print(get_jwt_identity())
    # if 'auth' in session:
    quest_data = {}
    quests = Quest.query.all()
    for quest in quests:
        quest_data[quest.id] = quest.name
    response = {
        "quests": quest_data,
        "status": "success"
    }
    return make_response(jsonify(response), 200)
    # return make_response(jsonify({"message": "Unauthenticated", "status": "error"}), 401)


@main.route("/quest_uuid")
@jwt_required()
def quest_uuid():
    response = {
        "uuid": str(uuid.uuid4()),
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@main.route("/quest_add", methods=['POST'])
def quest_add():
    if 'auth' in session:
        user_id = session['auth']
        try:
            data = quest_schema.load(request.json)
        except ValidationError as e:
            return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
        quest_id = data['quest_id']
        name = data['name']
        plot = data['plot']
        # if 'file' not in request.files:
        #     return make_response(jsonify({"message": "Missing file", 'status': 'error'}), 400)
        # file = request.files['file']
        # if file.filename == '':
        #     return make_response(jsonify({"message": "No selected file", 'status': 'error'}), 400)
        if plot:
            file_path = os.path.join(UPLOAD_FOLDER, quest_id, '.json')
            if not Quest.query.get(quest_id):
                with open(file_path, 'x') as f:
                    f.write(plot)
                quest = Quest(quest_id, name, quest_id)
                db.session.add(quest)
                db.session.commit()

                user = User.query.get(user_id)
                user.quests.append(quest.id)
                db.session.commit()
            else:
                if quest_id in User.query.get(user_id).quests:
                    os.remove(file_path)
                    with open(file_path, 'w') as f:
                        f.write(plot)
                    quest = Quest.query.get(quest_id)
                    quest.name = name
                    # quest.plot = plot
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
    print(init_data)
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
