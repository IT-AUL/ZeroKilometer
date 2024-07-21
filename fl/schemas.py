from marshmallow import Schema, fields


class QuestSchema(Schema):
    quest_id = fields.UUID(required=True)
    title = fields.Str(required=True)


class UserAuth(Schema):
    id = fields.Integer(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=False)
    username = fields.Str(required=False)
    photo_url = fields.Str(required=False)
    auth_date = fields.Integer(required=False)
    hash = fields.Str(required=True)


class QuestRate(Schema):
    quest_id = fields.UUID(required=True)
    rating = fields.Integer(required=True)
