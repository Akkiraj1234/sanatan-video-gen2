from typing import List, Tuple, Literal, Optional
from video_gen.editor.media import Video, Audio
from video_gen.editor.ffmpeg import ffmpeg
from video_gen.utils import assets

def get_size_code(
    total_duration: int,
    required_duration: int,
    videoid: str,
    frame_rate:int,
    custom_width: int = 720, 
    custom_height: int = 1080
) -> str:
    loop_count = required_duration // total_duration
    
    if required_duration % total_duration != 0:
        loop_count += 1
        
    loop_cmd = f"loop={int(loop_count)}:1:0"
    trim_cmd = f"trim=duration={required_duration}"
    fps_cmd = f"fps={frame_rate}"
    scale_cmd = f"scale={custom_width}x{custom_height}"
    
    return f"{videoid}{loop_cmd},{trim_cmd},{fps_cmd},{scale_cmd}[out];"


def Ken_Burns(
    input_path: Video,  
    output_path: str,
    total_duration: int,
    zoom_direction: Literal['top', 'bottom', 'center'] = 'center',
    target_zoom: float = 1.5,
    custom_width: int = 720,
    custom_height: int = 1080,
    fps: int = 24,
    **kwargs
) -> None:
    """
    Generates the Ken Burns effect on a video and processes it with ffmpeg.

    Args:
        media (Video): The input media object.
        output_file (str): The path where the output video will be saved.
        total_duration (int): The total duration for the Ken Burns effect in seconds.
        zoom_direction (Literal['top', 'bottom', 'center'], optional): The direction of zoom. Defaults to 'top'.
        target_zoom (float, optional): The target zoom level. Defaults to 1.5.
        custom_width (int, optional): The width of the output video. Defaults to 1280.
        custom_height (int, optional): The height of the output video. Defaults to 800.
        fps (int, optional): The frame rate of the video. Defaults to 24.

    Returns:
        None: Runs the ffmpeg command to generate the video.
    """
    cmd = ['-i', str(input_path)]

    # Get the size code filter to loop and trim video
    filter_complex = []
    filter_complex.append(
        get_size_code(input_path.duration, total_duration, '[0:v]', fps, custom_width, custom_height) #always [out]
    )
    
    # Calculate the zoom factor
    total_fps = fps * total_duration
    zoom_ipf = round((target_zoom - 1) / total_fps, 5)  # Zoom increment per frame
    zoompan, d= f"zoompan=z='1+{zoom_ipf}*on'", 1
    
    # Set the zoom direction
    if zoom_direction == 'center':
        zoompan_filter = f"[out]{zoompan}:x='(1-1/zoom)*iw/2':y='(1-1/zoom)*ih/2':d={d}:s={custom_width}x{custom_height}"
    elif zoom_direction == 'top':
        zoompan_filter = f"[out]{zoompan}:d={d}:s={custom_width}x{custom_height}"
    elif zoom_direction == 'bottom':
        zoompan_filter = f"[out]{zoompan}:x='(1-1/zoom)*iw/2':y='(1-1/zoom)*(ih-ih/4)':d={d}:s={custom_width}x{custom_height}"

    filter_complex.append(zoompan_filter)

    # Combine filters into one string
    filter_complex_str = ''.join(filter_complex)

    # Create the final ffmpeg command
    total_command = [
        *cmd, 
        '-filter_complex', f'{filter_complex_str}', 
        '-c:v', 'libx264', 
        '-pix_fmt', 'yuv420p', 
        '-y', output_path
    ]
    # print(' '.join(total_command),'\n\n')

    # Run the command using subprocess
    ffmpeg.run('ffmpeg', total_command)
    return Video(output_path)


def Ken_Burns_reversed(media:Video) -> Video:
    pass


def copy_video(input_path: str, output_path: str, **kwargs):
    cmd = [
        "-i", str(input_path), 
        "-c", "copy", "-map", "0", 
        "-y", output_path
    ]
    ffmpeg.run('ffmpeg', cmd)
    return Video(output_path)


class effect_get:
    
    registry = {
        "Ken_Burns_middle": None, 
        "Ken_Burns_top":Ken_Burns,
        'no_effect':copy_video
    }
    
    @staticmethod
    def get(key:str):
        value = effect_get.registry.get(key,None)
        
        if value is None:
            value = copy_video
        
        return value