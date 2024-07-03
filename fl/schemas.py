from marshmallow import Schema, fields


class QuestSchema(Schema):
    quest_id = fields.UUID(required=True)
    title = fields.Str(required=True)


class UserAuth(Schema):
    user_data = fields.Str(required=True)
