from backend.videolib.encore import Encore
from backend.videolib.encore_wrap import encore_transcode, concat_shots, create_normal, remux_videos
import backend.videolib.videoprocess as vp
import time
import json

from uuid import uuid4

def bitrate_vmaf_results(output_locations, original_source, vmaf_json):    
    result = {}
    for location in output_locations:
        print(location)
        name = location.split("/")
        name = name[len(name)-1]
        name = name.split(".")
        name = name[0]

        result[name] = {
            "bitrate": vp.bitrate_video(location),
            "vmaf": vp.vmaf_score(location, original_source, vmaf_json)
        }
        print(result)

    return result 

def calc_diff_percent(a, b):
    return (1-(float(a)/float(b)))*100

def calc_diff_results(result_remuxed, result_normal): 
    diff_bitrates = {}
    diff_vmafs = {}

    for (r_name, r_values), n_values in zip(result_remuxed.items(), result_normal.values()):
        diff_bitrates[r_name] = calc_diff_percent(r_values["bitrate"], n_values["bitrate"])
        diff_vmafs[r_name] = calc_diff_percent(r_values["vmaf"], n_values["vmaf"])
   
    diff = {
        "bitrates": diff_bitrates,
        "vmafs": diff_vmafs
    }

    return diff 
def create_json_file(dict, file):
    with open(file, "w") as json_file:
        json.dump(dict, json_file, indent=4)

def job(job_id, original_source, threshold, shot_length, url, vmaf_json_source, output_location, result_normal):

    start_time = time.time()
    output_location = f"{output_location}{job_id}/"

    if not vp.make_dir(output_location):
        return False
    
    temp_location = f"{output_location}temp/"
    keep_location = f"{output_location}keep/"
    
    if not vp.make_dir(temp_location):
        return False

    if not vp.make_dir(keep_location):
        return False

    only_audio = f"{temp_location}only_audio.wav"
    vp.copy_audio(original_source, only_audio)
    
    container = original_source.split("/")
    container = container[len(container)-1]
    container = container.split(".")
    container = container[1]

    only_video = f"{temp_location}only_video.{container}"
    vp.copy_video(original_source, only_video)
    split_time = time.time() - start_time

    shot_locations = vp.video_shot_split(only_video, temp_location, threshold, shot_length)
    shot_time = time.time() - start_time 
    shot_locations, audio_locations, encore_time = encore_transcode(job_id, url, shot_locations, only_audio, temp_location)

    #gibberish
    delay = time.time() - start_time
    delay -= encore_time
    start_time += delay
    encore_time = time.time() - start_time

    video_locations = concat_shots(shot_locations, temp_location)
    outputs_remux = remux_videos(video_locations, audio_locations, keep_location)
    remux_time = time.time() - start_time 

    plain = bitrate_vmaf_results(outputs_remux["STEREO"], original_source, vmaf_json_source)
    diff = calc_diff_results(plain, result_normal)

    result = {
        "split_time": split_time,
        "shot_time": shot_time,
        "encore_time": encore_time,
        "remux_time": remux_time,
        "diff": diff,
        "plain": plain 
    }
    
    return result

def main():
    test_videos = ["TESTVIDEO-1.mov"]
    for test_video in test_videos:
        split = test_video.split(".")
        test_video = split[0]
        container = split[1]
        
        output_location = "/shares/test_nas/shot-change/outputs/"
        original_source = f"/shares/test_nas/shot-change/videos/{test_video}.{container}"
        url = "https://videocore-encore.dev.aurora.svt.se"
        vmaf_json_source = "/shares/test_nas/shot-change/vmaf_v0.6.1.json"
        #vmaf_json_source = "/shares/test_nas/shot-change/vmaf_4k_v0.6.1.json"
        
    
        thresholds = [0.1, 0.2, 0.3, 0.4]
        shot_lengths = [0.5, 1, 1.5, 2, 2.5, 3, 6]
        #thresholds = [0.2]
        #shot_lengths = [1]
    
        output_location = f"{output_location}output-{test_video}/"
        if not vp.make_dir(output_location):
            return False
    
        result = {}
    
        encore = Encore(url)
        outputs_normal, normal_time = create_normal(encore, original_source, output_location)
        result_normal = bitrate_vmaf_results(outputs_normal, original_source, vmaf_json_source)
        result["normal"] = {
            "time": normal_time,
            "result":result_normal
        }
    
        result["per_shot"] = {}
    
        for threshold in thresholds:
            for shot_length in shot_lengths:
                job_id = str(uuid4())
                job_result = job(job_id, original_source, threshold, shot_length, url, vmaf_json_source, output_location, result_normal)
                result["per_shot"][job_id] = {
                    "threshold": threshold,
                    "shot_length": shot_length,
                    "result": job_result
                }
                create_json_file(result, f"./results/{test_video}-result.txt")
    
        print("TIDEN: ", time.time() - start_time)
    
    
if __name__ == "__main__":
    main()
