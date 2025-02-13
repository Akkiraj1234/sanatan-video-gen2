import subprocess
import shlex
from tqdm import tqdm
import os, sys

# its tells how we can add a custom progress bar and also
# and also how to lower the cpu load that's it.

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video_gen_path = os.path.join(path,"src")
sys.path.append(video_gen_path)

from video_gen.utility import DIR

def get_duration(input_file):
    """Get video duration using ffprobe"""
    cmd = f"ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 -i {input_file}"
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return float(result.stdout)

def convert_video():
    input_file = os.path.join(DIR,"media","video","video3.mp4")
    output_file = os.path.join(DIR,"media","video","output.mp4")
    
    # Get total duration
    duration = get_duration(input_file)
    
    # FFmpeg command (modified for progress parsing)
    # cmd = f"""
    # ffmpeg -threads 2 -hide_banner -loglevel error -progress pipe:1
    # -i {input_file} -vf "scale=1920:1080:flags=lanczos"
    # -c:v libx264 -c:a aac -y {output_file}
    # """
    cmd = f"""
    ffmpeg -hide_banner -loglevel error -progress pipe:1 \
    -i {input_file} \
    -threads:v 2 -threads:a 2 \
    -filter_complex_threads 2 \
    -vf "scale=1920:1080:flags=lanczos:threads=2" \
    -c:v libx264 -x264-params threads=2 \
    -c:a aac -y {output_file}
    """
    # cmd = f"""
    # ffmpeg -hwaccel cuda -i {input_file} \
    # -c:v h264_nvenc -preset slow \
    # ...
    # """
    # Run FFmpeg and parse progress
    with tqdm(total=duration, unit="s", desc="Processing", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        process = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        current_duration = 0
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            # Parse FFmpeg's progress output
            if "out_time_ms" in line:
                time_str = line.split("=")[1].strip()
                if time_str == 'N/A':
                    continue
                
                current_duration = round(float(time_str) / 1_000_000,2)  # Convert μs to seconds)
                pbar.n = current_duration
                pbar.refresh()

        process.wait()
        if process.returncode != 0:
            print("Error:", process.stderr.read())


convert_video()