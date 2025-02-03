from __future__ import annotations
from typing import List, Optional, Dict, Tuple, Union
from pathlib import Path
import logging
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