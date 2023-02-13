
from marshmallow import Schema, fields
from marshmallow.validate import Range, OneOf


# This class represents what data MUST be received when scheduling a job.
class ScheduleJobSchema(Schema):
    type = fields.String(required=True, validate=OneOf(["file_path"]))
    shot_parameter = fields.Float(
        required=True, validate=Range(min=0.0, max=1.0))
    shot_length = fields.Float(
        required=True, validate=Range(min=0.0, max=1000.0))
    video_location = fields.String(required=True)
    output_location = fields.String(required=True)
