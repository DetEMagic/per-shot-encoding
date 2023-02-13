
import sys
import re
from videolib.videoprocess import call_subprocess, subprocess_error

# In this file are functions related to gathering/computing information about
# video files that should be/have been processed by videoprocess.py


# Outputs information from ffprobe in a json object (dictionary in python).
def ffprobe_information_json(video_location):
    command = f'ffprobe \
            -v quiet \
            -print_format json \
            -show_streams \
            -i {video_location}'

    result = call_subprocess(command)

    # TODO: Error handling

    return result.stdout


# Computes the VMAF score between two files. 'input_video' is the reference
# video and 'processed_video' is the distorted video. 'n_subsample' is to
# compute VMAF score for every n:th frame. If set to 1, every frame will be
# computed. Returns empty string on error or the VMAF score as a string on the
# format: # xx.dddddd
def compute_vmaf_score(input_video, processed_video, n_threads=2, n_subsample=1,
                       model_path='videolib/vmaf_models/vmaf_v0.6.1.json'):

    command = f"ffmpeg \
        -i {processed_video} \
        -i {input_video} \
        -lavfi libvmaf=model_path='{model_path}:n_threads={n_threads}:n_subsample={n_subsample}' \
        -f null -"

    result = call_subprocess(command)

    try:
        vmaf_search = re.search('VMAF score: \d+\.\d+', result.stderr)
        vmaf_score_str = vmaf_search.group(0)[-9:]
    except:
        return ''

    # TODO: Error handling

    return vmaf_score_str
