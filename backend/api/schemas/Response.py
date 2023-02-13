
from marshmallow import Schema, fields

# Lookup table for response messages.
ResponseMessages = {
    "job_sch_success": "Successfully scheduled job",
    "job_sch_fail": "Failed to scheduled job",
    "vmaf_not_computed": "VMAF not computed",
    "vmaf_computing": "Computing VMAF",
}


# Used to validate that all responses are on the form defined in the Schema
# class.
class ResponseSchema(Schema):
    success = fields.Boolean(required=True)
    payload = fields.Dict(required=True)


# Used to construct a post response and check its validity towards the Response
# schema.
def post_response(success, payload):
    schema = ResponseSchema()

    return schema.load({
        "success": success,
        "payload": payload
    })


# Constructs a response with job response payload.
def post_response_job(success, message, job_id=None):

    if job_id is None:
        return post_response(success, {
            "message": message,
        })
    else:
        return post_response(success, {
            "message": message,
            "job_id": job_id,
        })


# Constructs a response with job response payload.
def post_response_vmaf(success, message):
    return post_response(success, {
        "message": message,
    })
