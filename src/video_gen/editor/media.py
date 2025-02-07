from __future__ import annotations
from typing import Dict
from video_gen.editor.ffmpeg import get_MediaInfo


class Video:
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
        return self.file_path

    def __len__(self) -> int:
        """
        Return the duration of the video in timestamp units.

        Returns:
            int: The duration timestamp of the video.
        """
        return self.duration_ts


class Audio:
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
        return self.file_path

    def __len__(self) -> int:
        """
        Return the duration of the audio in timestamp units.

        Returns:
            int: The duration timestamp of the audio.
        """
        return self.duration_ts

# class Image:
#     def __init__(self, file_path: str):
#         self.file_path = Path(file_path)
#         self.properties: Dict[str, Any] = {}
#         self.metadata: Dict[str, str] = {}
#         self._load_image_info()

#     def _load_image_info(self):
#         """Load image properties using FFmpeg's media info"""
#         media_info = get_MediaInfo(str(self.file_path))
        
#         # Get first video stream (images are treated as single-frame video)
#         video_stream = next(
#             (s for s in media_info['streams'] if s['codec_type'] == 'video'), 
#             None
#         )
        
#         if not video_stream:
#             raise ValueError("No image stream found in file")

#         self.properties = {
#             'width': video_stream.get('width'),
#             'height': video_stream.get('height'),
#             'format': video_stream.get('codec_name'),
#             'color_space': video_stream.get('pix_fmt'),
#             'bit_depth': self._get_bit_depth(video_stream),
#             'is_animated': self._is_animated(media_info),
#             'frame_count': video_stream.get('nb_frames', 1),
#             'duration': float(video_stream.get('duration', 0) if video_stream.get('duration', 0) else 0),
#             'compression': video_stream.get('compression'),
#         }
        
#         # Extract format-level metadata
#         self.metadata = media_info.get('format', {}).get('tags', {})

#     def _get_bit_depth(self, stream: Dict) -> Optional[int]:
#         """Estimate bit depth from pixel format"""
#         pix_fmt = stream.get('pix_fmt', '')
#         if pix_fmt.endswith('le') or pix_fmt.endswith('be'):
#             return int(pix_fmt[:-2])
#         return None

#     def _is_animated(self, media_info: Dict) -> bool:
#         """Check if image is animated (GIF/APNG)"""
#         return any(
#             stream.get('codec_name') in ['gif', 'apng'] 
#             and int(stream.get('nb_frames', 1)) > 1
#             for stream in media_info['streams']
#         )

#     def get_summary(self) -> str:
#         """Formatted image information"""
#         animated = " (Animated)" if self.properties['is_animated'] else ""
#         return (
#             f"Image: {self.properties['width']}x{self.properties['height']} "
#             f"{self.properties['format']}{animated} - "
#             f"{self.file_path.name}"
#         )

# class Font:
#     def __init__(self, file_path: str):
#         self.file_path = Path(file_path)
#         self.properties: Dict[str, Any] = {}
#         self.metadata: Dict[str, str] = {}
#         self._load_font_info()

#     def _load_font_info(self):
#         """Load font metadata using fontTools library"""
#         try:
#             from fontTools.ttLib import TTFont, TTLibError
#         except ImportError:
#             raise RuntimeError("fontTools library required for font processing")

#         try:
#             font = TTFont(self.file_path)
#             self._parse_font_data(font)
#         except TTLibError as e:
#             raise ValueError(f"Invalid font file: {e}") from e
#         finally:
#             if 'font' in locals():
#                 font.close()

#     def _parse_font_data(self, font: Any) -> None:
#         """Extract metadata from font file"""
#         # Get basic font properties
#         names = font['name'].names
#         family = self._get_name_entry(names, 1)
#         style = self._get_name_entry(names, 2)
#         version = self._get_name_entry(names, 5)

#         # Get metrics
#         metrics = {}
#         if 'hhea' in font:
#             metrics.update({
#                 'ascender': font['hhea'].ascent,
#                 'descender': font['hhea'].descent,
#                 'line_gap': font['hhea'].lineGap,
#             })

#         if 'OS/2' in font:
#             metrics.update({
#                 'weight_class': font['OS/2'].usWeightClass,
#                 'width_class': font['OS/2'].usWidthClass,
#             })

#         self.properties = {
#             'family': family,
#             'style': style,
#             'version': version,
#             'format': self._get_font_format(font),
#             'glyph_count': font['maxp'].numGlyphs if 'maxp' in font else 0,
#             'metrics': metrics,
#             'embedding': self._get_embedding_status(font),
#             'supported_languages': self._get_supported_languages(font),
#         }

#     def _get_name_entry(self, names: List, name_id: int) -> str:
#         """Extract name entry from font's name table"""
#         for entry in names:
#             if entry.nameID == name_id and entry.platformID == 3:
#                 try:
#                     return entry.toUnicode()
#                 except UnicodeDecodeError:
#                     return entry.string.decode('latin-1', errors='ignore')
#         return "Unknown"

#     def _get_font_format(self, font: Any) -> str:
#         """Determine font format (TTF/OTF)"""
#         if font.sfntVersion == 'OTTO':
#             return 'OpenType (OTF)'
#         return 'TrueType (TTF)'

#     def _get_embedding_status(self, font: Any) -> str:
#         """Check font embedding permissions"""
#         if 'OS/2' not in font:
#             return "Unknown"
#         fs_type = font['OS/2'].fsType
#         if fs_type == 0:
#             return "Installable Embedding"
#         return "Restricted License Embedding"

#     def _get_supported_languages(self, font: Any) -> List[str]:
#         """Extract supported languages from 'meta' table"""
#         if 'meta' not in font:
#             return []
#         return list(font['meta'].data.get('langs', []))

#     def get_summary(self) -> str:
#         """Formatted font information"""
#         return (
#             f"Font: {self.properties['family']} - {self.properties['style']} "
#             f"({self.properties['format']})"
#         )