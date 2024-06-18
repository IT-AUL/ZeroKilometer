from importlib.resources import Resource

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from api.models import User


class InitUser(Resource):
    def post(self):
        try:
            username = request.json['username']
            password = request.json['password']

            user = User(username, generate_password_hash(password))
            return jsonify({"status": True, "data": user})

        except Exception as e:
            return jsonify({"status": False, "data": str(e)})


class CheckUser(Resource):
    def post(self):
        try:
            username = request.json['username']
            password = request.json['password']
            username_only = request.json['username_only']

            user = User.query.filter_by(username=username).first()
            if username_only:
                return jsonify({"status": True, "data": user is not None})
            psw = User.query.filter_by(username=username).first().hash_password

            return jsonify({"status": True, "data": user is not None and check_password_hash(psw, password)})
        except Exception as e:
            return jsonify({"status": False, "data": str(e)})
