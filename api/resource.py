from flask import jsonify
from flask_restful import reqparse, Resource  # Correct import

from api import db, CHAPTERS
from api.models import User

register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument('id', type=str, required=True, help="Unique telegram user ID")
register_user_parser.add_argument('username', type=str, required=True, help="Telegram username")


class RegisterUser(Resource):
    def post(self):
        args = register_user_parser.parse_args()
        user_id = args['id']
        username = args['username']

        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()

        # user = User.query.filter_by(id=user_id).first()
        if user:
            return jsonify({"status": False}), 208

        user = User(user_id, username)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"status": True}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument('user_id', type=str, help='Unique telegram user ID')


class DeleteUser(Resource):
    def delete(self):
        args = delete_user_parser.parse_args()
        user_id = args['user_id']

        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
        # user = User.query.filter_by(id=user_id)
        if not user:
            return jsonify({"status": False}), 208
        try:
            user.delete()
            db.session.commit()
            return jsonify({"status": True}), 202
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


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

        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()

        if not user:
            return jsonify({"error": "User not found"}), 400
        # user = User.query.filter_by(id=user_id).first()

        chapter = CHAPTERS[user.progress[0]]  # user current chapter
        quest = chapter.quests[user.progress[1]]  # user current quest
        choices = quest.choices  # current quest choices

        if not any([choice.id == next_id for choice in choices]):
            return jsonify({"error": "Choice not found"}), 400

        ch = filter(lambda choice: choice.id == next_id, choices)[0]

        if ch.to_quest.startswith('q'):
            result = ch.result
            for key in result.keys():
                if key == "items":
                    user.inventory += result[key]

            try:
                user.progress = [chapter.id, ch.to_quest]
                db.session.commit()
                quest = chapter.quests[user.progress[1]]
                choices = quest.choices

                return jsonify({"chapter": chapter, "quest": quest, "choices": choices}), 202
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

        elif ch.to_quest.startswith('ch'):

            result = ch.result
            for key in result.keys():
                if key == "items":
                    user.inventory += result[key]

            try:
                user.progress = [ch.to_quest, "q0"]
                db.session.commit()

                chapter = CHAPTERS[user.progress[0]]
                quest = chapter.quests[user.progress[1]]
                choices = quest.choices

                return jsonify({"chapter": chapter, "quest": quest, "choices": choices})
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

    def get(self):
        args = choice_get.parse_args()

        user_id = args['user_id']

        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
        # user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 400

        chapter = CHAPTERS[user.progress[0]]
        quest = chapter.quests[user.progress[1]]
        choices = quest.choices
        return jsonify({"chapter": chapter, "quest": quest, "choices": choices})
