from video_gen.settings import setting
from typing import Union, List, Optional, Tuple
from pathlib import Path
from types import ModuleType
import importlib.util


class AssetsNotFoundError(Exception):
    """Raised when an asset file is not found."""
    pass


class AssetsLibraryNotFoundError(Exception):
    """Raised when the assets directory is missing."""
    pass


class AssetsManager:
    """
    Manages importing and listing asset files in a given directory.

    Raises:
        AssetsLibraryNotFoundError: Raised if the specified assets directory is missing.
        ValueError: Raised if an invalid path is provided.
        AssetsNotFoundError: Raised when a specified asset file is not found.
        ImportError: Raised if a module fails to load.
    
    Returns:
        ModuleType: The imported module when using `import_file`.
        List[str]: A list of module filenames when using `module_list`.
    """

    @classmethod
    def check_path(cls, module_dir: Union[Path, str]) -> bool:
        """
        Check if the assets directory exists, and cache the result.
        """
        assets_path = Path(module_dir).resolve()
        if not assets_path.exists():
            raise AssetsLibraryNotFoundError(f"Assets directory '{assets_path}' not found.")

        return True

    @staticmethod
    def get_module_name(module_path: Path) -> str:
        """
        Extracts the module name from a file path.
        """
        return module_path.stem  # Removes `.py` extension

    @classmethod
    def import_file(cls, module_path: Union[Path, str]) -> ModuleType:
        """
        Import a single Python file as a module from the assets directory.
        """
        module_path = Path(module_path).resolve()
        
        if module_path.suffix != ".py":
            raise ValueError(f"Invalid file type '{module_path.suffix}', expected a '.py' file.")

        if not module_path.is_file():
            raise AssetsNotFoundError(f"File '{module_path}' does not exist.")

        module_name = cls.get_module_name(module_path)

        spec = importlib.util.spec_from_file_location(module_name, str(module_path))
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            raise ImportError(f"Failed to import module '{module_name}': {e}")

    @classmethod
    def module_list(cls, module_dir_path: Union[Path, str]) -> List[str]:
        """
        Returns a list of all Python module filenames in the given directory.
        """
        cls.check_path(module_dir_path)
        module_dir = Path(module_dir_path).resolve()

        if not module_dir.is_dir():
            raise ValueError(f"'{module_dir}' is not a directory.")

        return [file.name for file in module_dir.glob("*.py") if file.is_file()]


class Clips:
    Clips_path = setting.ASSETS_PATH / "clips"
    
    def get(self, name):
        return countdown_video

class GLEffects:
    GLEffects_path = setting.ASSETS_PATH / "gl_assets" / "text_effects"

class GLTextEffcts:
    GLTextEffcts_path = setting.ASSETS_PATH / "gl_assets" / "video_effects"

class Font:
    Font_path = setting.ASSETS_PATH / "fonts"
    
    def getpath(self, path:str):
        if path is None:
            path = "/home/akkiraj/Downloads/Noto_Sans_Devanagari/static/NotoSansDevanagari_Condensed-Bold.ttf"
        return path
    

class SoundEffect:
    Sound_effect_path = setting.ASSETS_PATH / "media" / "sound_effects"

class Effects:
    pass


class Assets:
    Font = Font()
    Clips = Clips()
    Effects = Effects()
    GLEffects = GLEffects()
    GLTextEffcts = GLTextEffcts()
    SoundEffect = SoundEffect()
    
from video_gen.editor.media import Video, Audio
from video_gen.editor.ffmpeg import ffmpeg
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2
import os
import shutil
from typing import Optional, Tuple

def hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
    """Convert a hex color string to an RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    length = len(hex_color)

    if length == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, 255)  # Default alpha is 255
    elif length == 8:
        r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
        return (r, g, b, a)
    else:
        raise ValueError("Invalid hex color format")

# def countdown_video(
#     count=5,
#     width=720,
#     height=1280,
#     color: str = "#FFFFFF00",
#     font_path: str = "path/to/font.ttf",
#     output_file: str = "countdown.mov",
#     audio: Optional[str] = None
# ) -> Video:
    
#     color = hex_to_rgba(color)
#     fps = 24  
#     duration = 1  
#     total_frames = fps * duration  
#     fade_duration = fps * 0.5  

#     output_folder = os.path.join(os.path.dirname(output_file), "frames")
#     os.makedirs(output_folder, exist_ok=True)

#     if not os.path.exists(font_path):
#         raise FileNotFoundError(f"Font file not found: {font_path}")

#     frame_index = 0

#     for i in range(count, 0, -1):
#         for frame in range(total_frames):
#             img = np.zeros((height, width, 4), dtype=np.uint8)
#             pil_img = Image.fromarray(img)
#             draw = ImageDraw.Draw(pil_img)

#             scale = 1 + 1.0 * np.sin(frame / total_frames * np.pi)  
#             base_font_size = min(width, height) / 10  
#             font_size = int(scale * base_font_size)
#             font = ImageFont.truetype(font_path, font_size)

#             text = str(i)
#             text_size = draw.textbbox((0, 0), text, font=font)
#             text_width = text_size[2] - text_size[0]
#             text_height = text_size[3] - text_size[1]
#             text_x = (width - text_width) // 2
#             text_y = (height - text_height) // 2

#             alpha = 255  
#             if frame < fade_duration:
#                 alpha = int((frame / fade_duration) * 255)  
#             elif frame > total_frames - fade_duration:
#                 alpha = int(((total_frames - frame) / fade_duration) * 255)  

#             draw.text((text_x, text_y), text, font=font, fill=(color[0], color[1], color[2], alpha))

#             img = np.array(pil_img)

#             frame_filename = os.path.join(output_folder, f"frame_{frame_index:04d}.png")
#             cv2.imwrite(frame_filename, img)
#             frame_index += 1
    
#     cmd = [
#         "-framerate", str(fps),
#         "-i", os.path.join(output_folder, "frame_%04d.png"),
#         "-c:v", "prores_ks",
#         "-profile:v", "4444",
#         "-pix_fmt", "yuva444p10le",
#         "-c:a", "aac",
#         "-b:a", "192k",
#         "-y", output_file
#     ]
    
#     if audio:
#         cmd.insert(4, "-i")
#         cmd.insert(5, audio)
#         cmd.append("-shortest")

#     ffmpeg.run('ffmpeg',cmd)
#     shutil.rmtree(output_folder)
    
#     return Video(output_file)
from typing import Optional
import numpy as np
import os
import cv2
import shutil
from PIL import Image, ImageDraw, ImageFont
from video_gen.editor.media import Video, Audio
from video_gen.editor.ffmpeg import ffmpeg

# def countdown_video(
#     count=5,
#     width=720,
#     height=1280,
#     color: str = "#FFFFFF00",
#     font_path: str = "path/to/font.ttf",
#     output_file: str = "countdown.mov",
#     audio: Optional[str] = None
# ) -> Video:
    
#     color = hex_to_rgba(color)
#     fps = 24  
#     duration = 1  
#     total_frames = fps * duration  
#     fade_duration = fps * 0.5  

#     output_folder = os.path.join(os.path.dirname(output_file), "frames")
#     os.makedirs(output_folder, exist_ok=True)

#     if not os.path.exists(font_path):
#         raise FileNotFoundError(f"Font file not found: {font_path}")

#     frame_index = 0

#     for i in range(count, 0, -1):
#         for frame in range(total_frames):
#             img = np.zeros((height, width, 4), dtype=np.uint8)
#             pil_img = Image.fromarray(img)
#             draw = ImageDraw.Draw(pil_img)

#             scale = 1 + 1.0 * np.sin(frame / total_frames * np.pi)  
#             base_font_size = min(width, height) / 10  
#             font_size = int(scale * base_font_size)
#             font = ImageFont.truetype(font_path, font_size)

#             text = str(i)
#             text_size = draw.textbbox((0, 0), text, font=font)
#             text_width = text_size[2] - text_size[0]
#             text_height = text_size[3] - text_size[1]
#             text_x = (width - text_width) // 2
#             text_y = (height - text_height) // 2

#             alpha = 255  
#             if frame < fade_duration:
#                 alpha = int((frame / fade_duration) * 255)  
#             elif frame > total_frames - fade_duration:
#                 alpha = int(((total_frames - frame) / fade_duration) * 255)  

#             draw.text((text_x, text_y), text, font=font, fill=(color[0], color[1], color[2], alpha))

#             img = np.array(pil_img)

#             frame_filename = os.path.join(output_folder, f"frame_{frame_index:04d}.png")
#             cv2.imwrite(frame_filename, img)
#             frame_index += 1

#     # Generate countdown video
#     cmd = [
#         "-framerate", str(fps),
#         "-i", os.path.join(output_folder, "frame_%04d.png"),
#         "-c:v", "prores_ks",
#         "-profile:v", "4444",
#         "-pix_fmt", "yuva444p10le",
#         "-c:a", "aac",
#         "-b:a", "192k",
#         "-y", output_file
#     ]
    
#     if audio:
#         # Get video and audio duration
#         video_duration = count * duration
#         audio_instance = Audio(audio)
#         audio_duration = audio_instance.duration

#         # If audio is longer, trim it from the back
#         if audio_duration > video_duration:
#             trim_start = audio_duration - video_duration
#             audio_trim_filter = f"atrim=start={trim_start},asetpts=PTS-STARTPTS"
#         else:
#             audio_trim_filter = "anull"

#         cmd = [
#             "-framerate", str(fps),
#             "-i", os.path.join(output_folder, "frame_%04d.png"),
#             "-i", audio,
#             "-filter_complex",
#             f"[1:a] {audio_trim_filter} [audio_trimmed];"
#             f"[audio_trimmed] afade=t=out:st={video_duration-1}:d=1 [final_audio]",
#             "-map", "0:v",
#             "-map", "[final_audio]",
#             "-c:v", "prores_ks",
#             "-profile:v", "4444",
#             "-pix_fmt", "yuva444p10le",
#             "-c:a", "aac",
#             "-b:a", "192k",
#             "-shortest",
#             "-y", output_file
#         ]

#     ffmpeg.run("ffmpeg", cmd)
#     shutil.rmtree(output_folder)

#     return Video(output_file)


def hex_to_rgba(hex_color: str):
    """Convert hex color to RGBA format."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 8:  # Includes alpha
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
    elif len(hex_color) == 6:  # No alpha, assume full opacity
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    raise ValueError("Invalid hex color format")


def countdown_video(
    count=5,
    width=720,
    height=1280,
    color: str = "#FFFFFF",
    font_path: str = "path/to/font.ttf",
    output_file: str = "countdown.mov",
    audio: Optional[str] = None
) -> str:
    """Creates a countdown video with optional audio."""
    
    color = hex_to_rgba(color)
    fps = 24  
    duration = 1  
    total_frames = fps * duration  
    fade_duration = fps * 0.5  

    output_folder = os.path.join(os.path.dirname(output_file), "frames")
    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    frame_index = 0

    for i in range(count, 0, -1):
        for frame in range(total_frames):
            img = np.zeros((height, width, 4), dtype=np.uint8)  # RGBA
            pil_img = Image.fromarray(img)
            draw = ImageDraw.Draw(pil_img)

            # Animated scaling effect for numbers
            scale = 1 + 1.0 * np.sin(frame / total_frames * np.pi)  
            base_font_size = min(width, height) / 5  
            font_size = int(scale * base_font_size)
            font = ImageFont.truetype(font_path, font_size)

            # Center text position
            text = str(i)
            text_size = draw.textbbox((0, 0), text, font=font)
            ascent, descent = font.getmetrics()
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1] + descent
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2

            # FADE IN & FADE OUT CALCULATION
            bg_alpha = 255 - int((frame / total_frames) * 255)  # Background fades from black to transparent

            if frame < fade_duration:  # Fade-in
                alpha = int((frame / fade_duration) * 255)  
            elif frame > total_frames - fade_duration:  # Fade-out
                alpha = int(((total_frames - frame) / fade_duration) * 255)  
            else:
                alpha = 255  # Fully visible

            # Draw text with fading effect
            draw.text((text_x, text_y), text, font=font, fill=(color[0], color[1], color[2], alpha))

            # Apply background transparency
            img = np.array(pil_img)
            img[:, :, 3] = bg_alpha  # Modify alpha channel

            # Save frame
            frame_filename = os.path.join(output_folder, f"frame_{frame_index:04d}.png")
            cv2.imwrite(frame_filename, img)
            frame_index += 1

    # Convert frames into video
    cmd = [
        "-framerate", str(fps),
        "-i", os.path.join(output_folder, "frame_%04d.png"),
        "-c:v", "prores_ks",
        "-profile:v", "4444",
        "-pix_fmt", "yuva444p10le",
        "-y", output_file
    ]

    if audio:
        # Get video and audio duration
        video_duration = count * duration
        audio_instance = Audio(audio)
        audio_duration = audio_instance.duration

        # If audio is longer, trim it from the back
        if audio_duration > video_duration:
            trim_start = audio_duration - video_duration
            audio_trim_filter = f"atrim=start={trim_start},asetpts=PTS-STARTPTS"
        else:
            audio_trim_filter = "anull"

        # Process audio trim
        cmd = [
        "-framerate", str(fps),
        "-i", os.path.join(output_folder, "frame_%04d.png"),
        "-i", audio,
        "-filter_complex",
        f"[1:a] {audio_trim_filter},volume=2.0 [audio_louder];"
        f"[audio_louder] afade=t=out:st={video_duration-1}:d=1 [final_audio]",
        "-map", "0:v",
        "-map", "[final_audio]",
        "-c:v", "prores_ks",
        "-profile:v", "4444",
        "-pix_fmt", "yuva444p10le",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-y", output_file
    ]



    # Run ffmpeg command
    ffmpeg.run('ffmpeg',cmd)

    # Clean up frames and temp audio
    shutil.rmtree(output_folder)
    if os.path.exists("trimmed_audio.aac"):
        os.remove("trimmed_audio.aac")

    return output_file
