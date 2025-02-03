from video_gen.utility import validate_executable, Path, OS_NAME
from video_gen.settings import setting

from typing import Dict, Any, List, Optional
import subprocess
import json

# logger and info
import logging
logger = logging.getLogger(__name__)



class FFmpeg:
    __instance = None
    __configured = False
    
    def __init__(self) -> None:
        """
        Initialize with paths to FFmpeg binaries.
        """
        if self.__configured:
            return
        
        self.ffmpeg_path = Path(setting.ffmpeg)
        self.ffprobe_path = Path(setting.ffprobe)
        self.no_terminal = False
        self._validate_binaries()
        self.__configured = True
    
    def __new__(cls, *args, **kwargs) -> None:
        """
        manage singleton instance 
        """
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def _validate_binaries(self) -> None:
        """
        Validate FFmpeg binaries exist and are executable
        """
        self.update_paths(
            ffmpeg = self.ffmpeg_path,
            ffprobe = self.ffprobe_path,
            error_handle = False
        )

    def update_paths(self, ffmpeg:str = None, ffprobe:str = None, error_handle:bool = True) -> None:
        """
        Update the paths of FFmpeg and FFprobe executables.

        Args:
            ffmpeg (str, optional): New path to ffmpeg executable. Defaults to None (unchanged).
            ffprobe (str, optional): New path to ffprobe executable. Defaults to None (unchanged).
        
        Note: if its raise error then default to original executable path
        """
        paths = {"ffmpeg": ffmpeg, "ffprobe": ffprobe}

        for name, path in paths.items():
            if path is None:  continue
            try:
                validate_executable(name, path)
                setattr(self, f"{name}_path", Path(path)) 
                logger.info(f"Using path : {path} for {name.upper()}")
                
            except (FileNotFoundError, PermissionError) as e:
                if not error_handle: raise e from None
                logger.warning(f"Invalid path ({path}) for {name.upper()}. Retaining original path. error {e}")
        
    def run(self, command_type:str, args:List[str], check:bool = True) -> subprocess.CompletedProcess:
        """
        Generic method to run FFmpeg commands.

        Args:
            command_type (str): "ffmpeg" or "ffprobe".
            args (List[str]): Additional command-line arguments.
            check (bool): If True, raises an error if the command fails.

        Returns:
            subprocess.CompletedProcess: The result of the subprocess execution.
        """
        kwargs = {}
        
        if command_type == 'ffmpeg':
            base_command = [str(self.ffmpeg_path)]
        elif command_type == 'ffprobe':
            base_command = [str(self.ffprobe_path)]
        else:
            raise ValueError("Invalid command type. Use 'ffmpeg' or 'ffprobe'")
        
        if self.no_terminal:
            if OS_NAME == 'Windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        try:
            return subprocess.run(
                base_command + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=check,
                **kwargs
            )
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"{command_type} error: {e.stderr.strip()}") from e



class MediaProbe:
    _SUPPORTED_MEDIA_TYPES = frozenset(('video', 'audio', 'subtitle', 'data'))
    
    @staticmethod
    def process_media_info(raw_data: Dict) -> Dict[str, Any]:
        """Process and normalize raw ffprobe output"""
        return {
            "format": MediaProbe._process_format(raw_data.get("format", {})),
            "streams": [MediaProbe._process_stream(s) for s in raw_data.get("streams", [])],
            "chapters": raw_data.get("chapters", []),
            "programs": raw_data.get("programs", []),
            "summary": MediaProbe._generate_summary(raw_data)
        }

    @staticmethod
    def _process_format(format_info: Dict) -> Dict:
        numeric_fields = [
            'duration', 'size', 'bit_rate', 
            'probe_score', 'nb_streams'
        ]
        return {
            **format_info,
            **{k: MediaProbe._try_convert_number(format_info.get(k)) 
               for k in numeric_fields}
        }

    @staticmethod
    def _process_stream(stream_info: Dict) -> Dict:
        numeric_fields = [
            'duration', 'bit_rate', 'width', 'height',
            'sample_aspect_ratio', 'display_aspect_ratio',
            'sample_rate', 'channels', 'bits_per_sample',
            'frame_count', 'r_frame_rate', 'avg_frame_rate'
        ]
        
        processed = {
            **stream_info,
            **{k: MediaProbe._try_convert_number(stream_info.get(k)) 
               for k in numeric_fields}
        }
        
        for rate in ['r_frame_rate', 'avg_frame_rate']:
            if processed.get(rate):
                processed[f'{rate}_float'] = MediaProbe._parse_frame_rate(processed[rate])
                
        return processed

    @staticmethod
    def _try_convert_number(value: str) -> Any:
        try:
            return float(value) if '.' in value else int(value)
        except (TypeError, ValueError):
            return value

    @staticmethod
    def _parse_frame_rate(frame_rate: str) -> Optional[float]:
        try:
            numerator, denominator = map(float, frame_rate.split('/'))
            return numerator / denominator if denominator != 0 else None
        except Exception:
            return None

    @classmethod
    def _generate_summary(cls, raw_data: Dict) -> Dict[str, Any]:
        format_info = raw_data.get("format", {})
        streams = raw_data.get("streams", [])
        return {
            "media_type": cls._detect_media_type(streams),
            "duration": cls._try_convert_number(format_info.get("duration")),
            "size": cls._try_convert_number(format_info.get("size")),
            "bit_rate": cls._try_convert_number(format_info.get("bit_rate")),
            "stream_count": len(streams)
        }

    @classmethod
    def _detect_media_type(cls, streams: List[Dict]) -> Optional[str]:
        found_types = {s['codec_type'] for s in streams if 'codec_type' in s}
        for media_type in cls._SUPPORTED_MEDIA_TYPES:
            if media_type in found_types:
                return media_type
        return None

    @staticmethod
    def save_to_json(data: Dict, output_path: str) -> None:
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=2)



def get_MediaInfo(file_path: str) -> Dict[str, Any]:
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Media file not found: {file_path}")

    ffmpeg = FFmpeg()
    result = ffmpeg.run(
        'ffprobe', 
        [
            "-v", "error",
            "-show_format",
            "-show_streams",
            "-show_chapters",
            "-show_programs",
            "-print_format", "json",
            str(file_path)
        ]
    )

    try:
        return MediaProbe.process_media_info(json.loads(result.stdout))
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse ffprobe output") from e


# def convert_to_wave(input_audio):
#     """
#     Converts any audio file to WAV format.

#     :param input_audio: Path to the input audio file (e.g., MP3, WebM, OGG, etc.).
#     :param output_wav: Path where the output WAV file should be saved.
#     """
#     # FFmpeg command to convert audio to WAV format
#     wave_path = "".join(input_audio.split('.')[:-1])+".wav"
#     command = [
#         'ffmpeg',
#         '-i', input_audio,  # Input audio file
#         '-acodec', 'pcm_s16le',  # Use PCM codec for WAV format (signed 16-bit little-endian)
#         '-ar', '44100',  # Audio sample rate (44.1kHz is standard for most audio)
#         '-ac', '2',  # Number of audio channels (2 = stereo)
#         '-y',  # Overwrite output file without asking
#         wave_path  # Output WAV file path
#     ]
#     subprocess.run(command)
#     os.remove(input_audio)
#     return wave_path