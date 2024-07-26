from marshmallow import Schema, fields, validates_schema, ValidationError

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

    title = fields.Str(required=False, allow_none=True, missing=None)
    coords = fields.Str(required=False, allow_none=True, missing=None)
    description = fields.Str(required=False, allow_none=True, missing=None)
    lang = fields.Enum(Language, required=False, allow_none=True, missing=None)


class LineSchema(Schema):
    coords = fields.List(fields.Tuple((fields.Float(), fields.Float())), required=False, allow_none=True, default=None,
                         missing=None)


class LinesSchema(Schema):
    ids = fields.List(fields.Str, required=False, allow_none=True, default=None)
    lines = fields.List(fields.Nested(LineSchema()), required=False, allow_none=True, default=None)

    @validates_schema
    def validate_ids_length(self, data, **kwargs):
        if len(data['lines']) != len(data['ids']):
            raise ValidationError("The number of lines must match the number of IDs")
