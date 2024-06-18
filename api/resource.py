from importlib.resources import Resource

from flask import request, jsonify
from flask_restful import reqparse
from werkzeug.security import generate_password_hash, check_password_hash

from api import db
from api.models import User

CHAPTERS = {}

"""
1 user_init post(username, password) -> save user to db
2 check_user post(username, password, username_only=True) -> check if user is exist or if password is correct
3 get_info_by_choice post(cur_chapter, cur_quest, next_id) -> apply choice_result and return next chapter and quest data
4 get_info post() -> get last chapter and quest
5 clear_data delete(username) -> delete user
"""


class Register(Resource):
    def post(self):


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


choice_apply = reqparse.RequestParser()
choice_apply.add_argument('user_id', type=str, help='Unique telegram user ID')
choice_apply.add_argument('next_id', type=str, help='ID for the next quest or chapter')

choice_get = reqparse.RequestParser()
choice_get.add_argument('user_id', type=str, help='Unique telegram user ID')


class Choice(Resource):
    def post(self):
        args = choice_apply.parse_args()
        user_id = args['user_id']
        next_id = args['next_id']

        if not user_id or not User.query.filter_by(user_id=user_id).first() or not next_id:
            return jsonify({"error": "incorrect user_id, next_id"})
        user = User.query.filter_by(id=user_id).first()

        chapter = CHAPTERS[user.progress[0]]
        quest = chapter.quests[user.progress[1]]
        choices = quest.choices
        if next_id.startswith('q'):

            if not any([next_id == i.to_quest for i in choices]):
                return jsonify({"error": "incorrect choice_id"})

            result = filter(lambda x: x.id == next_id, choices)[0].result
            for key in result.keys():
                if key == "items":
                    user.inventory += result[key]
            user.progress = [chapter.id, next_id]
            db.session.commit()

            return jsonify(
                {"chapter": chapter, "quest": chapter.quests[next_id], "choices": chapter.quests[next_id].choices})
        elif next_id.startswith('ch'):
            if not any(next_id == i.id for i in CHAPTERS.values()):
                return jsonify({"error": "incorrect choice_id"})

            result = filter(lambda x: x.id == next_id, choices)[0].result
            for key in result.keys():
                if key == "items":
                    user.inventory += result[key]

            user.progress = [next_id, "q0"]
            db.session.commit()
            return jsonify({"chapter": CHAPTERS[next_id], "quest": CHAPTERS[next_id].quests['q0'],
                            "choices": CHAPTERS[next_id].quests['q0'].choices})

    def get(self):
        args = choice_get.parse_args()

        user_id = args['user_id']

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"})

        chapter = CHAPTERS[user.progess[0]]
        quest = chapter.quests[user.progess[1]]
        choices = quest.choices
        return jsonify({"chapter": chapter, "quest": quest, "choices": choices})


delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument('user_id', type=str, help='Unique telegram user ID')


class DeleteUser(Resource):
    def delete(self):
        args = delete_user_parser.parse_args()
        user_id = args['user_id']

        try:
            User.query.filter_by(id=user_id).delete()
            db.session.commit()
            return jsonify({"status": True})
        except Exception as e:
            return jsonify({"error": str(e)})
