
# This file is intended to house all routes related to the Schedule API.
import threading
import sys
import time
import yaml
import os.path
import json

from flask import Blueprint, request, jsonify
from werkzeug.routing import NotFound
from marshmallow import ValidationError

from api.schemas.ScheduleJob import ScheduleJobSchema
from api.schemas.Response import ResponseMessages, post_response_job, post_response_vmaf
from api.scheduler.Job import Job, is_valid_jobid
from api.scheduler.JobDb import (
    get_job, get_all_jobs, get_active_jobs, get_completed_jobs, JobStatusTypes
)

from api.scheduler.VMAFDb import (
    insert_vmaf_db, get_vmaf_db, update_vmaf_status_db, update_vmaf_score_db,
    VMAFStatusTypes
)

import videolib.videoprocess as vp
from videolib.videoinfo import ffprobe_information_json, compute_vmaf_score
from videolib.encore_wrap import encore_transcode, concat_shots, remux_videos

config = yaml.safe_load(open("../config.yml"))["videolib"]


# Create a Blueprint called "schedule_api"
schedule_api_routes = Blueprint("schedule_api", __name__)


# Returns True if the provided path is a path to a video file.
def is_valid_video_file(file_path):
    file_exists = os.path.isfile(file_path)

    if not file_exists:
        return False

    # Get ffprobe information of the file in a dictionary.
    video_info_str = ffprobe_information_json(file_path)
    video_info = json.loads(video_info_str)

    # If the data returned by the ffprobe information is empty, the file is not
    # a video.
    if len(video_info) == 0:
        return False

    return True


# Used in order to process video jobs. Should be executed in a new thread.
def video_processing(job):
    print(f"Starting processing of job '{str(job.id)}' in new thread.")

    output_location = f"{job.output_location}{job.id}/"

    if not vp.make_dir(output_location):
        return False

    temp_location = f"{output_location}temp/"
    keep_location = f"{output_location}keep/"

    if not vp.make_dir(temp_location):
        return False

    if not vp.make_dir(keep_location):
        return False

    only_audio = f"{temp_location}only_audio.wav"
    vp.copy_audio(job.video_location, only_audio)

    container = job.video_location.split("/")
    container = container[len(container)-1]
    container = container.split(".")
    container = container[1]

    only_video = f"{temp_location}only_video.{container}"
    vp.copy_video(job.video_location, only_video)

    # Detect and split source video into shots.
    shot_names = vp.video_shot_split(
        only_video, temp_location, job.shot_parameter, job.shot_length)
    job.update_status(JobStatusTypes.Processing)

    # Transcode shots using Encore.
    shot_names, audio_locations = encore_transcode(
        job.id, config["encoreUrl"], shot_names, only_audio, temp_location)
    job.update_status(JobStatusTypes.Transcoding)

    # Mux transcoded shots together.
    video_locations = concat_shots(shot_names, temp_location)
    outputs_remux = remux_videos(
        video_locations, audio_locations, keep_location)
    job.update_status(JobStatusTypes.Completed)

    print(f"Done processing job '{job.id}'.")


def compute_vmaf(job):
    print(f"Computing VMAF score of job '{str(job.id)}' in a new thread.")

    # Insert job to db.
    insert_vmaf_db(job.id)

    # TODO: THIS NEEDS TO BE CHANGED IN THE FUTURE. HOWEVER THIS SHOULD WORK NOW.
    vmaf_score = compute_vmaf_score(job.video_location, os.path.join(
        job.output_location, job.id, "keep", "STEREO_remuxed_encore_x264_crf_23.mp4"))

    if vmaf_score == '':
        # Change status of vmaf compute to failed.
        update_vmaf_status_db(job.id, VMAFStatusTypes.Failed)

        print(f"Failed to compute VMAF score of job '{job.id}'.")
    else:
        # Change status of vmaf compute to completed.
        update_vmaf_status_db(job.id, VMAFStatusTypes.Completed)

        # Update score.
        update_vmaf_score_db(job.id, vmaf_score)

        print(f"Successfully computed VMAF score of job '{job.id}'.")


@schedule_api_routes.route("/schedule_job", methods=["POST"])
def schedule_jobs_route():

    # Get Request body from JSON
    request_data = request.json
    schema = ScheduleJobSchema()

    try:
        # Validate request body against schema data types
        result = schema.load(request_data)

        # Check if the file exists.
        if not is_valid_video_file(result["video_location"]):
            # If the file is not a valid video, send error message.
            return jsonify(post_response_job(False, "Not a valid input location."))

        # Create a new job instance (this also inserts the job into the database).
        job = Job(result["shot_parameter"], result["shot_length"],
                  result["video_location"], result["output_location"])

        handle = threading.Thread(target=video_processing, args=(job,))
        handle.start()

        return jsonify(post_response_job(
            True, ResponseMessages["job_sch_success"], job.id))

    except ValidationError as err:
        return jsonify(err.messages), 400


@schedule_api_routes.route("/job/<job_id>", methods=["GET"])
def get_job_route(job_id):

    if not is_valid_jobid(job_id):
        return "Not a valid job id", 400

    job = get_job(job_id)

    if job == None:
        return f"Job with id '{job_id}' does not exist", 400

    return job


@schedule_api_routes.route("/video_info/<job_id>", methods=["GET"])
def get_media_info_route(job_id):

    if not is_valid_jobid(job_id):
        return "Not a valid job id", 400

    job = Job.from_database(job_id)

    if job == None:
        return f"Job with id '{job_id}' does not exist", 400

    # Now we know that a job with a valid id exists.
    video_info = ffprobe_information_json(job.video_location)

    return video_info


@schedule_api_routes.route("/all_jobs", methods=["GET"])
def all_jobs_route():

    jobs = get_all_jobs()

    return jsonify(jobs)


@schedule_api_routes.route("/active_jobs", methods=["GET"])
def active_jobs_route():

    active_jobs = get_active_jobs()

    return jsonify(active_jobs)


@schedule_api_routes.route("/completed_jobs", methods=["GET"])
def completed_jobs_route():

    comp_jobs = get_completed_jobs()

    return jsonify(comp_jobs)


@schedule_api_routes.route("/vmaf_get/<job_id>", methods=["GET"])
def vmaf_get(job_id):

    if not is_valid_jobid(job_id):
        return "Not a valid job id", 400

    vmaf_data = get_vmaf_db(job_id)

    if vmaf_data is None:
        return jsonify(post_response_vmaf(False, ResponseMessages["vmaf_not_computed"]))
    else:
        return jsonify(post_response_vmaf(True, vmaf_data))


@schedule_api_routes.route("/vmaf_compute/<job_id>", methods=["GET"])
def vmaf_compute(job_id):

    if not is_valid_jobid(job_id):
        return "Not a valid job id", 400

    # Check if a job with job_id exists.
    job = Job.from_database(job_id)

    if job == None:
        return f"Job with id '{job_id}' does not exist", 400

    handle = threading.Thread(target=compute_vmaf, args=(job,))
    handle.start()

    return jsonify(post_response_vmaf(True, ResponseMessages["vmaf_computing"]))


# Serves as a 'catch-all' that raises a NotFound error for any path that is not
# defined in the routes above. A NotFound error is sent to the
# 'app_errorhandler', which is defined below.


@schedule_api_routes.route('/', defaults={'path': ''})
@schedule_api_routes.route('/<path:path>')
def catch_all(path):
    raise NotFound()


# Handles any NotFound errors by sending a json response message.
@schedule_api_routes.app_errorhandler(404)
def handle_404(e):
    return jsonify(error=str(e)), 404
