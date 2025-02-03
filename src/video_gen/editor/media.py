from __future__ import annotations
from typing import Dict, List, Optional, Any
from pathlib import Path
from video_gen.editor.ffmpeg import get_MediaInfo


class Video:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.audio = None  # Reference to associated audio
        self._load_video_info()
        
    def _load_video_info(self):
        """Load video-specific data using ffmpeg.py"""
        media_info = get_MediaInfo(str(self.file_path))
        
        # Get first video stream
        video_stream = next(
            (s for s in media_info['streams'] if s['codec_type'] == 'video'), 
            None
        )
        
        if not video_stream:
            raise ValueError("No video stream found in file")
        
        self.properties = {
            'width': video_stream.get('width'),
            'height': video_stream.get('height'),
            'fps': video_stream.get('r_frame_rate_float'),
            'bitrate': video_stream.get('bit_rate'),
            'duration': video_stream.get('duration'),
            'codec': video_stream.get('codec_name')
        }
        
        self.metadata = video_stream.get('tags', {})

    def link_audio(self, audio_obj: Audio):
        """
        Connect related audio object
        """
        self.audio = audio_obj
        audio_obj.linked_video = self.file_path

    def get_video_summary(self) -> str:
        """Simple formatted video info"""
        return (
            f"Video: {self.properties['width']}x{self.properties['height']} "
            f"@{self.properties['fps']:.2f}fps ({self.properties['codec']})"
        )

class Audio:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.linked_video: Optional[Path] = None
        self.properties: Dict[str, Any] = {}
        self.metadata: Dict[str, str] = {}
        self._load_audio_info()

    def _load_audio_info(self):
        """Load audio data from either audio file or video container"""
        media_info = get_MediaInfo(str(self.file_path))
        
        # Check if source is a video file with audio
        if any(s['codec_type'] == 'video' for s in media_info['streams']):
            self.linked_video = self.file_path

        # Get first audio stream
        audio_stream = next(
            (s for s in media_info['streams'] if s['codec_type'] == 'audio'), 
            None
        )
        if not audio_stream:
            raise ValueError("No audio stream found in file")

        # Extract duration from audio stream or format
        duration = audio_stream.get('duration')
        if not duration:
            duration = media_info.get('format', {}).get('duration')
        duration = float(duration) if duration else None

        # Populate audio properties
        self.properties = {
            'channels': audio_stream.get('channels'),
            'sample_rate': audio_stream.get('sample_rate'),
            'bitrate': audio_stream.get('bit_rate'),
            'language': audio_stream.get('tags', {}).get('language', 'und'),
            'codec': audio_stream.get('codec_name'),
            'codec_long_name': audio_stream.get('codec_long_name'),
            'bit_depth': audio_stream.get('bits_per_sample'),
            'duration': duration,
            'container_format': media_info.get('format', {}).get('format_name'),
        }
        self.metadata = audio_stream.get('tags', {})

    def get_audio_summary(self) -> str:
        """Formatted audio info with duration"""
        source = f"from {self.linked_video.name}" if self.linked_video else ""
        
        # Format duration
        duration = self.properties.get('duration')
        if duration:
            minutes = int(duration // 60)
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:04.1f}"
        else:
            duration_str = "N/A"

        return (
            f"Audio: {self.properties['channels']}ch "
            f"{self.properties['sample_rate']}Hz "
            f"({duration_str}) {source}".strip()
        )

    def export_audio(self, output_path: str):
        """Export audio stream (would implement with FFmpeg.py)"""
        if self.linked_video:
            print(f"Extracting audio from {self.linked_video}")

class Image:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.properties: Dict[str, Any] = {}
        self.metadata: Dict[str, str] = {}
        self._load_image_info()

    def _load_image_info(self):
        """Load image properties using FFmpeg's media info"""
        media_info = get_MediaInfo(str(self.file_path))
        
        # Get first video stream (images are treated as single-frame video)
        video_stream = next(
            (s for s in media_info['streams'] if s['codec_type'] == 'video'), 
            None
        )
        
        if not video_stream:
            raise ValueError("No image stream found in file")

        self.properties = {
            'width': video_stream.get('width'),
            'height': video_stream.get('height'),
            'format': video_stream.get('codec_name'),
            'color_space': video_stream.get('pix_fmt'),
            'bit_depth': self._get_bit_depth(video_stream),
            'is_animated': self._is_animated(media_info),
            'frame_count': video_stream.get('nb_frames', 1),
            'duration': float(video_stream.get('duration', 0) if video_stream.get('duration', 0) else 0),
            'compression': video_stream.get('compression'),
        }
        
        # Extract format-level metadata
        self.metadata = media_info.get('format', {}).get('tags', {})

    def _get_bit_depth(self, stream: Dict) -> Optional[int]:
        """Estimate bit depth from pixel format"""
        pix_fmt = stream.get('pix_fmt', '')
        if pix_fmt.endswith('le') or pix_fmt.endswith('be'):
            return int(pix_fmt[:-2])
        return None

    def _is_animated(self, media_info: Dict) -> bool:
        """Check if image is animated (GIF/APNG)"""
        return any(
            stream.get('codec_name') in ['gif', 'apng'] 
            and int(stream.get('nb_frames', 1)) > 1
            for stream in media_info['streams']
        )

    def get_summary(self) -> str:
        """Formatted image information"""
        animated = " (Animated)" if self.properties['is_animated'] else ""
        return (
            f"Image: {self.properties['width']}x{self.properties['height']} "
            f"{self.properties['format']}{animated} - "
            f"{self.file_path.name}"
        )

class Font:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.properties: Dict[str, Any] = {}
        self.metadata: Dict[str, str] = {}
        self._load_font_info()

    def _load_font_info(self):
        """Load font metadata using fontTools library"""
        try:
            from fontTools.ttLib import TTFont, TTLibError
        except ImportError:
            raise RuntimeError("fontTools library required for font processing")

        try:
            font = TTFont(self.file_path)
            self._parse_font_data(font)
        except TTLibError as e:
            raise ValueError(f"Invalid font file: {e}") from e
        finally:
            if 'font' in locals():
                font.close()

    def _parse_font_data(self, font: Any) -> None:
        """Extract metadata from font file"""
        # Get basic font properties
        names = font['name'].names
        family = self._get_name_entry(names, 1)
        style = self._get_name_entry(names, 2)
        version = self._get_name_entry(names, 5)

        # Get metrics
        metrics = {}
        if 'hhea' in font:
            metrics.update({
                'ascender': font['hhea'].ascent,
                'descender': font['hhea'].descent,
                'line_gap': font['hhea'].lineGap,
            })

        if 'OS/2' in font:
            metrics.update({
                'weight_class': font['OS/2'].usWeightClass,
                'width_class': font['OS/2'].usWidthClass,
            })

        self.properties = {
            'family': family,
            'style': style,
            'version': version,
            'format': self._get_font_format(font),
            'glyph_count': font['maxp'].numGlyphs if 'maxp' in font else 0,
            'metrics': metrics,
            'embedding': self._get_embedding_status(font),
            'supported_languages': self._get_supported_languages(font),
        }

    def _get_name_entry(self, names: List, name_id: int) -> str:
        """Extract name entry from font's name table"""
        for entry in names:
            if entry.nameID == name_id and entry.platformID == 3:
                try:
                    return entry.toUnicode()
                except UnicodeDecodeError:
                    return entry.string.decode('latin-1', errors='ignore')
        return "Unknown"

    def _get_font_format(self, font: Any) -> str:
        """Determine font format (TTF/OTF)"""
        if font.sfntVersion == 'OTTO':
            return 'OpenType (OTF)'
        return 'TrueType (TTF)'

    def _get_embedding_status(self, font: Any) -> str:
        """Check font embedding permissions"""
        if 'OS/2' not in font:
            return "Unknown"
        fs_type = font['OS/2'].fsType
        if fs_type == 0:
            return "Installable Embedding"
        return "Restricted License Embedding"

    def _get_supported_languages(self, font: Any) -> List[str]:
        """Extract supported languages from 'meta' table"""
        if 'meta' not in font:
            return []
        return list(font['meta'].data.get('langs', []))

    def get_summary(self) -> str:
        """Formatted font information"""
        return (
            f"Font: {self.properties['family']} - {self.properties['style']} "
            f"({self.properties['format']})"
        )