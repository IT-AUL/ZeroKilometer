import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from marshmallow import ValidationError

from .models import db, User, UserProgress
from .storage import upload_file
from .schemas import UserAuth
from .tools import check_telegram_authorization

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

user_auth = UserAuth()

user_bp = Blueprint('user_bp', __name__)


@user_bp.post('/refresh')  # about once every 10 minutes, you need to update the jwt token
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


@user_bp.post('/auth')  # auth user
def auth():
    try:
        data = request.get_json()
        data = user_auth.load(data)
    except ValidationError as e:
        print(str(e))
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
    user_data, valid_data = check_telegram_authorization(TELEGRAM_BOT_TOKEN, data)
    # try:
    #     data = request.form.get('json')
    #     data = user_auth.load(json.loads(data))
    # except ValidationError as e:
    #     return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
    # valid_data, user_data = is_user_valid(TELEGRAM_BOT_TOKEN, data["user_data"])

    if valid_data:
        user = User.query.get(user_data['id'])
        if not user:
            user = User(user_data['id'], user_data['username'])
            if 'photo_url' in user_data:
                response = requests.get(user_data['photo_url'], allow_redirects=True)
                if response.status_code == 200:
                    user.link_to_profile_picture = f"user_profile/{user.id}/user_profile.jpg"
                    upload_file(BytesIO(response.content), user.link_to_profile_picture)
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


@user_bp.put('/save_progress')  # save user progress
@jwt_required()
def save_progress():
    user_id = get_jwt_identity()
    data = request.json

    quest_id = data['quest_id']

    location_ids = data['location_ids']
    for location_id in location_ids:
        progress = UserProgress(user_id, quest_id, location_id)
        db.session.add(progress)
    db.session.commit()
    return make_response(jsonify({"message": "Saved user progress", "status": "success"}), 200)
