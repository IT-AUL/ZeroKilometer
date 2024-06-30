from marshmallow import Schema, fields


class QuestSchema(Schema):
    quest_id = fields.UUID(required=True)
    name = fields.Str(required=True)
    plot = fields.Dict(required=True)


class UserAuth(Schema):
    user_data = fields.Str(required=True)
