from __future__ import annotations
from video_gen.utils import Media
from video_gen.editor.ffmpeg import get_MediaInfo
from typing import Dict


class Video(Media):
    """
    A class to represent a video file and its metadata.

    This class extracts video-related metadata from a media file using ffprobe.
    It provides methods to access detailed properties such as resolution, frame rate,
    codec information, duration, and more. An associated audio track can also be linked.

    Attributes:
        file_path (str): The path to the video file.
        audio (Audio or None): An optional Audio object linked to the video.
        format (str): The container format of the video.
        size (int): The file size of the video.
        creation_time (str): The creation time of the video file.
        index (int): The index of the video stream within the file.
        width (int): The width of the video frame.
        height (int): The height of the video frame.
        fps (str): The frame rate of the video.
        bitrate (int): The bitrate of the video stream.
        duration (str): The duration of the video.
        duration_ts (int): The duration in timestamp units.
        codec (str): The codec used for the video stream.
        nb_frames (int): The total number of frames in the video.
        pix_fmt (str): The pixel format of the video.
        time_base (str): The time base of the video stream.

    Methods:
        _load_video_info(): Loads video-specific metadata from the file.
        link_audio(audio_obj): Links an Audio object to the video.
        summary(): Returns a formatted summary of the video details.
        __repr__(): Returns a concise string representation of the video.
        __str__(): Returns the video file path.
        __len__(): Returns the duration of the video in timestamp units.
    """
    
    def __init__(self, file_path: str) -> None:
        """
        Initialize a Video object by loading media information from the given file path.

        Args:
            file_path (str): The path to the video file.
        """
        self.file_path = file_path
        self.audio = None
        self._load_video_info()

    def _load_video_info(self) -> None:
        """
        Load video-specific metadata from the file using get_MediaInfo.

        Raises:
            ValueError: If no video stream is found in the media file.
        """
        media_info = get_MediaInfo(self.file_path)
        self.format = media_info.format
        self.size = media_info.size
        self.creation_time = media_info.creation_time

        if not media_info.VIDEO:
            raise ValueError("No video stream found in file")

        video_stream = next(
            (s for s in media_info.STREAMS if s['type'] == 'video'),
            None
        )
        if video_stream is None:
            raise ValueError("No video stream found in file")
            
        self.index = video_stream['index']
        self.width = video_stream['width']
        self.height = video_stream['height']
        self.fps = video_stream['r_frame_rate']
        self.bitrate = video_stream['bit_rate']
        self.duration = video_stream['duration']
        self.duration_ts = video_stream['duration_ts']
        self.codec = video_stream['codec_name']
        self.nb_frames = video_stream['nb_frames']
        self.pix_fmt = video_stream['pix_fmt']
        self.time_base = video_stream['time_base']

    def link_audio(self, audio_obj: 'Audio') -> None:
        """
        Link an Audio object to this video.

        Args:
            audio_obj (Audio): The Audio object to be linked with the video.
        """
        self.audio = audio_obj
        audio_obj.linked_video = self.file_path

    @property
    def summary(self) -> str:
        """
        Generate a summary of the video details in a key–value pair format.

        Returns:
            str: A formatted string with video details.
        """
        details = {
            "File Path": self.file_path,
            "Format": self.format,
            "Size": self.size,
            "Creation Time": self.creation_time,
            "Index": self.index,
            "Resolution": f"{self.width}x{self.height}",
            "Frame Rate": self.fps,
            "Bitrate": self.bitrate,
            "Duration": self.duration,
            "Duration Timestamp": self.duration_ts,
            "Codec": self.codec,
            "Number of Frames": self.nb_frames,
            "Pixel Format": self.pix_fmt,
            "Time Base": self.time_base,
            "Linked Audio": self.audio.file_path if self.audio else "None"
        }
        # Build the summary string line by line.
        summary_lines = [f"{key}: {value}" for key, value in details.items()]
        return "\n".join(summary_lines)
    
    def isimage(self):
        return True

    def __repr__(self) -> str:
        """
        Return a concise representation of the video information.

        Returns:
            str: A formatted string representing key video properties.
        """
        return (
            f"Video: {self.width}x{self.height} @ {self.fps} fps "
            f"({self.codec}), Format: {self.format}, File Size: {self.size}"
        )

    def __str__(self) -> str:
        """
        Return the file path of the video.

        Returns:
            str: The video file path.
        """
        return str(self.file_path)

    def __len__(self) -> int:
        """
        Return the duration of the video in timestamp units.

        Returns:
            int: The duration timestamp of the video.
        """
        return self.duration_ts


class Audio(Media):
    """
    A class to represent an audio file and its metadata.

    This class extracts audio-related metadata from a media file using ffprobe.
    It provides methods to access details such as codec, sample rate, bitrate, and duration.
    The metadata is useful for audio analysis and processing.

    Attributes:
        file_path (str): The path to the audio file.
        metadata (dict): A dictionary to store additional audio metadata.
        format (str): The container format of the audio.
        size (int): The file size of the audio.
        creation_time (str): The creation time of the audio file.
        index (int): The index of the audio stream within the file.
        codec (str): The codec used for the audio stream.
        sample_rate (int): The sampling rate of the audio.
        bits_per_sample (int or None): The bits per sample in the audio stream.
        fps (str): The frame rate of the audio (if applicable).
        time_base (str): The time base of the audio stream.
        duration (str): The duration of the audio.
        duration_ts (int): The duration in timestamp units.
        bitrate (int): The bitrate of the audio stream.
        nb_frames (int): The total number of frames in the audio.
    
    Methods:
        _load_audio_info(): Loads audio-specific metadata from the file.
        summary(): Returns a formatted summary of the audio details.
        __repr__(): Returns a concise string representation of the audio.
        __str__(): Returns the audio file path.
        __len__(): Returns the duration of the audio in timestamp units.
    """
    def __init__(self, file_path: str) -> None:
        """
        Initialize an Audio object by loading media information from the given file path.

        Args:
            file_path (str): The path to the audio file.
        """
        self.file_path = file_path
        self.metadata: Dict[str, str] = {}
        self._load_audio_info()

    def _load_audio_info(self) -> None:
        """
        Load audio-specific metadata from the file using get_MediaInfo.

        Raises:
            ValueError: If no audio stream is found in the media file.
        """
        media_info = get_MediaInfo(self.file_path)
        self.format = media_info.format
        self.size = media_info.size
        self.creation_time = media_info.creation_time

        if not media_info.AUDIO:
            raise ValueError("No audio stream found in file")

        audio_stream = next(
            (a for a in media_info.STREAMS if a['type'] == 'audio'),
            None
        )
        if audio_stream is None:
            raise ValueError("No audio stream found in file")

        self.index = audio_stream['index']
        self.codec = audio_stream['codec_name']
        self.sample_rate = audio_stream['sample_rate']
        # bits_per_sample might not always be available so we use .get()
        self.bits_per_sample = audio_stream.get('bits_per_sample', None)
        self.fps = audio_stream['r_frame_rate']
        self.time_base = audio_stream['time_base']
        self.duration = audio_stream['duration']
        self.duration_ts = audio_stream['duration_ts']
        self.bitrate = audio_stream['bit_rate']
        self.nb_frames = audio_stream['nb_frames']

    @property
    def summary(self) -> str:
        """
        Generate a summary of the audio details in a key–value pair format.

        Returns:
            str: A formatted string with audio details.
        """
        details = {
            "File Path": self.file_path,
            "Format": self.format,
            "Size": self.size,
            "Creation Time": self.creation_time,
            "Index": self.index,
            "Codec": self.codec,
            "Sample Rate": self.sample_rate,
            "Bits per Sample": self.bits_per_sample,
            "Frame Rate": self.fps,
            "Time Base": self.time_base,
            "Duration": self.duration,
            "Duration Timestamp": self.duration_ts,
            "Bitrate": self.bitrate,
            "Number of Frames": self.nb_frames,
        }
        summary_lines = [f"{key}: {value}" for key, value in details.items()]
        return "\n".join(summary_lines)

    def __repr__(self) -> str:
        """
        Return a concise representation of the audio information.

        Returns:
            str: A formatted string representing key audio properties.
        """
        return (
            f"Audio: {self.file_path}, Codec: {self.codec}, "
            f"{self.sample_rate}Hz, Duration: {self.duration}, "
            f"Format: {self.format}, File Size: {self.size}"
        )

    def __str__(self) -> str:
        """
        Return the file path of the audio.

        Returns:
            str: The audio file path.
        """
        return str(self.file_path)

    def __len__(self) -> int:
        """
        Return the duration of the audio in timestamp units.

        Returns:
            int: The duration timestamp of the audio.
        """
        return self.duration_ts