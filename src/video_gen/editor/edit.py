from __future__ import annotations
from typing import List, Optional, Dict, Tuple, Union
from pathlib import Path
import logging, json, subprocess, os, tempfile
from video_gen.editor.ffmpeg import FFmpeg, get_MediaInfo
from video_gen.editor.media import Video, Audio, Image

logger = logging.getLogger(__name__)

class Editor:
    def __init__(self):
        self.ffmpeg = FFmpeg()
        self.media_classes = {
            'video': Video,
            'audio': Audio,
            'image': Image
        }

    def _create_media_object(self, file_path: str) -> Union[Video, Audio, Image, None]:
        """Instantiate appropriate media object based on file type"""
        try:
            info = get_MediaInfo(file_path)
            media_type = info['summary']['media_type']
            return self.media_classes[media_type](file_path)
        except Exception as e:
            logger.error(f"Failed to create media object: {e}")
            return None

    # --------------------------
    # Core Editing Operations
    # --------------------------

    def execute_ffmpeg(self, command_args: List[str], output_path: str) -> bool:
        """Generic FFmpeg command executor with media object validation"""
        try:
            self.ffmpeg.run('ffmpeg', command_args + [str(output_path)])
            return Path(output_path).exists()
        except Exception as e:
            logger.error(f"FFmpeg operation failed: {e}")
            return False

    # --------------------------
    # Video Operations
    # --------------------------

    def process_video(self, video: Video, command_args: List[str], output_path: str) -> Optional[Video]:
        """Generic video processing template"""
        if not self.execute_ffmpeg(["-i", str(video.file_path)] + command_args, output_path):
            return None
        return self._create_media_object(output_path)

    def trim(self, video: Video, output_path: str, start: float, end: float) -> Optional[Video]:
        """Trim video using copy codecs for speed"""
        return self.process_video(
            video,
            [
                "-ss", str(start),
                "-to", str(end),
                "-c:v", "copy",
                "-c:a", "copy",
                "-avoid_negative_ts", "make_zero"
            ],
            output_path
        )

    def concatenate(self, inputs: List[Union[Video, Audio]], output_path: str) -> Optional[Video]:
        """Concatenate multiple media files"""
        list_file = Path("concat_list.txt")
        
        try:
            # Generate concat list respecting media types
            with list_file.open('w') as f:
                for media in inputs:
                    f.write(f"file '{media.file_path}'\n")
            
            return self.process_video(
                inputs[0],
                [
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(list_file),
                    "-c", "copy"
                ],
                output_path
            )
        finally:
            list_file.unlink(missing_ok=True)

    # --------------------------
    # Audio Operations
    # --------------------------

    def extract_audio(self, video: Video, output_path: str) -> Optional[Audio]:
        """Extract audio stream from video"""
        if self.execute_ffmpeg([
            "-i", str(video.file_path),
            "-q:a", "0",
            "-map", "a"
        ], output_path):
            return self._create_media_object(output_path)
        return None

    def normalize_audio(self, audio: Audio, output_path: str) -> Optional[Audio]:
        """Normalize audio levels using loudnorm filter"""
        return self._process_audio(
            audio,
            ["-af", "loudnorm=I=-16:LRA=11:TP=-1.5"],
            output_path
        )

    # --------------------------
    # Image Operations
    # --------------------------

    def create_slideshow(self, images: List[Image], output_path: str, 
                        duration: float = 5.0, fps: int = 30) -> Optional[Video]:
        """Create video slideshow from images"""
        inputs = []
        filters = []
        
        for idx, image in enumerate(images):
            inputs.extend(["-loop", "1", "-t", str(duration), "-i", str(image.file_path)])
            filters.append(f"[{idx}:v]scale=1280:720:force_original_aspect_ratio=decrease[v{idx}];")
            filters.append(f"[v{idx}]setsar=1[v{idx}];")
        
        filters.append(f"{''.join(f'[v{i}]' for i in range(len(images)))}concat=n={len(images)}:v=1[v]")
        
        return self.process_video(
            images[0],
            inputs + ["-filter_complex", "".join(filters)],
            output_path
        )

    # --------------------------
    # Advanced Operations
    # --------------------------

    def add_subtitles(self, video: Video, subtitle_path: str, 
                     output_path: str, style: Dict[str, str] = None) -> Optional[Video]:
        """Burn subtitles into video with optional styling"""
        style_str = ""
        if style:
            style_str = ":force_style='" + ",".join(
                f"{k}={v}" for k, v in style.items()
            ) + "'"
            
        return self.process_video(
            video,
            [
                "-vf", f"subtitles={subtitle_path}{style_str}",
                "-c:a", "copy"
            ],
            output_path
        )

    def apply_filterchain(self, media: Union[Video, Audio], output_path: str,
                         filter_complex: str) -> Optional[Union[Video, Audio]]:
        """Apply custom filter complex to media"""
        if isinstance(media, Video):
            return self.process_video(
                media,
                ["-filter_complex", filter_complex],
                output_path
            )
        elif isinstance(media, Audio):
            return self._process_audio(
                media,
                ["-filter_complex", filter_complex],
                output_path
            )
        return None

    # --------------------------
    # Utility Methods
    # --------------------------

    def _process_audio(self, audio: Audio, command_args: List[str], 
                      output_path: str) -> Optional[Audio]:
        """Generic audio processing template"""
        if not self.execute_ffmpeg(["-i", str(audio.file_path)] + command_args, output_path):
            return None
        return self._create_media_object(output_path)

    def generate_video_clip(self, audio: Audio, timestamps: List[Tuple[float, float, str]], 
                           images: List[Image], output_path: Path) -> Optional[Video]:
        """
        Generate video clip from images synchronized with audio using timestamps
        Args:
            audio: Audio object to use as soundtrack
            timestamps: List of (start_ms, end_ms, text) for each image
            images: List of Image objects in order
            output_path: Output video path
        """
        if len(timestamps) != len(images):
            logger.error("Mismatch between timestamps and images count")
            return None

        with tempfile.TemporaryDirectory() as tmpdir:
            list_file = Path(tmpdir) / "concat.txt"
            
            # Generate concat list with durations
            with list_file.open('w') as f:
                for idx, ((start, end, _), image) in enumerate(zip(timestamps, images)):
                    duration = (end - start) / 1000  # Convert ms to seconds
                    f.write(f"file '{image.file_path}'\n")
                    f.write(f"duration {duration:.3f}\n")
                
                # Repeat last frame to match audio length
                f.write(f"file '{images[-1].file_path}'\n")

            # Build FFmpeg command
            cmd = [
                "-f", "concat", "-safe", "0", "-i", str(list_file),
                "-i", str(audio.file_path),
                "-c:v", "libx264", "-preset", "fast",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-y", str(output_path)
            ]

            if not self.ffmpeg.run('ffmpeg',cmd):
                return None

            return self._create_media_object(output_path)

    def concatenate_transparent_videos(self, videos: List[Video], output_path: Path) -> Optional[Video]:
        """Concatenate videos with alpha channel"""
        if len(videos) < 2:
            logger.error("Need at least 2 videos for concatenation")
            return None

        try:
            filter_chains = []
            inputs = []
            
            for idx, video in enumerate(videos):
                inputs.extend(["-i", str(video.file_path)])
                filter_chains.append(
                    f"[{idx}:v]format=rgba,scale=1080:1920:force_original_aspect_ratio=decrease[v{idx}];"
                )

            concat_inputs = "".join(f"[v{i}]" for i in range(len(videos)))
            filter_complex = (
                "".join(filter_chains) +
                f"{concat_inputs}concat=n={len(videos)}:v=1:a=0[vout];"
                "amix=inputs=1[aout]"
            )

            return self.process_video(
                videos[0],
                inputs + [
                    "-filter_complex", filter_complex,
                    "-map", "[vout]",
                    "-map", "[aout]",
                    "-c:v", "prores_ks",
                    "-c:a", "aac",
                    "-y", str(output_path)
                ],
                output_path
            )
        except Exception as e:
            logger.error(f"Transparent concatenation failed: {e}")
            return None

    def overlay_videos(self, base_video: Video, overlay_video: Video, 
                      output_path: Path, position: Tuple[int, int] = (0, 0)) -> Optional[Video]:
        """Overlay one video on top of another"""
        return self.process_video(
            base_video,
            [
                "-i", str(overlay_video.file_path),
                "-filter_complex", f"[0:v][1:v]overlay={position[0]}:{position[1]}",
                "-c:a", "copy",
                "-y", str(output_path)
            ],
            output_path
        )

    def get_duration(self, media: Union[Video, Audio]) -> Optional[float]:
        """Get duration of media file in seconds"""
        try:
            info = get_MediaInfo(str(media.file_path))
            return info['summary']['duration']
        except Exception as e:
            logger.error(f"Failed to get duration: {e}")
            return None


def generate_video_clip(audio_path, timestamps, image_folder, output_video_path):
    """
    Generate a video clip using audio, timestamps, and image frames.
    
    Args:
    - audio_path (str): Path to the audio file.
    - timestamps (list of tuples): List of tuples containing (start_time, end_time, text) for each frame.
    - image_folder (str): Folder where the image frames are stored.
    - output_video_path (str): Path where the final video will be saved.
    
    Returns:
    - str: Path to the final video.
    """
    
    # Prepare a temporary file to list images and their durations
    image_list_file = os.path.join(image_folder, "image_list.txt")
    with open(image_list_file, 'w') as f:
        for i, (start, end, text) in enumerate(timestamps, 1):
            duration = (end - start) / 1000.0  # Convert milliseconds to seconds
            image_path = os.path.join(image_folder, f"frame_{str(i).zfill(3)}.png")
            f.write(f"file '{image_path}'\n")
            f.write(f"duration {duration:.3f}\n")  # Ensure duration is in seconds (floating-point)
    
    # Add the last image to hold until audio ends
    last_image_path = os.path.join(image_folder, f"frame_{str(len(timestamps)).zfill(3)}.png")
    with open(image_list_file, 'a') as f:
        f.write(f"file '{last_image_path}'\n")
    
    # Generate the final video using ffmpeg
    # command = [
    #     'ffmpeg', '-f', 'concat', '-safe', '0', '-i', image_list_file, '-i', audio_path,
    #     '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', '-shortest', output_video_path
    # ]
    command = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', image_list_file, '-i', audio_path,
        '-c:v', 'qtrle', '-pix_fmt', 'argb', '-c:a', 'aac', '-strict', 'experimental',
        '-shortest', output_video_path
    ]
    subprocess.run(command, check=True)
    
    # Cleanup: Remove the image list file and frames
    os.remove(image_list_file)
    for i in range(1, len(timestamps) + 1):
        frame_path = os.path.join(image_folder, f"frame_{str(i).zfill(3)}.png")
        if os.path.exists(frame_path):
            os.remove(frame_path)
    os.remove(audio_path)
    
    # Return the path to the final video
    return output_video_path


def concatenate_transparent_videos(video1, video2, output):
    try:
        # Construct the FFmpeg command to concatenate videos and mix audios
        command = [
            'ffmpeg',
            '-i', video1,  # Input video 1
            '-i', video2,  # Input video 2
            '-filter_complex', (
                '[0:v]format=rgba,scale=1080:1920[video1];'  # Scale first video
                '[1:v]format=rgba,scale=1080:1920[video2];'  # Scale second video
                '[0:a]atrim=start=0[audio1];'  # Trim audio from first video
                '[1:a]atrim=start=0[audio2];'  # Trim audio from second video
                '[video1][video2]concat=n=2:v=1:a=0[v];'  # Concatenate the video streams only
                '[audio1][audio2]concat=n=2:v=0:a=1[audio_output];'  # Concatenate the audio streams
            ),
            '-map', '[v]',  # Map the final video stream
            '-map', '[audio_output]',  # Map the final audio stream
            '-c:v', 'prores_ks',  # Encode the video stream using ProRes codec
            '-c:a', 'aac',  # Encode the audio stream using aac codec
            '-y',  # Overwrite output file if it exists
            output
        ]

        # Run the FFmpeg command
        subprocess.run(command, check=True)
        return output

    except subprocess.CalledProcessError as e:
        pass
                
def get_video_duration(file_path):
    try:
        # Get the duration of the video file in seconds
        command = [
            'ffmpeg',
            '-i', file_path,
            '-v', 'quiet',  # Suppress unnecessary output
            '-print_format', 'json',  # Print output in JSON format
            '-show_entries', 'format=duration'  # Extract only duration
        ]
        
        # Run the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Parse the JSON output to extract duration
        output_json = json.loads(result.stdout)
        duration = float(output_json['format']['duration'])  # Duration is in seconds
        return duration
    
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: {e}")
        print(f"stderr: {e.stderr}")
        return None  # Return None if there's an error

def overlay_and_trim_video(mov_file, mp4_file, output_file):
    try:
        # Construct the FFmpeg command to overlay the MOV file (with video and audio) on top of the MP4 file
        command = [
            'ffmpeg',
            '-i', mp4_file,  # Input MP4 file
            '-i', mov_file,  # Input MOV file
            '-filter_complex', '[0:v][1:v]overlay=0:0[v];[1:a]anull[a]',  # Overlay MOV video on MP4 video and use MOV audio
            '-map', '[v]',  # Map the video stream from the overlay filter
            '-map', '[a]',  # Map the audio stream from the MOV file
            '-c:v', 'libx264',  # Encode the video using libx264
            '-c:a', 'aac',  # Encode the audio using AAC
            '-y',  # Overwrite the output file if it exists
            output_file  # Output file path
        ]
        
        # Run the FFmpeg command
        subprocess.run(command, check=True)

        print(f"Output video successfully created at: {output_file}")

    except subprocess.CalledProcessError as e:
        print("Error while processing the video:", e)

        
def concatenate_videos(video1, video2, output):
    try:
        # Check if both videos have audio and video
        command = [
            'ffmpeg',
            '-i', video1,  # Input video 1
            '-i', video2,  # Input video 2
            '-filter_complex', (
                '[0:v][1:v]concat=n=2:v=1:a=0[v];'  # Concatenate only video
            ),
            '-map', '[v]',  # Map the final video stream
            '-c:v', 'libx264',  # Use libx264 codec for video encoding
            '-y',  # Overwrite output file if it exists
            output  # Output file path
        ]
        
        # Run the FFmpeg command
        subprocess.run(command, check=True)

        return output

    except subprocess.CalledProcessError as e:
        pass
