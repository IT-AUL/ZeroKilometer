import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, send_file, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Location, Quest, UserProgress
import json
from .storage import delete_location_res, load_user_locations, upload_file, copy_file, load_quest_locations
from .schemas import QuestSchema, QuestRate, LocationSchema
from .tools import is_file_allowed

load_dotenv()

quest_schema = QuestSchema()
quest_rating = QuestRate()
location_schema = LocationSchema()

location_bp = Blueprint('location_bp', __name__)

PROMO_FILES = set(os.getenv('PROMO_FILES').split(','))
MEDIA_FILES = set(os.getenv('MEDIA_FILES').split(','))
AUDIO_FILES = set(os.getenv('AUDIO_FILES').split(','))


@location_bp.get("/users/locations")  # return all user's locations
@jwt_required()
def get_all_user_locations():
    user_id = get_jwt_identity()
    return make_response(send_file(load_user_locations(user_id)['message'], download_name="file.zip"), 200)


@location_bp.post('/locations')
@jwt_required()
def create_location():
    user_id = get_jwt_identity()
    data = request.form.get('json')
    data = json.loads(data)
    try:
        data = location_schema.load(data)
    except ValidationError as err:
        app.logger.error(err.messages)
        return make_response(jsonify({"message": "Data is not valid"}), 422)

    location_id = data['location_id']

    location: Location = Location.query.get(location_id)
    if location:
        return make_response(jsonify({"message": "Location already exists", "status": "error"}), 422)

    location = Location(location_id)
    location.user_id = user_id
    db.session.add(location)
    db.session.commit()

    ans = delete_location_res(location, True)
    if ans['status'] == 'error':
        return make_response(jsonify({"message": "Something going wrong", "status": "error"}), 500)

    location.title_draft = data['title']
    location.coords_draft = data['coords']
    location.description_draft = data['description']
    location.lang_draft = data['lang']

    location.links_to_media_draft.clear()
    location.link_to_promo_draft = None
    location.link_to_audio_draft = None

    if 'promo' in request.files and is_file_allowed(request.files['promo'].filename, PROMO_FILES):
        location.link_to_promo_draft = f"location/{location.id}/promo_draft.{request.files['promo'].filename.split('.')[-1]}"
        upload_file(request.files['promo'], location.link_to_promo_draft)

    if 'audio' in request.files and is_file_allowed(request.files['audio'].filename, AUDIO_FILES):
        location.link_to_promo_draft = f"location/{location.id}/audio_draft.{request.files['audio'].filename.split('.')[-1]}"
        upload_file(request.files['audio'], location.link_to_promo_draft)

    if 'media' in request.files:
        cnt = 0
        for media in request.files.getlist('media'):
            if is_file_allowed(media.filename, MEDIA_FILES):
                location.links_to_media_draft.append(
                    f"location/{location.id}/media_{cnt}_draft.{media.filename.split('.')[-1]}")
                upload_file(media, location.links_to_media_draft[-1])
                cnt += 1

    db.session.commit()
    response = {
        "message": "Location saved",
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@location_bp.put("/location")  # add new location/save location
@jwt_required()
def update_location():
    user_id = get_jwt_identity()
    data = request.form.get('json')
    data = json.loads(data)
    try:
        data = location_schema.load(data)
    except ValidationError as err:
        return make_response(jsonify({"message": "Data is not valid"}), 422)

    location_id = data['location_id']

    location: Location = Location.query.get(location_id)
    if not location:
        return make_response(jsonify({"message": "Location does not exists", "status": "error"}), 422)
    user = User.query.filter_by(id=user_id).first()
    if not any(loc.id == location_id for loc in user.locations):
        return make_response(
            jsonify({"message": "You do not have the rights to edit this location", "status": "error"}), 403)

    ans = delete_location_res(location, True)
    if ans['status'] == 'error':
        return make_response(jsonify({"message": "Something going wrong", "status": "error"}), 500)

    location.title_draft = data['title']
    location.coords_draft = data['coords']
    location.description_draft = data['description']
    location.lang_draft = data['lang']

    location.links_to_media_draft.clear()
    location.link_to_promo_draft = None
    location.link_to_audio_draft = None

    if 'promo' in request.files and is_file_allowed(request.files['promo'].filename, PROMO_FILES):
        location.link_to_promo_draft = f"location/{location.id}/promo_draft.{request.files['promo'].filename.split('.')[-1]}"
        upload_file(request.files['promo'], location.link_to_promo_draft)

    if 'audio' in request.files and is_file_allowed(request.files['audio'].filename, AUDIO_FILES):
        location.link_to_promo_draft = f"location/{location.id}/audio_draft.{request.files['audio'].filename.split('.')[-1]}"
        upload_file(request.files['audio'], location.link_to_promo_draft)

    if 'media' in request.files:
        cnt = 0
        for media in request.files.getlist('media'):
            if is_file_allowed(media.filename, MEDIA_FILES):
                location.links_to_media_draft.append(
                    f"location/{location.id}/media_{cnt}_draft.{media.filename.split('.')[-1]}")
                upload_file(media, location.links_to_media_draft[-1])
                cnt += 1

    db.session.commit()
    response = {
        "message": "Location saved",
        "status": "success"
    }
    return make_response(jsonify(response), 200)


@location_bp.post(
    "/locations/<str:location_id>/publish")  # checks that the location is ready for publication and sends it if so
@jwt_required()
def publish_location(location_id):
    user_id = get_jwt_identity()

    location: Location = Location.query.get(location_id)
    user: User = User.query.get(user_id)

    if not location or not any(loc.id == location_id for loc in user.locations):
        return make_response(jsonify({"message": "Location can't be published", "status": "error"}), 403)

    if not location.ready_for_publish():
        return make_response(jsonify({"message": "Not all data is filled in", "status": "error"}), 400)

    ans = delete_location_res(location)
    location.prepare_for_publishing()
    copy_file(location.link_to_promo_draft, location.link_to_promo)
    if location.link_to_audio:
        copy_file(location.link_to_audio_draft, location.link_to_audio)
    for link_c, link in zip(location.links_to_media_draft, location.links_to_media):
        copy_file(link_c, link)
    db.session.commit()

    return make_response(jsonify({"message": "The location was successfully published", "status": "success"}), 200)


@location_bp.get("/quests/str:quest_id/locations")  # return all quest's locations
@jwt_required()
def get_all_quest_locations(quest_id):
    user_id = get_jwt_identity()
    is_draft = request.args.get('is_draft', False, type=bool)

    if not quest_id:
        return make_response(jsonify({"message": "quest_id is required", "status": "error"}), 400)

    quest: Quest = Quest.query.get(quest_id)
    if not quest:
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 400)

    if is_draft and quest.user_id != user_id:
        return make_response(jsonify({"message": "You can't edit this quest", "status": "error"}), 403)

    if not quest.published and quest.user_id != user_id:
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 400)

    ans = load_quest_locations(quest, is_draft)
    if ans['status'] == 'success':
        return make_response(send_file(ans['message'], download_name='file.zip'), 200)


@location_bp.delete(
    "/locations/<str:location_id>")  # delete location (if after deleting location, there are no points left in some quests, they become unpublishable)
@jwt_required()
def delete_location(location_id):
    user_id = get_jwt_identity()
    location: Location = Location.query.get(location_id)
    if not location or location.user_id != user_id:
        return make_response(jsonify({"message": "You can't delete this location", "status": "error"}), 403)

    for quest in User.query.get(user_id).quests:
        if location in quest.locations and len(quest.locations) == 1:
            quest.published = False
    user_progresses = UserProgress.query.filter_by(location_id=location_id).all()
    for progress in user_progresses:
        db.session.delete(progress)
    delete_location_res(location, True)
    delete_location_res(location, False)
    db.session.delete(location)
    db.session.commit()

    return make_response(jsonify({"message": "Location deleted", "status": "success"}), 200)
