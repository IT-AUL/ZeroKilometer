from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, make_response, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .models import db, User, Quest, Line
from .schemas import LineSchema  # , LinesSchema

load_dotenv()

line_schema = LineSchema()
# lines_schema = LinesSchema(many=True)

line_bp = Blueprint('line_bp', __name__)


# @line_bp.post('/lines/<uuid:quest_id>')
# @jwt_required()
# def create_line(quest_id):
#     quest_id = str(quest_id)
#     user_id = get_jwt_identity()
#     try:
#         data = line_schema.load(request.json)
#     except ValidationError as err:
#         app.logger.error(f'data {request.json}, err {err.messages}')
#         return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)
#
#     line = Line.query.get(data['line_id'])
#     quest: Quest = Quest.query.get(quest_id)
#
#     if not quest or not quest.owner(user_id):
#         return make_response(jsonify({"message": "Quest does not exist", "status": "error"}), 404)
#
#     if not line:
#         line = Line(data['line_id'], data['coords'])
#         quest.lines_draft.append(line)
#         User.query.get(user_id).lines.append(line)
#
#         try:
#             db.session.add(line)
#             db.session.commit()
#             return make_response(jsonify({"message": "Success", "status": "success"}), 201)
#         except Exception as e:
#             db.session.flush()
#             app.logger.error(e)
#             return make_response(jsonify({"message": "Error", "status": "error"}), 500)
#     return make_response(jsonify({"message": "Line already exist", "status": "error"}), 422)


@line_bp.post('/lines/<uuid:quest_id>')
@jwt_required()
def create_lines(quest_id):
    user_id = get_jwt_identity()
    quest: Quest = Quest.query.get(str(quest_id))
    if not quest or not quest.owner(user_id):
        return make_response(jsonify({"message": "Quest not found", "status": "error"}), 404)
    # data = line_schema.load(request.json, many=True)
    try:
        data = line_schema.load(request.json, many=True)
    except ValidationError as err:
        app.logger.error(f'data {request.json}, err {err.messages}')
        return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)
    for line_data in data:
        # line_data['line_id'] = str(line_data['line_id'])
        line: Line = Line.query.get(line_data['line_id'])
        if not line:
            line = Line(line_data['line_id'], line_data['coords'])

            user: User = User.query.get(user_id)
            user.lines.append(line)
            quest.lines_draft.append(line)
            db.session.add(line)
    db.session.commit()
    return make_response(jsonify({"message": "Success", "status": "success"}), 201)
    # try:
    #     for line_data in data:
    #
    #         print(line_data, type(line_data['line_id']))
    #         line_data['line_id'] = str(line_data['line_id'])
    #         line: Line = Line.query.get(str(line_data['line_id']))
    #         if not line:
    #             line = Line(line_data['line_id'], line_data['coords'])
    #
    #             user: User = User.query.get(user_id)
    #             user.lines.append(line)
    #             quest: Quest = Quest.query.get(quest_id)
    #             quest.lines_draft.append(line)
    #             print("egegeg")
    #             db.session.add(line)
    #     db.session.commit()
    #     return make_response(jsonify({"message": "Success", "status": "success"}), 201)
    # except Exception as e:
    #     db.session.flush()
    #     app.logger.error(e)
    #     print(e)
    #     return make_response(jsonify({"message": "Error", "status": "error"}), 500)


#
# @line_bp.put('/lines/str:line_id')
# @jwt_required()
# def update_line(line_id):
#     user_id = get_jwt_identity()
#     line: Line = Line.query.get(line_id)
#     try:
#         data = line_schema.load(request.json)
#     except ValidationError as err:
#         app.logger.error(f'data {request.json}, err {err.messages}')
#         return make_response(jsonify({"message": "Data is not valid", "status": "error"}), 400)
#
#     if not line or not line.owner(user_id):
#         return make_response(jsonify({"message": "Line does not exist", "status": "error"}), 404)
#
#     line.coords = data['coords']
#     try:
#         db.session.commit()
#         return make_response(jsonify({"message": "Success", "status": "success"}), 201)
#     except Exception as e:
#         db.session.flush()
#         app.logger.error(e)
#         return make_response(jsonify({"message": "Error", "status": "error"}), 500)
#

# @line_bp.delete('/lines/<uuid:line_id>')
# @jwt_required()
# def delete_line(line_id):
#     user_id = get_jwt_identity()
#     line: Line = Line.query.get(line_id)
#
#     if not line or not line.owner(user_id):
#         return make_response(jsonify({"message": "Line does not exist", "status": "error"}), 404)
#
#     try:
#         db.session.delete(line)
#         return make_response(jsonify({"message": "Success", "status": "success"}), 200)
#     except Exception as e:
#         db.session.flush()
#         app.logger.error(e)
#         return make_response(jsonify({"message": "Error", "status": "error"}), 500)


@line_bp.delete('/lines/<uuid:quest_id>')
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


# @line_bp.get('/lines/<uuid:line_id>')
# @jwt_required()
# def get_line(line_id):
#     user_id = get_jwt_identity()
#     line: Line = Line.query.get(line_id)
#
#     if not line or not line.owner(user_id):
#         return make_response(jsonify({"message": "Line does not exist", "status": "error"}), 404)
#
#     return make_response(jsonify({"line": line.to_dict(), "status": "success"}), 200)


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
    is_draft = request.args.get('is_draft', default=False, type=bool)

    quest: Quest = Quest.query.get(str(quest_id))

    if not quest or (is_draft and not quest.owner(user_id)):
        return make_response(jsonify({"message": "Quest does not exist", "status": "error"}), 404)

    lines: list[Line] = quest.lines

    ans = {line.id: line.to_dict() for line in lines}

    if is_draft:
        ans.update({line.id: line.to_dict() for line in quest.lines_draft})

    return make_response(jsonify({"lines": ans, "status": "success"}), 200)
