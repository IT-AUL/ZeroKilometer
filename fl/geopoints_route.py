from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, send_file
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import db, User, GeoPoint
import json
from .storage import delete_geopoint_res, load_user_geopoint, upload_file
from .schemas import QuestSchema, QuestRate
from .tools import allowed_file

load_dotenv()

quest_schema = QuestSchema()
quest_rating = QuestRate()

geopoint_bp = Blueprint('geopoint_bp', __name__)
CORS(geopoint_bp)

ALLOWED_IMAGE = {'png', 'jpg', 'jpeg'}
ALLOWED_FILES = {'mp4', 'png', 'jpg', 'jpeg', 'avi'}
AUDIO_FILES = {'mp3', 'wav', 'ogg'}


@geopoint_bp.get("/user_geopoints")
@jwt_required()
def all_geopoint():
    user_id = get_jwt_identity()
    return make_response(send_file(load_user_geopoint(user_id)['message'], download_name="file.zip"), 200)


@geopoint_bp.route("/geopoint_save", methods=['POST'])
@jwt_required()
def geopoint_save():
    user_id = get_jwt_identity()
    data = request.form.get('json')
    data = json.loads(data)

    geopoint_id = data.get("geopoint_id", None)
    if not geopoint_id:
        return make_response(jsonify({"message": "Missing geopoint id"}), 400)
    geopoint = GeoPoint.query.get(geopoint_id)
    if not geopoint:
        geopoint = GeoPoint(geopoint_id)
        geopoint.user_id = user_id
        db.session.add(geopoint)
        db.session.commit()
    else:
        user = User.query.filter_by(id=user_id).first()
        if not any(geo.id == geopoint_id for geo in user.geo_points):
            return make_response(
                jsonify({"message": "You do not have the rights to edit this geopoint", "status": "error"}), 403)

    delete_geopoint_res(geopoint, True)
    geopoint.title_draft = data.get('title', None)
    geopoint.coords_draft = data.get('coords', None)
    geopoint.description_draft = data.get('description', None)
    geopoint.links_to_media_draft.clear()
    geopoint.link_to_promo_draft = None
    geopoint.link_to_audio_draft = None

    print(request.files['promo'].filename.split('.')[-1], 'promo' in request.files,
          allowed_file(request.files['promo'], ALLOWED_IMAGE))

    if 'promo' in request.files and allowed_file(request.files['promo'].filename, ALLOWED_IMAGE):
        print(request.files['promo'])
        geopoint.link_to_promo_draft = f"geopoint/{geopoint.id}/promo_draft.{request.files['promo'].filename.split('.')[-1]}"
        upload_file(request.files['promo'], geopoint.link_to_promo_draft)

    if 'audio' in request.files and allowed_file(request.files['audio'].filename, AUDIO_FILES):
        geopoint.link_to_promo_draft = f"geopoint/{geopoint.id}/audio_draft.{request.files['audio'].filename.split('.')[-1]}"
        upload_file(request.files['audio'], geopoint.link_to_promo_draft)

    if 'media' in request.files:
        cnt = 0
        for media in request.files.getlist('media'):
            if allowed_file(media.filename, ALLOWED_FILES):
                geopoint.links_to_media_draft.append(
                    f"geopoint/{geopoint.id}/media_{cnt}_draft.{media.filename.split('.')[-1]}")
                upload_file(media, geopoint.links_to_media_draft[-1])
                cnt += 1

    db.session.commit()
    response = {
        "message": "Geopoint Added",
        "status": "success"
    }
    return make_response(jsonify(response), 200)
