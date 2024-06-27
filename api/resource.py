import base64

from flask import jsonify, send_file
from flask_restful import reqparse, Resource

from api import db, bucket
from api.models import User
from api import uuid as u

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
            return jsonify({"status": False})

        user = User(user_id, username)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"status": True})
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

    def get(self):
        uuid = str(u.uuid4())
        return jsonify({"uuid": uuid})


add_quest_parser = reqparse.RequestParser()
add_quest_parser.add_argument('id', type=str, required=True, help="Unique telegram user ID")
add_quest_parser.add_argument('quest_id', type=str, required=True, help="Unique quest ID")
add_quest_parser.add_argument("file", type=str, required=True, help="File with quest plot")


class Quest(Resource):

    def get(self, quest_id):
        try:
            blob = bucket.blob(f'{quest_id}.json')
            if not blob.exists():
                return jsonify({'error': 'File not found'})

            file_content = blob.download_as_bytes()
            encoded_content = base64.b64encode(file_content).decode('utf-8')

            response = {
                'file_name': f'{quest_id}.json',
                'content': encoded_content
            }
            return jsonify(response)
        except Exception as e:
            return {'message': str(e)}, 500

    def post(self):
        args = add_quest_parser.parse_args()
        user_id = args['id']
        quest_id = args['quest_id']
        file = args['file']

        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({"status": False})

        try:
            file_path = f'uploaded_files/{quest_id}'
            blob = bucket.blob(file_path)
            blob.upload_from_file(file)
            return jsonify({'status': True})
        except Exception as e:
            return jsonify({'error': str(e)})
