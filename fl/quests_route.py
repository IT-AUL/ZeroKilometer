import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, send_file, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Quest, Location, UserProgress, Line
import json
import uuid
from .storage import load_quests_list, delete_quest_res, upload_file, copy_file, load_quest_file, load_user_quests
from .schemas import QuestSchema, QuestRate
from .tools import is_file_allowed

load_dotenv()

quest_schema = QuestSchema()
quest_rating = QuestRate()

quest_bp = Blueprint('quest_bp', __name__)

PROMO_FILES = set(os.getenv('PROMO_FILES').split(','))
AUDIO_FILES = set(os.getenv('AUDIO_FILES').split(','))


@quest_bp.get("/user_quests")  # return all user's locations
@jwt_required()
def user_locations():
    user_id = get_jwt_identity()
    return make_response(send_file(load_user_quests(user_id)['message'], download_name="file.zip"), 200)


@quest_bp.post('/rate_quest')  # rate quest
@jwt_required()
def rate_quest():
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


@quest_bp.get("/quest_list")  # return all quests
@jwt_required()
def quest_list():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    ans = load_quests_list(offset, limit)
    return send_file(ans['message'], download_name="file.zip")


@quest_bp.get("/uuid")  # return uuid for quest or location
@jwt_required()
def quest_uuid():
    cnt = request.args.get('cnt', 1, int)
    ans = []
    for _ in range(cnt):
        ans.append(str(uuid.uuid4()))
    response = {
        "uuid": ans,
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@quest_bp.get("/edit_quest")  # return quest for editing
@jwt_required()
def edit_quest():
    user_id = get_jwt_identity()
    quest_id = request.args.get('quest_id', type=str)
    app.logger.info(quest_id)
    print(quest_id)
    print(Quest.query.get(quest_id))
    if not Quest.query.get(quest_id):
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 404)
    if Quest.query.get(quest_id).user_id != user_id:
        return make_response(jsonify({"message": "You can't edit this quest", "status": "error"}), 403)
    print(quest_id)
    return make_response(
        send_file(load_quest_file(Quest.query.get(quest_id), is_draft=True, add_author=False)['message'],
                  download_name="file.zip"),
        200)


@quest_bp.get("/view_quest")  # return quest for viewing
@jwt_required()
def view_quest():
    user_id = get_jwt_identity()
    quest_id = request.args.get('quest_id', type=str)

    if not Quest.query.get(quest_id):
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 404)
    if not Quest.query.get(quest_id).published:
        return make_response(jsonify({"message": "You can't play this quest now", "status": "error"}), 403)
    return make_response(
        send_file(load_quest_file(Quest.query.get(quest_id), is_draft=False, add_author=True)['message'],
                  download_name="file.zip"),
        200)


@quest_bp.put("/save_quest")  # add new quest/save quest
@jwt_required()
def save_quest():
    try:
        user_id = get_jwt_identity()
        data = request.form.get('json')
        data = json.loads(data)
        try:
            data = quest_schema.load(data)
        except ValidationError as e:
            return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
        quest_id = data['quest_id']
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
        quest.title_draft = data['title']
        quest.description_draft = data['description']
        quest.lang_draft = data['lang']
        quest.type_draft = data['type']

        quest.locations_draft.clear()
        quest.link_to_promo_draft = None
        quest.link_to_audio_draft = None

        for loc_id in data['locations']:
            quest.locations_draft.append(Location.query.get(loc_id))

        if 'promo' in request.files and is_file_allowed(request.files['promo'].filename, PROMO_FILES):
            # save file
            quest.link_to_promo_draft = f"quest/{quest_id}/promo_draft.{request.files["promo"].filename.split('.')[-1]}"
            upload_file(request.files['promo'], quest.link_to_promo_draft)

        if 'audio' in request.files and is_file_allowed(request.files['audio'].filename, PROMO_FILES):
            # save file
            quest.link_to_promo_draft = f"quest/{quest_id}/audio_draft.{request.files["audio"].filename.split('.')[-1]}"
            upload_file(request.files['audio'], quest.link_to_promo_draft)

        db.session.commit()
        response = {
            "message": "Quest Added",
            "status": "success"
        }
        return make_response(jsonify(response), 200)
    except json.JSONDecodeError:
        return make_response(jsonify({"message": "Invalid JSON format", "status": "error"}), 400)


@quest_bp.post("/publish_quest")  # publish quest if it readies to it
@jwt_required()
def publish_quest():
    user_id = get_jwt_identity()
    quest_id = request.json['quest_id']

    quest: Quest = Quest.query.get(quest_id)
    user = User.query.get(user_id)

    if not quest or not any(q.id == quest_id for q in user.quests):
        return make_response(jsonify({"message": "Quest can't be published", "status": "error"}), 403)

    if not quest.ready_for_publish():
        return make_response(jsonify({"message": "Not all data is filled in", "status": "error"}), 400)

    quest.prepare_for_publishing()
    copy_file(quest.link_to_promo_draft, quest.link_to_promo)
    if quest.link_to_audio_draft:
        copy_file(quest.link_to_audio_draft, quest.link_to_audio)
    db.session.commit()

    return make_response(jsonify({"message": "The quest was successfully published", "status": "success"}), 200)


@quest_bp.delete("/delete_quest")  # delete quest
@jwt_required()
def delete_quest():
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
        user_progresses = UserProgress.query.filter_by(quest_id=quest_id).all()
        for progress in user_progresses:
            db.session.delete(progress)
        db.session.delete(quest)
        db.session.commit()
        return make_response(jsonify({"message": "Quest is deleted", "status": "success"}), 200)
    except Exception as e:
        db.session.rollback()
        return make_response(
            jsonify({"message": "An error occurred during the deletion process", "status": "error"}), 500)
