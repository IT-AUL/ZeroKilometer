from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, send_file
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Quest, GeoPoint
import json
import uuid
from .storage import load_quests_list, delete_quest_res, upload_file, load_quest_for_edit, copy_file
from .schemas import QuestSchema, QuestRate

load_dotenv()

ALLOWED_EXTENSIONS_PROMO = {'png', 'jpg', 'jpeg'}

quest_schema = QuestSchema()
quest_rating = QuestRate()

quest_bp = Blueprint('quest_bp', __name__)
CORS(quest_bp)


@quest_bp.post('/quest_rate')
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


@quest_bp.route("/quest_list")
@jwt_required()
def quest_list():
    ans = load_quests_list(0, 5)
    return send_file(ans['message'], download_name="file.zip")


@quest_bp.route("/quest_uuid")
@jwt_required()
def quest_uuid():
    response = {
        "uuid": str(uuid.uuid4()),
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@quest_bp.get("/quest_edit/<quest_id>")
@jwt_required()
def quest_edit(quest_id):
    return make_response(send_file(load_quest_for_edit(Quest.query.get(quest_id))['message'], download_name="file.zip"),
                         200)


@quest_bp.route("/quest_save", methods=['POST'])
@jwt_required()
def quest_save():
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

    delete_quest_res(quest, True)
    quest.title_draft = data.get('title', None)
    quest.description_draft = data.get('description', None)
    quest.geopoints_draft.clear()
    quest.link_to_promo_draft = None
    for g_id in data.get('geopoints', []):
        quest.geopoints_draft.append(GeoPoint.query.get(g_id))
    print(request.files.getlist('promo'))
    if 'promo' in request.files and request.files['promo'].filename != '' and allowed_file(
            request.files['promo'].filename, ALLOWED_EXTENSIONS_PROMO):
        # save file
        quest.link_to_promo_draft = f"quest/{quest_id}_promo_draft.{request.files["promo"].filename.split('.')[-1]}"
        upload_file(request.files['promo'], quest.link_to_promo_draft)

    db.session.commit()
    response = {
        "message": "Quest Added",
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@quest_bp.route("/quest_publish", methods=['POST'])
@jwt_required()
def quest_publish():
    user_id = get_jwt_identity()
    quest_id = request.json['quest_id']

    quest = Quest.query.get(quest_id)
    user = User.query.get(user_id)

    if not quest or not any(q.id == quest_id for q in user.quests):
        return make_response(jsonify({"message": "Quest can't be published", "status": "error"}), 403)

    if not quest.ready_for_publish():
        return make_response(jsonify({"message": "Not all data is filled in", "status": "error"}), 400)

    quest.prepare_for_publishing()
    copy_file(quest.link_to_promo_draft, quest.link_to_promo)
    db.session.commit()

    return make_response(jsonify({"message": "The quest was successfully published", "status": "success"}), 200)


@quest_bp.route("/quest_delete", methods=['POST'])
@jwt_required()
def quest_delete():
    user_id = get_jwt_identity()
    quest_id = request.json['quest_id']
    user = User.query.get(user_id)
    quest = Quest.query.get(quest_id)
    if not user or not quest:
        return make_response(
            jsonify({"message": "The user is not specified or the quest is not found", "status": "error"}), 404)
    if quest.user_id != user_id:
        return make_response(
            jsonify({"message": "You do not have the rights to delete this quest", "status": "error"}), 403)
    try:
        delete_quest_res(quest, True)
        delete_quest_res(quest, False)
        db.session.delete(quest)
        db.session.commit()
        return make_response(jsonify({"message": "Quest is deleted", "status": "success"}), 200)
    except:
        db.session.rollback()
        return make_response(
            jsonify({"message": "An error occurred during the deletion process", "status": "error"}), 500)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions
