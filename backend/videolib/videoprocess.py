"""! This module is used for shot-based processing of a video"""
import os
import time
import subprocess as sp


###General functions#########################################################################
def make_dir(name):
    try:
        os.mkdir(name)
    except FileExistsError:
        return True
    except OSError as e:
        return False

    return True


def call_subprocess(command):
    """! Calls the terminal with the specified command

    @param command  The command to be called in the terminal

    @return The output from the terminal in text 
    """
    result = sp.run(command,
                    shell=True,
                    capture_output=True,
                    text=True)
    return result


def subprocess_error(result, where):
    """! Crashes the program if an error occured in subprocess and prints the error messages 

    @param result   The result from the call_subprocess() function
    @param where    Which function the error occured 
    """
    if result.returncode != 0:
        raise Exception(
            f"{where} failed with error code {result.returncode}", result.stderr)


###Used to find shots###############################################################################
def video_duration(video_location) -> str:
    """! The duration of the video

    @param video_location   The filepath to the video

    @return The video duration in millieseconds
    """
    command = f'ffprobe \
                -v error \
                -show_entries format=duration \
                -of default=noprint_wrappers=1:nokey=1 {video_location}'
    result = call_subprocess(command)

    subprocess_error(result, "Video duration")

    return result.stdout


def shot_detection(video_location, shot_parameter) -> str:
    """! The timestamps of the shots in the video

    @param video_location       The filepath to the video
    @param shot_parameter       The amount of change the algortihm considers. 
                                Value between 0-1 where 1 is the least amount of change. 

    @return The timestamps of shots
    """
    command = f'ffprobe \
                -hide_banner \
                -v panic \
                -show_entries packet=pts_time \
                -of default=noprint_wrappers=1:nokey=1 \
                -f lavfi "movie={video_location}, select=\'gt(scene,{shot_parameter})\'"'

    start_time = time.time()

    result = call_subprocess(command)

    duration = time.time() - start_time

    subprocess_error(result, "Scene detection")

    print(f"Shot detection done in: {duration} seconds")

    return result.stdout


def format_shot_detection(video_location, shot_parameter, shot_length=0) -> str:
    """! Formating the result from shot_detection  
    @param video_location       The filepath to the video
    @param shot_parameter       The amount of change the algortihm considers. 
                                Value between 0-1 where 1 is the least amount of change. 
    @param shot_length          The minimum length of a shot (number)

    @return The formatted version from shot_detection
    """
    detection = shot_detection(video_location, shot_parameter)

    # Need to add start of video
    start = "0.000000"
    # Need to add end of video a.k.a its duration
    duration = video_duration(video_location)

    detection = f"{start}\n{detection}{duration}"
    detection = detection.split()

    if shot_length == 0:
        return detection

    count = 0
    while count < len(detection)-1:
        diff = float(detection[count+1]) - float(detection[count])
        if diff < shot_length:
            if count == len(detection)-2:
                # can't delete last timestamp
                del detection[count]
            else:
                del detection[count+1]
        else:
            count += 1

    return detection


def trim_video(video_location, detection, output_location, video_location_name, container):
    """! The function called for trimming the video
    @param video_location           The filepath to the video
    @param detection                The formatted version of timestamps of the shots 
    @param output_location          The absolute path to the output directory
    @param video_location_name      The name of the video_location file
    @param container                The container format of the video      

    @return The absolute path to the output videos
    """

    video_paths = []

    command = 'ffmpeg -y -hide_banner -stats -v panic'

    for count in range(0, len(detection)-1):
        output_name = f'{video_location_name}-{count}.{container}'
        output_path = f'{output_location}{output_name}'

        command += f' -i {video_location}'
        command += f' -ss {detection[count]}'
        command += f' -to {detection[count+1]}'
        command += f' -c copy {output_path}'

        video_paths.append(output_path)

    result = call_subprocess(command)

    subprocess_error(result, "Trim video")

    # Used for debugging purpose
    errcheck = f'ffmpeg \
                -y \
                -v error \
                -i {video_location} \
                -f null \
                - 2>{output_location}error.log'
    result = call_subprocess(errcheck)

    subprocess_error(result, "Error check")

    return video_paths


def video_shot_split(video_location, output_location, shot_parameter, shot_length=0):
    """! Splits video based on shots where 
        shot_parameter determines how much change must 
        be in between frames for a shot change to occur

    @param video_location    The filepath to the video
    @param output_location   The absolute path to the output directory
    @param shot_parameter    The amount of change the algortihm considers. 
                             Value between 0-1 where 1 is the least amount of change. 
    @param shot_length       The minimum length of a shot

    @return The absolute path to the output videos
    """

    detection = format_shot_detection(
        video_location, shot_parameter, shot_length)

    output_location = f"{output_location}shots/"

    if not make_dir(output_location):
        return False

    format = video_location.split('/')
    format = format[len(format)-1]
    format = format.split('.')
    video_location_name = format[0]
    container = format[1]

    video_paths = trim_video(video_location, detection,
                             output_location, video_location_name, container)

    return video_paths


###Used to stitch the videos########################################################################
def create_concat_file(video_paths, concat_file):
    """! Creates the file to be used to concat videos into a video 

    @param video_paths  The absolute paths to all the splitted videos 
    @param concat_file  The type of file to be used to concat videos 
    """
    try:
        with open(f'{concat_file}', 'w') as f:
            for path in video_paths:
                f.write(f'file {path} \n')
    except Exception:
        print(f"Could not create: {concat_file}")


def stitch_video(video_paths, concat_file, output_name):
    """! Stitches videos together into a video 

    @param video_paths  The absolute paths to all the splitted videos 
    @param concat_file  The type of file to be used to concat videos 
    @param output_name  The output name of the stitched video 
    """

    create_concat_file(video_paths, concat_file)

    command = f'ffmpeg \
                -y \
                -hide_banner \
                -f concat \
                -safe 0 \
                -i {concat_file} \
                -c copy {output_name}'

    result = call_subprocess(command)

    subprocess_error(result, "Stitch video")

#####################################################################################################


def copy_audio(video_location, output_location):
    command = f"ffmpeg \
                -y -hide_banner \
                -i {video_location} \
                -map 0:a \
                -c copy {output_location}"

    result = call_subprocess(command)
    subprocess_error(result, "Copy audio")


def copy_video(video_location, output_location):
    command = f"ffmpeg \
                -y -hide_banner \
                -i {video_location} \
                -c:v copy -an {output_location}"

    result = call_subprocess(command)
    subprocess_error(result, "Copy video")


def mux_audio_video(video_location, audio_location, output_location):
    command = f"ffmpeg \
                -y -hide_banner \
                -i {video_location} \
                -i {audio_location} \
                -c copy {output_location}"

    # command =  f"ffmpeg \
    #            -y -hide_banner \
    #            -i {video_location} \
    #            -i {audio_location} \
    #            -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {output_location}"

    result = call_subprocess(command)
    subprocess_error(result, "Mux video and audio")


def bitrate_video(video_input):
    command = f"ffprobe \
                -v quiet \
                -select_streams v:0 \
                -show_entries stream=bit_rate \
                -of default=noprint_wrappers=1 {video_input}"

    result = call_subprocess(command)
    subprocess_error(result, "Bitrate video")
    result = result.stdout.split("=")
    result = float(result[1].strip())
    return result


def vmaf_score(encoded_video, original_video, json_path):
    command = f"ffmpeg \
                -hide_banner \
                -i {encoded_video} \
                -i {original_video} \
                -lavfi libvmaf=model_path='{json_path}':n_threads=4 \
                -f null -"

    result = call_subprocess(command)
    subprocess_error(result, "vmaf yolo")
    result = result.stderr.split(":")
    result = float(result[len(result)-1].strip())
    return result
