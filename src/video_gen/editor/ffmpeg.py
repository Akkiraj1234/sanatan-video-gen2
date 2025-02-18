from video_gen.utils import validate_executable, OS_NAME, validate_file, assets
from typing import Dict, Any, List
import subprocess
import json

# Default data to use for rn
ffmpeg_path = assets.ffmpeg
ffprobe_path = assets.ffprobe
terminal = False


class FFmpeg:
    __instance = None
    # __configured = False
    def __init__(self) -> None:
        """Path
        Initialize with paths to FFmpeg binaries.
        """        
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.no_terminal = terminal
        self._validate_binaries()
        # self.__configured = True
    
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
            ffmpeg=self.ffmpeg_path,
            ffprobe=self.ffprobe_path,
            error_handle=False
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
            if path is None: 
                continue
            try:
                validate_executable(name, path)
                setattr(self, f"{name}_path", path)
                
            except (FileNotFoundError, PermissionError) as e:
                if not error_handle: raise e from None
        
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
            base_command = [str(self.ffmpeg_path)] #+ terminal_info
            
        elif command_type == 'ffprobe':
            base_command = [str(self.ffprobe_path)]
            
        else:
            raise ValueError("Invalid command type. Use 'ffmpeg' or 'ffprobe'")
        
        if self.no_terminal:
            if OS_NAME == 'Windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
        before = []                                                  #['cpulimit', '-l', '50', '--', 'ffmpeg']
        terminal_info = ['-hide_banner', '-loglevel', 'error']       #'-progress', 'pipe:1'
        cpu_manage = ['-preset', 'ultrafast', '-threads', '2']
        try:
            result = subprocess.run(
                before + base_command + args + terminal_info + cpu_manage,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                # check=check,
                **kwargs
            )
            return result
        
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip() if e.stderr else "No error message available."
            raise RuntimeError(f"{command_type} \nERROR: {error_message}") from e


# do not support these:-
# Broadcast TV (DVB, ATSC, IPTV)
# Live streaming protocols (MPEG-TS, HLS)
# Satellite and cable transmissions
class MediaInfo:
    """
    A class to extract and store metadata from media files using ffprobe.
    
    Attributes:
        _SUPPORTED_MEDIA_TYPES (tuple): Supported media types (video, audio, image).
        media_data (dict): Raw media data from ffprobe.
        STREAMS (list): List of processed media streams.
        VIDEO (int): Number of video streams detected.
        AUDIO (int): Number of audio streams detected.
        filename (str): Media file name.
        format (str): Media format type.
        duration (float): Duration of the media in seconds.
        size (int): File size in bytes.
        bit_rate (int): Bit rate of the media.
        nb_streams (int): Number of streams in the media.
        creation_time (str): Media creation timestamp (if available).
    """
    _SUPPORTED_MEDIA_TYPES = ('video', 'audio', 'image')
    
    def __repr__(self) -> str:
        """a repr function"""
        return f"MediaInfo(filename={self.filename}, format={self.format}, VIDEO={self.VIDEO}, AUDIO={self.AUDIO})"

    def __len__(self) -> int:
        """return length of stream"""
        return self.duration
    
    def __str__(self) -> str:
        """return file path of stream"""
        return self.filename
    
    def _try_convert_number(self, value: str) -> float|int:
        """
        Attempts to convert a string to an integer or float,
        rounding to two decimal places if necessary.
        """
        try:
            return round(float(value),2) if '.' in value else int(value)
        except (TypeError, ValueError):
            return value
    
    def _parse_frame_rate(self, rate_str: str) -> float:
        """Convert fraction frame rate to float."""
        try:
            parts = rate_str.split('/')
            if len(parts) == 2:
                numerator = float(parts[0])
                denominator = float(parts[1])
                return round(numerator / denominator if denominator != 0 else 0.0,2)
            
            return round(float(rate_str),2)
        except Exception:
            return 0.0
        
    def __init__(self, media_data:Dict[str, Any]) -> None:
        """
        Initializes MediaInfo with raw media data.
        
        Args:
            media_data (Dict[str, Any]): meida json data by ffprobe
        """
        self.media_data = media_data
        self.STREAMS = []
        self.VIDEO = 0
        self.AUDIO = 0
        self._process_format()
        self._process_streams()

    def _process_format(self) -> None:
        """
        Extracts general metadata (format, duration, size, bit rate, etc.)
        from the media file.
        """
        format_ = self.media_data.get('format', {})
        self.filename = format_.get('filename', None)
        self.format = format_.get('format_name', None)
        self.duration = self._try_convert_number(format_.get('duration', "0"))
        self.size = self._try_convert_number(format_.get('size', "0"))
        self.bit_rate = self._try_convert_number(format_.get('bit_rate', "0"))
        self.nb_streams = int(format_.get('nb_streams', 0))
        self.creation_time = format_.get('tags', {}).get('creation_time', None)

    def _process_video_streams(self, data:Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes metadata for video streams.
        """
        return {
            'index': data.get('index'),
            'codec_name': data.get('codec_name', None),
            'codec_tag_string': data.get('codec_tag_string', None),
            'width': data.get('width', 0),
            'height': data.get('height', 0),
            'pix_fmt': data.get('pix_fmt', None),
            'r_frame_rate': self._parse_frame_rate(data.get('r_frame_rate', '0/1')),
            'time_base': self._parse_frame_rate(data.get('time_base', '0/1')),
            'duration_ts': int(self._try_convert_number(data.get('duration_ts', 0))),
            'duration': self._try_convert_number(data.get('duration', "0")),
            'bit_rate': self._try_convert_number(data.get('bit_rate', "0")),
            'nb_frames': self._try_convert_number(data.get('nb_frames', 0)),
            'type': 'video'
        }

    def _process_audio_streams(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes metadata for audio streams.
        """
        return {
            'index': data.get('index'),
            'codec_name': data.get('codec_name', None),
            'codec_tag_string': data.get('codec_tag_string', None),
            'sample_fmt': data.get('sample_fmt', None),
            'sample_rate': self._try_convert_number(data.get('sample_rate', "0")),
            'channels': int(data.get('channels', 0)),
            'bits_per_sample': self._try_convert_number(data.get('bits_per_sample', 0)),
            'r_frame_rate': self._parse_frame_rate(data.get('r_frame_rate', '0/1')),
            'time_base': self._parse_frame_rate(data.get('time_base', '0/1')),
            'duration_ts': int(self._try_convert_number(data.get('duration_ts', 0))),
            'duration': self._try_convert_number(data.get('duration', "0")),
            'bit_rate': self._try_convert_number(data.get('bit_rate', "0")),
            'nb_frames': self._try_convert_number(data.get('nb_frames', 0)),
            'type': 'audio'
        }

    def _process_streams(self) -> None:
        """
        Processes all media streams (video/audio) 
        and updates the STREAMS list.
        """
        for stream in self.media_data.get("streams", []):
            codec_type = stream.get("codec_type")
            if codec_type == "video":
                processed_stream = self._process_video_streams(stream)
                self.VIDEO += 1
            elif codec_type == "audio":
                processed_stream = self._process_audio_streams(stream)
                self.AUDIO += 1
            else:
                continue
            self.STREAMS.append(processed_stream)
            

def get_MediaInfo(file_path: str) -> MediaInfo:
    """
    Extracts and returns detailed media metadata using ffprobe.

    This function checks if the given media file exists and then invokes ffprobe
    to retrieve format, stream, chapter, and program information in JSON format.
    The extracted metadata is parsed and returned as a MediaInfo object.

    Args:
        file_path (str): The path to the media file.

    Returns:
        MediaInfo: An object containing the extracted metadata.

    Raises:
        FileNotFoundError: If the specified media file does not exist.
        ValueError: If the ffprobe output cannot be parsed as JSON.
    """
    if not validate_file(file_path):
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
            file_path
        ]
    )

    try:
        return MediaInfo(json.loads(result.stdout))
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse ffprobe output") from e

ffmpeg = FFmpeg()
