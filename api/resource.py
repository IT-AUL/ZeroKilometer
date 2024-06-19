from flask import jsonify
from flask_restful import reqparse, Resource  # Correct import

from api import db
from api.models import User

CHAPTERS = {}

register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument('id', type=str, required=True, help="Unique telegram user ID")
register_user_parser.add_argument('username', type=str, required=True, help="Telegram username")


class RegisterUser(Resource):
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


delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument('user_id', type=str, help='Unique telegram user ID')


class DeleteUser(Resource):
    def delete(self):
        args = delete_user_parser.parse_args()
        user_id = args['user_id']

        user = User.query.filter_by(id=user_id)
        if not user:
            return jsonify({"status": False})
        try:
            user.delete()
            db.session.commit()
            return jsonify({"status": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)})


choice_apply = reqparse.RequestParser()
choice_apply.add_argument('user_id', type=str, help='Unique telegram user ID')
choice_apply.add_argument('next_id', type=str, help='ID for the next quest or chapter')

choice_get = reqparse.RequestParser()
choice_get.add_argument('user_id', type=str, help='Unique telegram user ID')


class ApplyChoice(Resource):
    def post(self):
        args = choice_apply.parse_args()
        user_id = args['user_id']
        next_id = args['next_id']

        if not user_id or not User.query.filter_by(id=user_id).first() or not next_id:
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

        chapter = CHAPTERS[user.progress[0]]
        quest = chapter.quests[user.progress[1]]
        choices = quest.choices
        return jsonify({"chapter": chapter, "quest": quest, "choices": choices})
