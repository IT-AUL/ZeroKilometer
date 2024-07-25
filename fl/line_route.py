from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Quest, Line
from .schemas import LineSchema, LinesSchema

load_dotenv()

line_schema = LineSchema()
lines_schema = LinesSchema()

line_bp = Blueprint('line_bp', __name__)


@line_bp.post('/lines/str:quest_id/str:line_id')
@jwt_required()
def create_line(quest_id, line_id):
    user_id = get_jwt_identity()
    line = Line.query.get(line_id)
    try:
        data = line_schema.load(request.json)
    except ValidationError as err:
        app.logger.error(f'data {request.json}, err {err.messages}')
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)

    if not line:
        line = Line(line_id, data['coords'], user_id, quest_id)
        try:
            db.session.add(line)
            db.session.commit()
            return make_response(jsonify({"message": "Success", "status": "success"}), 201)
        except Exception as e:
            db.session.flush()
            app.logger.error(e)
            return make_response(jsonify({"message": "Error", "status": "error"}), 500)
    return make_response(jsonify({"message": "Line already exist", "status": "error"}), 422)


@line_bp.post('/lines/str:quest_id')
@jwt_required()
def create_lines(quest_id):
    user_id = get_jwt_identity()
    try:
        data = lines_schema.load(request.json)
    except ValidationError as err:
        app.logger.error(f'data {request.json}, err {err.messages}')
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)
    try:
        for line_id in data['ids']:
            line: Line = Line.query.get(line_id)
            if not line:
                line = Line(line_id, data['coords'], user_id, quest_id)
                db.session.add(line)
        db.session.commit()
        return make_response(jsonify({"message": "Success", "status": "success"}), 201)
    except Exception as e:
        db.session.flush()
        app.logger.error(e)
        return make_response(jsonify({"message": "Error", "status": "error"}), 500)


@line_bp.put('/lines/str:line_id')
@jwt_required()
def update_line(line_id):
    user_id = get_jwt_identity()
    line: Line = Line.query.get(line_id)
    try:
        data = line_schema.load(request.json)
    except ValidationError as err:
        app.logger.error(f'data {request.json}, err {err.messages}')
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)

    if not line or not line.owner(user_id):
        return make_response(jsonify({"message": "Line does not exist", "status": "error"}), 404)

    line.coords = data['coords']
    try:
        db.session.commit()
        return make_response(jsonify({"message": "Success", "status": "success"}), 201)
    except Exception as e:
        db.session.flush()
        app.logger.error(e)
        return make_response(jsonify({"message": "Error", "status": "error"}), 500)


@line_bp.delete('/lines/str:line_id')
@jwt_required()
def delete_line(line_id):
    user_id = get_jwt_identity()
    line: Line = Line.query.get(line_id)

    if not line or not line.owner(user_id):
        return make_response(jsonify({"message": "Line does not exist", "status": "error"}), 404)

    try:
        db.session.delete(line)
        return make_response(jsonify({"message": "Success", "status": "success"}), 200)
    except Exception as e:
        db.session.flush()
        app.logger.error(e)
        return make_response(jsonify({"message": "Error", "status": "error"}), 500)


@line_bp.delete('/lines/str:quest_id')
@jwt_required()
def delete_quest_lines(quest_id):
    user_id = get_jwt_identity()
    is_draft = request.args.get('is_draft', default=False, type=bool)

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


@line_bp.get('/lines/str:line_id')
@jwt_required()
def get_line(line_id):
    user_id = get_jwt_identity()
    line: Line = Line.query.get(line_id)

    if not line or not line.owner(user_id):
        return make_response(jsonify({"message": "Line does not exist", "status": "error"}), 404)

    return make_response(jsonify({"message": line.to_dict(), "status": "success"}), 200)


@line_bp.get('/lines')
@jwt_required()
def get_user_lines():
    user_id = get_jwt_identity()

    lines: list[Line] = User.query.get(user_id).lines

    ans = {line.id: line.to_dict() for line in lines}

    return make_response(jsonify({"lines": ans, "status": "success"}), 200)


@line_bp.get('/lines/str:quest_id')
@jwt_required()
def get_quest_lines(quest_id):
    user_id = get_jwt_identity()
    is_draft = request.args.get('is_draft', default=False, type=bool)

    quest: Quest = Quest.query.get(quest_id)

    if not quest or (is_draft and not quest.owner(user_id)):
        return make_response(jsonify({"message": "Quest does not exist", "status": "error"}), 404)

    lines: list[Line] = quest.lines

    ans = {line.id: line.to_dict() for line in lines}

    if is_draft:
        ans.update({line.id: line.to_dict() for line in quest.lines_draft})

    return make_response(jsonify({"lines": ans, "status": "success"}), 200)
