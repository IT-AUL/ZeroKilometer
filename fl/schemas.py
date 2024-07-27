from marshmallow import Schema, fields, validates_schema, ValidationError, post_load

from fl.models import Language, Type


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


class CreateLocationSchema(Schema):
    location_id = fields.UUID(required=True, allow_none=False)

    @post_load
    def convert_id_to_string(self, data, **kwargs):
        data['location_id'] = str(data['location_id'])
        return data


class CreateLocationsSchema(Schema):
    locations_id = fields.List(fields.UUID, required=True, allow_none=False)

    @post_load
    def convert_ids_to_string(self, data, **kwargs):
        for i in range(len(data['locations_id'])):
            data['locations_id'][i] = str(data['locations_id'][i])
        return data


class UpdateLocationSchema(Schema):
    title = fields.Str(required=False, allow_none=True, missing=None, )
    coords = fields.Str(required=False, allow_none=True, missing=None)
    description = fields.Str(required=False, allow_none=True, missing=None)
    lang = fields.Enum(Language, required=False, allow_none=True, missing=None)


class LocationSchema(Schema):
    location_id = fields.UUID(required=True, allow_none=False)
    title = fields.Str(required=False, allow_none=True, missing=None, )
    coords = fields.Str(required=False, allow_none=True, missing=None)
    description = fields.Str(required=False, allow_none=True, missing=None)
    lang = fields.Enum(Language, required=False, allow_none=True, missing=None)

    @post_load
    def convert_ids_to_string(self, data, **kwargs):
        data['location_id'] = str(data['location_id'])
        return data


# class UpdateLocationsSchema(Schema):


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
