from marshmallow import Schema, fields

from fl.models import Language, Type


# class QuestSchema(Schema):
#     quest_id = fields.UUID(required=True)
#     title = fields.Str(required=True)


class UserAuth(Schema):
    id = fields.Integer(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=False)
    username = fields.Str(required=False)
    photo_url = fields.Str(required=False)
    auth_date = fields.Integer(required=False)
    hash = fields.Str(required=True)


class QuestRate(Schema):
    quest_id = fields.Str(required=True)
    rating = fields.Integer(required=True)


class QuestSchema(Schema):
    quest_id = fields.Str(required=True)

    title = fields.Str(required=False, allow_none=True, missing=None)
    description = fields.Str(required=False, allow_none=True, missing=None)
    lang = fields.Enum(Language, required=False, allow_none=True, missing=None)
    type = fields.Enum(Type, required=False, allow_none=True, missing=None)

    locations = fields.List(fields.Str, required=False, allow_none=True, missing=[], default=[])


class LocationSchema(Schema):
    location_id = fields.Str(required=True)

    title = fields.Str(required=False, allow_none=True, missing=None)
    coords = fields.Str(required=False, allow_none=True, missing=None)
    description = fields.Str(required=False, allow_none=True, missing=None)
    lang = fields.Enum(Language, required=False, allow_none=True, missing=None)
