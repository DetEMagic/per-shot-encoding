from asyncore import poll
import time
import yaml
from videolib.videoprocess import make_dir, stitch_video, mux_audio_video
from videolib.encore import Encore
from datetime import datetime

config = yaml.safe_load(open("../config.yml"))["videolib"]


def create_video_jobs(external_id, encore, video_paths, base_dir, base_name="encore",
                      profile="shot-change-video-only", progress_callback_uri="", priority="0",
                      debug_overlay="false", log_context={}, paramtype="Video", params={}):

    if not make_dir(base_dir):
        return False

    job_ids = []

    for count in range(0, len(video_paths)):

        id = f"v-{count}"

        output_dir = f"{base_dir}{id}"
        if not make_dir(output_dir):
            return False

        data = {
            "externalId": id,
            "profile": profile,
            "outputFolder": output_dir,
            "baseName": base_name,
            "priority": priority,
            "debugOverlay": debug_overlay,
            "logContext": log_context,
            "inputs": [{
                "type": paramtype,
                "uri": video_paths[count],
                "params": params
            }]
        }

        response = encore.create_job(data)

        if not response:
            # TODO add some callback function that reports back number of jobs that was created
            # wait 3 seconds before trying again
            count -= 1
            time.sleep(3)
            continue
        else:
            job_ids.append(response["id"])

    return job_ids


def poll_jobs(encore, encore_ids, delay=3):

    while True:
        # poll every 3 second
        time.sleep(delay)
        responses = []

        for job_id in encore_ids:
            response = encore.get_job(job_id)
            # if response was bad we want to start from the beginning
            if not response:
                break

            if response["status"] == "SUCCESSFUL":
                responses.append(response)

            if response["status"] == "FAILED":
                return response["message"]

        # if all responses was successful terminate the loop
        if len(encore_ids) == len(responses):
            return responses


def get_outputs_locations(responses):
    output_locations = []
    for i in range(0, len(responses)):
        location = 0
        for output in responses[i]["output"]:
            if output["type"] == "VideoFile":
                if i == 0:
                    output_locations.append([output["file"]])
                else:
                    output_locations[location].append(output["file"])
                    location += 1

    return output_locations


def get_output_locations(response, type):
    output_locations = []
    for output in response["output"]:
        if output["type"] == type:
            output_locations.append(output["file"])

    return output_locations


def concat_shots(video_locations, base_dir):

    concat_txt_dir = f"{base_dir}concat/"
    remuxed_dir = f"{base_dir}remuxed/"

    if not make_dir(concat_txt_dir):
        return False

    if not make_dir(remuxed_dir):
        return False

    remuxed_locations = []

    for locations in video_locations:
        # only need to get the name of the video once
        video = locations[0].split("/")
        video = video[len(video)-1]
        # remove container ex (.mp4)
        name = video.split(".")
        name = name[0]

        concat = f"{concat_txt_dir}concat_{name}.txt"
        output_dir = f"{remuxed_dir}remuxed_{video}"
        stitch_video(locations, concat, output_dir)
        remuxed_locations.append(output_dir)

    return remuxed_locations


def remux_videos(video_locations, audio_locations, output_location):
    outputs = {}
    for audio in audio_locations:
        audio_name = audio.split("/")
        audio_name = audio_name[len(audio_name)-1]
        # remove container
        audio_name = audio_name.split(".")
        audio_name = audio_name[0]
        # remove base_name from encore
        audio_name = audio_name.split("_")
        audio_name = audio_name[1]
        same_audio = []

        for video in video_locations:
            # börjar med stereo bara
            video_name = video.split("/")
            video_name = video_name[len(video_name)-1]

            output_remuxed = f"{output_location}{audio_name}_{video_name}"
            mux_audio_video(video, audio, output_remuxed)
            same_audio.append(output_remuxed)

        outputs[audio_name] = same_audio

    return outputs


def create_normal(encore, source, base_dir):

    normal_dir = f"{base_dir}normal"

    if not make_dir(normal_dir):
        return False

    while True:
        data = {
            "externalId": "normal",
            "profile": "shot-change-video",
            "outputFolder": normal_dir,
            "baseName": "normal",
            "progressCallbackUri": "",
            "priority": "0",
            "debugOverlay": "false",
            "logContext": {},
            "inputs": [{
                "type": "AudioVideo",
                "uri": source,
                "params": {}
            }]
        }

        response = encore.create_job(data)

        if not response:
            # TODO add some callback function that reports back number of jobs that was created
            # wait 3 seconds before trying again
            time.sleep(3)
            continue
        else:
            print("normal", response["id"])
            response = poll_jobs(encore, [response["id"]])[0]
            outputs = get_output_locations(response, "VideoFile")
            encore_time = calc_time(
                response["startedDate"], response["completedDate"])
            return outputs, encore_time


def create_audio_job(job_id, encore, audio_location, output_dir):

    if not make_dir(output_dir):
        return False

    while True:
        data = {
            "externalId": f"{job_id}-a",
            "profile": "audio-only",
            "outputFolder": output_dir,
            "baseName": "audio",
            "priority": "0",
            "debugOverlay": "false",
            "logContext": {},
            "inputs": [{
                "type": "Audio",
                "uri": audio_location,
                "params": {}
            }]
        }

        response = encore.create_job(data)

        if not response:
            # TODO add some callback function that reports back number of jobs that was created
            # wait 3 seconds before trying again
            time.sleep(3)
            continue
        else:
            return response["id"]


def calc_time(start_date, completed_date):
    start_date = datetime.fromisoformat(start_date)
    completed_date = datetime.fromisoformat(completed_date)
    return (completed_date-start_date).total_seconds()


def encore_transcode(job_id, url, video_paths, audio_path, output_dir):

    encore = Encore(url)

    audio_dir = f"{output_dir}encoded_audio"
    shots_dir = f"{output_dir}encoded_shots/"

    # TODO fixa error handling genom hela skiten
    audio_id = create_audio_job(job_id, encore, audio_path, audio_dir)
    video_ids = create_video_jobs(job_id, encore, video_paths, shots_dir)

    audio_response = poll_jobs(encore, [audio_id])[0]
    audio_locations = get_output_locations(audio_response, "AudioFile")

    video_responses = poll_jobs(encore, video_ids)
    video_locations = get_outputs_locations(video_responses)

    # encore_time = calc_time(audio_response["startedDate"],
    #                        max([response["completedDate"] for response in video_responses]))

    return video_locations, audio_locations
