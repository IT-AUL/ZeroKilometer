import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from marshmallow import ValidationError

from .models import db, User
import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl
from .storage import upload_file
from .schemas import UserAuth

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

user_auth = UserAuth()

auth_bp = Blueprint('auth_bp', __name__)
CORS(auth_bp)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


@auth_bp.route('/auth', methods=['POST'])
def auth():
    try:
        data = request.form.get('json')
        data = user_auth.load(json.loads(data))
    except ValidationError as e:
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 422)
    valid_data, user_data = check(TELEGRAM_BOT_TOKEN, data["user_data"])

    if valid_data or True:
        user = User.query.get(user_data['id'])
        if not user:
            user = User(user_data['id'], user_data['username'])
            user.link_to_profile_picture = f"user_profile/user_profile.{request.files['profile'].filename.split('.')[1]}"
            upload_file(request.files['profile'], user.link_to_profile_picture)
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
