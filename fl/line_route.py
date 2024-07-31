from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Quest, Line
from .schemas import LineSchema

load_dotenv()

line_schema = LineSchema()

line_bp = Blueprint('line_bp', __name__)


@line_bp.post('/lines/<uuid:quest_id>')
@jwt_required()
def create_lines(quest_id):
    is_draft = request.args.get('is_draft', default=False, type=lambda v: v.lower() == 'true')
    user_id = get_jwt_identity()
    quest: Quest = Quest.query.get(str(quest_id))
    if not quest or not quest.owner(user_id):
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 404)
    try:
        data = line_schema.load(request.json, many=True)
    except ValidationError as err:
        app.logger.error(f'data {request.json}, err {err.messages}')
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)
    for line_data in data:
        line: Line = Line.query.get(line_data['line_id'])
        if not line:
            line = Line(line_data['line_id'], line_data['coords'])

            user: User = User.query.get(user_id)
            user.lines.append(line)

            if is_draft:
                quest.lines_draft.append(line)
            else:
                quest.lines.append(line)

            db.session.add(line)
    db.session.commit()
    return make_response(jsonify({"message": "Success", "status": "success"}), 201)


@line_bp.delete('/lines/<uuid:quest_id>')
@jwt_required()
def delete_quest_lines(quest_id):
    user_id = get_jwt_identity()
    is_draft = request.args.get('is_draft', default=False, type=lambda v: v.lower() == 'true')

    quest: Quest = Quest.query.get(quest_id)

    if not quest or not quest.owner(user_id):
        return make_response(jsonify({"message": "Lines do not exist", "status": "error"}), 404)

    try:
        if is_draft:
            db.session.delete(quest.lines_draft)
        else:
            db.session.delete(quest.lines)
        return make_response(jsonify({"message": "Success", "status": "success"}), 200)
    except Exception as e:
        db.session.flush()
        app.logger.error(e)
        return make_response(jsonify({"message": "Error", "status": "error"}), 500)


@line_bp.get('/lines')
@jwt_required()
def get_user_lines():
    user_id = get_jwt_identity()

    lines: list[Line] = User.query.get(user_id).lines

    ans = {line.id: line.to_dict() for line in lines}

    return make_response(jsonify({"lines": ans, "status": "success"}), 200)


@line_bp.get('/lines/<uuid:quest_id>')
@jwt_required()
def get_quest_lines(quest_id):
    user_id = get_jwt_identity()
    is_draft = request.args.get('is_draft', default=False, type=lambda v: v.lower() == 'true')

    quest: Quest = Quest.query.get(str(quest_id))

    if not quest or (is_draft and not quest.owner(user_id)):
        return make_response(jsonify({"message": "Quest does not exist", "status": "error"}), 404)

    if is_draft:
        lines: list[Line] = quest.lines_draft
    else:
        lines: list[Line] = quest.lines

    ans = {line.id: line.to_dict() for line in lines}

    return make_response(jsonify({"lines": ans, "status": "success"}), 200)
