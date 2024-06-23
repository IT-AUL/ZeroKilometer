from flask import jsonify
from flask_restful import reqparse, Resource

from api import db
from api.models import User

register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument('id', type=str, required=True, help="Unique telegram user ID")
register_user_parser.add_argument('username', type=str, required=True, help="Telegram username")

delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument('id', type=str, help='Unique telegram user ID')


class UserResource(Resource):
    def post(self):
        args = register_user_parser.parse_args()
        user_id = args['id']
        username = args['username']

        user = User.query.filter_by(id=user_id).first()

        if user:
            user.progress.append(user_id)
            db.session.commit()
            return jsonify({"status": False})

        user = User(user_id, username)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"status": True, "user_id": user_id})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)})

    def delete(self):
        args = delete_user_parser.parse_args()
        user_id = args['id']
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"status": False})
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"status": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)})
