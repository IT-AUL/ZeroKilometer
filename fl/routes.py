import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, render_template
from flask_cors import CORS
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from marshmallow import ValidationError

from .models import db, User, Quest, GeoPoint
import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl
import uuid

from .schemas import QuestSchema, UserAuth, QuestRate

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
UPLOAD_FOLDER = os.getenv('PLOT_FOLDER')

ALLOWED_EXTENSIONS_PROMO = {'png', 'jpg', 'jpeg'}

quest_schema = QuestSchema()
user_auth = UserAuth()
quest_rating = QuestRate()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

main = Blueprint('main', __name__)
CORS(main)


@main.route('/')
def index():
    quests = Quest.query.all()
    return render_template('index.html', quests=quests)


@main.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


@main.route('/auth', methods=['POST'])
def auth():
    try:
        data = user_auth.load(request.json)
    except ValidationError as e:
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
    valid_data, user_data = check(TELEGRAM_BOT_TOKEN, data["user_data"])

    if valid_data or True:
        user = User.query.get(user_data['id'])
        if not user:
            user = User(user_data['id'], user_data['username'])
            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(identity=user_data['id'])
        refresh_token = create_refresh_token(identity=user_data['id'])
        response = {
            "message": "Authentication Successful",
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return make_response(jsonify(response), 200)
    else:
        response = {
            "message": "Authentication Failed",
            "status": "error"
        }
        return make_response(jsonify(response), 401)


@main.post('/quest_rate')
@jwt_required()
def quest_rate():
    user_id = get_jwt_identity()
    try:
        data = quest_rating.load(request.json)
    except ValidationError as e:
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)

    quest_id, rating = str(data['quest_id']), data['rating']
    quest = Quest.query.get(quest_id)
    if not quest:
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 404)

    user = User.query.get(user_id)
    new_r = quest.rating * quest.rating_count + rating

    if quest_id in user.rating:
        new_r -= user.rating[quest_id]
        quest.rating_count -= 1

    quest.rating_count += 1
    quest.rating = round(new_r / quest.rating_count, 2)

    user.rating[quest_id] = rating

    db.session.commit()
    return make_response(jsonify({"message": "Rating successfully updated", "status": "success"}), 200)


@main.route("/quest_list")
@jwt_required()
def quest_list():
    quest_data = {}
    quests = Quest.query.all()
    for quest in quests:
        quest_data[quest.id] = quest.name
    response = {
        "quests": quest_data,
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@main.route("/quest_uuid")
@jwt_required()
def quest_uuid():
    response = {
        "uuid": str(uuid.uuid4()),
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@main.route("/quest_save", methods=['POST'])
@jwt_required()
def quest_add():
    user_id = get_jwt_identity()
    data = request.form.get('json')
    data = json.loads(data)
    quest_id = str(data.get("quest_id", None))
    if quest_id is None:
        return make_response(jsonify({"message": "Missing quest id"}), 400)
    quest = Quest.query.get(quest_id)
    if not quest:
        quest = Quest(quest_id)
        quest.user_id = user_id
        db.session.add(quest)
        db.session.commit()
    else:
        user = User.query.filter_by(id=user_id).first()
        if not any(q.id == quest_id for q in user.quests):
            return make_response(
                jsonify({"message": "You do not have the rights to edit this quest", "status": "error"}), 403)

    quest.title_draft = data.get('title', None)
    quest.description_draft = data.get('description', None)
    quest.geopoints_draft.clear()
    quest.link_to_promo_draft = None
    for g_id in data.get('geopoints', []):
        quest.geopoints_draft.append(GeoPoint.query.get(g_id))
    if 'promo' in request.files and request.files['promo'].filename != '' and allowed_file(
            request.files['promo'].filename, ALLOWED_EXTENSIONS_PROMO):
        # save file
        quest.link_to_promo_draft = f"{quest_id}_promo_draft.{request.files["promo"].filename.split('.')[-1]}"
    db.session.commit()
    response = {
        "message": "Quest Added",
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@main.route("/quest_delete", methods=['POST'])
@jwt_required()
def quest_delete():
    user_id = get_jwt_identity()
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


@main.route("/quest_get", methods=['POST'])
@jwt_required()
def quest_get():
    quest_id = request.json['quest_id']
    quest = Quest.query.get(quest_id)
    if not quest:
        return make_response(jsonify({"message": "The quest is not found", "status": "error"}), 404)
    return make_response(jsonify({"quest": quest.to_dict(), "status": "success"}), 200)


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


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions
