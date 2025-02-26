from typing import List, Tuple, Dict, Optional

from video_gen.utils import UserDict, Path, clean_files, assets
from video_gen.editor.media import Video, Audio
from video_gen.editor.edit import edit
from PIL import Image, ImageFont, ImageDraw
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import subprocess

def get_text_size(text: str, font:ImageFont) -> tuple[int, int]:
    """
    Calculates the dimensions of the text using the provided font.
    """
    ascent, descent = font.getmetrics()
    
    with Image.new("RGBA",(1,1)) as temp_image:
        draw = ImageDraw.Draw(temp_image)
        bbox = draw.textbbox((0,0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1] + descent + ascent)

def generate_flow_image_data(word_list:list[str], font:ImageFont):
    char_w, char_h = get_text_size(" ", font) #a sing space char size
    text_width_list = [] 
    
    # calculating the total size each word in sentence
    for word in word_list:
        w, _ = get_text_size(word, font)
        text_width_list.append(w)
    
    # calculating the total size of text
    total_size = sum(text_width_list)+((len(text_width_list)-1) * char_w)
    return total_size, text_width_list, char_w, char_h

def size_word_wrap(size_list: list[int], total_width: int, space_size: int) -> list[list[int] | int]:
    """
    Wrap words into lines based on their widths and the maximum allowed width.
    
    Args:
        size_list (list[int]): List of word widths.
        total_width (int): Maximum width available for each line.
        space_size (int): The space width between words.

    Returns:
        list[list[int] | int]: A list where each element is a list of word widths representing one line,
                               and the total size (width) of each line.
    """
    total_size = []
    wrapped_lines = []  
    current_line = []
    current_width = 0   
    
    for size in size_list:
        # If the current word fits on the current line (including the space after the word)
        if current_width + size + (space_size if current_line else 0) <= total_width:
            current_line.append(size)
            current_width += size + (space_size if current_line else 0)
        else:
            # Line is full, so we add it and start a new line
            wrapped_lines.append(current_line)
            total_size.append(current_width)  # Store the width of the full line
            current_line = [size]  # Start a new line with the current word
            current_width = size  # The new line starts with the current word width

    # Add the last line if it has words
    if current_line:
        wrapped_lines.append(current_line)
        total_size.append(current_width)  # Add the width of the last line

    return wrapped_lines, total_size

def divide_word_list(word_list: list[str], wrap_size_list: list[list[int]]) -> list[list[str]]:
    """
    Divides the word list into sublists based on the wrap size information.

    Args:
        word_list (list[str]): List of words to be wrapped.
        wrap_size_list (list[list[int]]): List of wrapped lines with the width of each word in those lines.

    Returns:
        list[list[str]]: A list of sublists, each containing words that fit within a line.
    """
    wrapped_words = []
    current_index = 0
    
    for line_size in wrap_size_list:
        line_words = []
        total_line_width = sum(line_size)  # Sum of word widths for the current line
        
        for word_width in line_size:
            line_words.append(word_list[current_index])
            current_index += 1
        
        wrapped_words.append(line_words)
    
    return wrapped_words

def generate_flow_image(
    text: str, 
    font_size: int,
    font_path: str, 
    width:int,
    height:int,
    padding: int = 100,
    output_folder: str = "",
    bg_image: tuple[int] = (0,0,0,0),
    font_color: tuple[int] = (255,255,255,255),
    stroke_width = 5,
    stroke_fill=(0, 0, 0, 255)
) -> list[str]:
    """Generate an image with wrapped text lines and save each frame as a separate image.

    Args:
        text (str): Text to be displayed.
        font_size (int): Font size for the text.
        font_path (str): Path to the font file.
        padding (int, optional): Padding around the content. Defaults to 20.
        output_folder (str, optional): Folder to save the output images. Defaults to "".
        bg_image (tuple[int], optional): Background color (R, G, B, A). Defaults to transparent (0,0,0,0).
        font_color (tuple[int], optional): Font color (R, G, B, A). Defaults to white (255, 255, 255, 255).

    Returns:
        list[str]: List of file paths for the saved images.
    """
    word_list = text.split(" ")
    
    font = ImageFont.truetype(font_path, font_size)
    size, word_size_list, char_w, char_h = generate_flow_image_data(word_list, font)
    
    # some important info to calculate
    centerx, centery = width // 2, height // 2
    content_w = width - (padding * 2)
    content_h = height - (padding * 2)
    
    #wraping text and size
    wrap_size_list, wrap_total_size = size_word_wrap(word_size_list, content_w, char_w)
    starty = centery - ((char_h * len(wrap_size_list)) // 2)
    word_list = divide_word_list(word_list, wrap_size_list)
    
    image = Image.new("RGBA", (width, height), bg_image)
    current_y = starty
    frame_paths = []  
    index = 0
    
    for paragraph_size_list, paragraph_size, paragraph_list in zip(wrap_size_list, wrap_total_size, word_list):
        # Calculate start position for X-axis (centering horizontally)
        current_word_list = paragraph_list
        draw = ImageDraw.Draw(image)
        current_x = padding + ((content_w - paragraph_size) // 2)
        
        for word, size in zip(current_word_list, paragraph_size_list):
            draw.text(
                (current_x, current_y),
                text = word,
                font = font,
                fill = font_color,
                stroke_width= stroke_width,              # Adjust the border width as needed
                stroke_fill=stroke_fill     # Black border color in RGBA
            )
            current_x += size + char_w

            # save the image
            frame_path = os.path.join(output_folder, f"frame_{index + 1:03d}.png")
            image.save(frame_path)
            frame_paths.append(Video(frame_path))
            index += 1
            
        current_y += char_h

    return frame_paths

def hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
    """Convert a hex color string to an RGBA tuple.

    Args:
        hex_color (str): The hex color string (e.g., "#RRGGBB" or "#RRGGBBAA").

    Returns:
        Tuple[int, int, int, int]: The color in RGBA format.
    """
    hex_color = hex_color.lstrip('#')
    length = len(hex_color)
    
    if length == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, 255)  # Default alpha value is 255 (fully opaque)
    elif length == 8:
        r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
        return (r, g, b, a)
    else:
        raise ValueError("Invalid hex color format")

def gen_trans_sub(
    text: str,
    audio: Audio,
    timestamps: List[Tuple[int, int, str]],
    file_info: UserDict,
    output_file: Path|str
) -> Video:
    """
    Generate a transparent subtitle video.

    Args:
        text (str): Subtitle text.
        audio (Audio): Audio file associated with the subtitles.
        timestamps (List[Tuple[int, int, str]]): List of (start, end, text) tuples.
        file_info (UserDict): Dictionary containing font settings.
        output_file (Optional[Path]): Path to save the output video (defaults to None).

    Returns:
        Video: The generated video with transparent subtitles.
    
    Note:
        for rn just provide .mov file path else there will be error in video gen
    """
    frame_paths = []
    
    try:
        frame_paths = generate_flow_image(
            text = text,
            font_size = file_info.font_size,
            font_path = file_info.font_name,
            width = file_info.width,
            height = file_info.height,
            output_folder = assets.temp_path,
            padding = file_info.padding,
            font_color = hex_to_rgba(file_info.text_color)
        )
        video = edit.concatenate_by_image(
            audio = audio,
            timestamps = timestamps,
            images = frame_paths,
            output_path = output_file
        )
    
    except Exception as e:
        raise 
    
    finally:
        clean_files(frame_paths)
                
    return video


# notes must be written here 


class gen_Text_Frame:
    
    def __init__(self):
        pass
    
    def gen_image(self):
        pass
    
    
    
class gen_Text_Video:
    
    def __init__(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *arg, **kw):
        pass










import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import subprocess

def init_ffmpeg_pipe(output_path, width, height, fps, bg_music, word_data=None):
    """Initialize an ffmpeg process if output_path is given; otherwise, return None."""
    if output_path:
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-loglevel', 'quiet',  # suppress logs
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgba',
            '-s', f'{width}x{height}',
            '-r', str(fps),
            '-i', '-',  # Video input from stdin
        ]
        if bg_music:
            # If we have word_data, compute total duration from its last tuple
            if word_data:
                total_duration = word_data[-1][1]
                ffmpeg_cmd.extend(['-t', str(total_duration)])
            # Add the audio input (without -shortest)
            ffmpeg_cmd.extend(['-i', bg_music, '-c:a', 'copy'])
        ffmpeg_cmd.extend(['-c:v', 'qtrle', output_path])
        return subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return None

def wrap_text(full_text, font, max_width):
    """Wrap full_text so that each line fits within max_width."""
    words = full_text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        if font.getbbox(test_line)[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def create_text_frame(text, font, width, height, background_color, padding,
                      text_color, shadow_color, shadow_offsets, border_thickness, border_color):
    """
    Create a frame (as a NumPy array) with the given text drawn on it.
    The text is wrapped to fit within (width - 2*padding) and centered.
    Shadows and a text border (using stroke) are applied.
    """
    frame_img = np.full((height, width, 4), background_color, dtype=np.uint8)
    pil_img = Image.fromarray(frame_img, 'RGBA')
    draw = ImageDraw.Draw(pil_img)
    
    wrapped_lines = wrap_text(text, font, width - 2 * padding)
    # Compute line height (using "Ay" as a sample)
    line_height = font.getbbox("Ay")[3] + 10
    total_text_height = len(wrapped_lines) * line_height
    start_y = (height - total_text_height) // 2
    
    for i, line in enumerate(wrapped_lines):
        text_width = font.getbbox(line)[2]
        x_start = padding + ((width - 2 * padding - text_width) // 2)
        y_line = start_y + i * line_height
        # Draw shadow offsets
        for dx, dy in shadow_offsets:
            draw.text((x_start + dx, y_line + dy), line, font=font, fill=shadow_color)
        # Draw text with an outline (border) if border_thickness > 0
        draw.text((x_start, y_line), line, font=font, fill=text_color,
                  stroke_width=border_thickness, stroke_fill=border_color)
    return np.array(pil_img)

def output_frame(frame, proc):
    """Output a frame either through the ffmpeg pipe or display it with OpenCV."""
    if proc:
        proc.stdin.write(frame.tobytes())
    else:
        cv2.imshow("Typing Effect", frame)
        cv2.waitKey(1)

def typing_effect(word_data, font, width, height, background_color, padding,
                       text_color, shadow_color, shadow_offsets, border_thickness, border_color, fps,
                       final_hold_fraction=0.3):
    """
    Generator for word-data mode: for each word, yield frames that gradually reveal the word.
    
    For the final word, the reveal is sped up (using only 1 frame for the reveal)
    and then the final frame is held for the remaining frames.
    This reallocation ensures that the overall duration remains the same.
    """
    accumulated_text = ""
    total_words = len(word_data)
    for idx, (start_time, end_time, word) in enumerate(word_data):
        is_last_word = (idx == total_words - 1)
        total_interval = end_time - start_time
        num_frames = max(int(round(total_interval * fps)), 1)
        
        if is_last_word:
            # For the final word, reveal very quickly (animate in 1 frame)
            animate_frames = 1  
            hold_frames = num_frames - animate_frames
        else:
            animate_frames = num_frames
            hold_frames = 0
        
        # Animate the current word letter-by-letter (for animate_frames)
        for frame_idx in range(1, animate_frames + 1):
            fraction = frame_idx / animate_frames
            partial_word = word[:max(1, int(len(word) * fraction))]
            current_text = (accumulated_text + " " + partial_word).strip() if accumulated_text else partial_word
            frame = create_text_frame(current_text, font, width, height, background_color, padding,
                                      text_color, shadow_color, shadow_offsets, border_thickness, border_color)
            yield frame, 1.0 / fps
        
        # Finalize the word
        accumulated_text = (accumulated_text + " " + word).strip() if accumulated_text else word
        frame = create_text_frame(accumulated_text, font, width, height, background_color, padding,
                                  text_color, shadow_color, shadow_offsets, border_thickness, border_color)
        # Hold the final frame for the remaining frames
        for _ in range(hold_frames):
            yield frame, 1.0 / fps

def fallback_word_data_mode(
    word_data: List[Tuple[int,int,str]],
    font: str,
    width: int,
    height: int,
    background_color: str,
    padding: int,
    fps: int,
    border_thickness: int,
    text_color: tuple[int,int,int,int],
    shadow_color: tuple[int,int,int,int], 
    shadow_offsets: tuple[int,int,int,int],
    border_color: tuple[int,int,int,int],
    final_hold_fraction:float  = 0.3
    ):
    """
    Generator for word-data mode: for each word, yield frames that gradually reveal the word.
    
    For the final word, we reveal it over a small fraction (here 20% of its allocated frames)
    and then hold the final frame for the remaining frames. This reallocation ensures that
    the final word stays on screen for a bit longer instead of vanishing immediately.
    """
    accumulated_text = ""
    total_words = len(word_data)
    
    for idx, (start_time, end_time, word) in enumerate(word_data):
        is_last_word = (idx == total_words - 1)
        total_interval = end_time - start_time
        num_frames = max(int(round(total_interval * fps)), 1)
        
        if is_last_word:
            # For the final word, reveal it in a short burst (e.g. 20% of the frames)
            animate_frames = max(1, int(round(num_frames * 0.2)))
            hold_frames = num_frames - animate_frames
        else:
            animate_frames = num_frames
            hold_frames = 0
        
        # Animate the current word letter-by-letter
        for frame_idx in range(1, animate_frames + 1):
            fraction = frame_idx / animate_frames
            partial_word = word[:max(1, int(len(word) * fraction))]
            current_text = (accumulated_text + " " + partial_word).strip() if accumulated_text else partial_word
            frame = create_text_frame(current_text, font, width, height, background_color, padding,
                                      text_color, shadow_color, shadow_offsets, border_thickness, border_color)
            yield frame, 1.0 / fps
        
        # Finalize the word
        accumulated_text = (accumulated_text + " " + word).strip() if accumulated_text else word
        frame = create_text_frame(accumulated_text, font, width, height, background_color, padding,
                                  text_color, shadow_color, shadow_offsets, border_thickness, border_color)
        # Hold the final frame for the remaining frames
        for _ in range(hold_frames):
            yield frame, 1.0 / fps
            
def sub(font_path, font_size, width, height, 
                  text_color=(255, 255, 255, 255), shadow_color=(50, 50, 50, 255),
                  background_color=(0, 0, 0, 0), animate_from_start=False,
                  output_path=None, fps=30, word_data=None, 
                  shadow_offsets=[(3,3), (2,2), (4,4), (5,5)],
                  padding=40, border_thickness=0, border_color=(255,255,255,255),
                  bg_music=None, final_hold_fraction=0.3):
    """
    Displays a typing effect animation.
    
    In word_data mode, a list of tuples (start_time, end_time, word) is used to
    gradually reveal the text word-by-word. For the final word, the animation is sped up
    and then the final frame is held for a brief moment (as determined by final_hold_fraction).
    
    Otherwise, text is revealed character-by-character.
    
    The drawn text is wrapped to fit within (width - 2*padding) and centered.
    Shadows and a text border (via stroke) are applied.
    
    If output_path is provided, frames are piped to ffmpeg to generate a transparent MOV video.
    If bg_music is provided, it is muxed into the output video.
    """
    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Error: Font file not found.")
        return

    proc = init_ffmpeg_pipe(output_path, width, height, fps, bg_music, word_data)
    
    if animate_from_start:
        frame_gen = typing_effect(word_data, font, width, height, background_color, padding,
                                       text_color, shadow_color, shadow_offsets, border_thickness, border_color, fps,
                                       final_hold_fraction=final_hold_fraction)
    else:
        frame_gen = fallback_word_data_mode(word_data, font, width, height, background_color, padding,
                                       text_color, shadow_color, shadow_offsets, border_thickness, border_color, fps,
                                       final_hold_fraction=final_hold_fraction)
    
    for frame, frame_delay in frame_gen:
        try:
            output_frame(frame, proc)
        except BrokenPipeError:
            break
        time.sleep(frame_delay)
    
    if proc:
        proc.stdin.close()
        proc.wait()
    else:
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    return output_path  # Or return a Video object as needed




import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import math, subprocess

###############################
# Helper Functions
###############################

def wrap_text(text, font, max_width):
    """
    Wraps the text into lines so that each line fits within max_width (in pixels).
    If a word is too wide, it is split character-by-character.
    Returns a list of strings.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        bbox_word = font.getbbox(word)
        word_width = bbox_word[2] - bbox_word[0]
        if word_width > max_width:
            partial = ""
            for char in word:
                test = partial + char
                test_width = font.getbbox(test)[2] - font.getbbox(test)[0]
                if test_width <= max_width:
                    partial = test
                else:
                    if current_line:
                        test_line = current_line + " " + partial
                        if font.getbbox(test_line)[2] - font.getbbox(test_line)[0] <= max_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = partial
                    else:
                        lines.append(partial)
                        current_line = ""
                    partial = char
            if partial:
                if current_line:
                    test_line = current_line + " " + partial
                    if font.getbbox(test_line)[2] - font.getbbox(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = partial
                else:
                    current_line = partial
        else:
            test_line = current_line + (" " if current_line else "") + word
            test_width = font.getbbox(test_line)[2] - font.getbbox(test_line)[0]
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def generate_letter_overlay(letter_img, step, reveal_steps, transition_pixels, final_color):
    """
    Creates a dynamic overlay for the letter (or word) image (RGBA) that reveals it gradually.
    Now supports final_color being an RGBA tuple.
    """
    fraction = step / reveal_steps
    letter_np = np.array(letter_img)  # (H, W, 4)
    H, W, _ = letter_np.shape
    reveal_pos = int(W * fraction)

    mask_line = np.zeros(W, dtype=np.float32)
    for x in range(W):
        if x < reveal_pos - transition_pixels/2:
            mask_line[x] = 1.0
        elif x > reveal_pos + transition_pixels/2:
            mask_line[x] = 0.0
        else:
            rel = (x - (reveal_pos - transition_pixels/2)) / transition_pixels
            mask_line[x] = 1.0 - rel
            
    mask_full = np.tile(mask_line, (H, 1))

    # Determine if final_color has an alpha value:
    if len(final_color) == 4:
        final_rgb_arr = np.array(final_color[:3], dtype=np.float32)
        final_alpha_val = final_color[3]
    else:
        final_rgb_arr = np.array(final_color, dtype=np.float32)
        final_alpha_val = 255

    overlay_colors = np.zeros((W, 3), dtype=np.float32)
    for x in range(W):
        phase = (x / W) * 2 * math.pi
        r_cloud = 127 * (1 + math.sin(phase + fraction * 2 * math.pi))
        g_cloud = 127 * (1 + math.sin(phase + fraction * 2 * math.pi + 2 * math.pi/3))
        b_cloud = 127 * (1 + math.sin(phase + fraction * 2 * math.pi + 4 * math.pi/3))
        cloudy = np.array([r_cloud, g_cloud, b_cloud], dtype=np.float32)
        overlay_color = (1 - fraction) * cloudy + fraction * final_rgb_arr
        overlay_colors[x] = np.clip(overlay_color, 0, 255)
    overlay_img = np.tile(overlay_colors[None, :, :], (H, 1, 1)).astype(np.uint8)

    letter_alpha = letter_np[:, :, 3:4] / 255.0
    combined_mask = (mask_full[:, :, None] * letter_alpha).clip(0, 1)
    final_rgb = (overlay_img.astype(np.float32) * combined_mask).astype(np.uint8)
    final_alpha = (combined_mask * final_alpha_val).astype(np.uint8)
    final_rgba = np.dstack([final_rgb, final_alpha])
    return Image.fromarray(final_rgba, mode="RGBA")

def apply_neon_glow(image, glow_layers=6, base_radius=5, intensity_decay=0.9):
    """
    Applies an omnidirectional neon glow to an RGBA image by additively blending
    several blurred copies with increasing radii and decaying opacity.
    (Lower glow layers and base radius help keep text sharp.)
    """
    base = image.convert("RGBA")
    glow_accum = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for i in range(1, glow_layers + 1):
        radius = base_radius * i
        blurred = base.filter(ImageFilter.GaussianBlur(radius=radius))
        np_blurred = np.array(blurred).astype(np.float32)
        np_blurred[..., 3] *= (intensity_decay ** i)
        np_blurred = np.clip(np_blurred, 0, 255).astype(np.uint8)
        layer = Image.fromarray(np_blurred, mode="RGBA")
        glow_accum = ImageChops.add(glow_accum, layer)
    result = Image.alpha_composite(glow_accum, base)
    return result

def get_pulsating_neon(base_image, glow_layers, base_glow_radius, intensity_decay, pulsation_factor):
    """
    Applies neon glow to base_image with a scaled glow radius for pulsation.
    """
    return apply_neon_glow(base_image, glow_layers=glow_layers,
                           base_radius=base_glow_radius * pulsation_factor,
                           intensity_decay=intensity_decay)

###############################
# NeonWordAnimator Class
###############################
# This class takes a list of tuples (start, end, word) and reveals each word over its given duration.
# It now also takes a parameter 'global_padding' that specifies the margin from the video edges,
# so that all text is drawn within that padded region.

class NeonWordAnimator:
    def __init__(self, word_data, font_path, font_size, canvas_width, canvas_height,
                 final_color=(255, 255, 255), bg_color=(0, 0, 0),
                 pos="center", global_padding=20, space_between_words=10,
                 transition_pixels=60, glow_layers=6, base_glow_radius=10, intensity_decay=0.8,
                 extra_hold_time=0.2, fps=30,
                 base_canvas_width=720, base_canvas_height=1280):
        """
        Initializes the animator.
        
        Parameters:
          word_data: List of tuples (start, end, word). Each word is revealed over (end - start) seconds.
          font_path: Path to a TTF font.
          font_size: Base font size (for base_canvas_width).
          canvas_width, canvas_height: Desired output canvas dimensions.
          final_color: Final text color (RGB tuple).
          bg_color: Background color.
          pos: "center" or (x,y) for text block positioning (within the padded region).
          global_padding: Padding (in pixels) from the video edges.
          space_between_words: Space (in pixels) between words (before scaling).
          transition_pixels: Base width (in pixels) for soft transition.
          glow_layers: Number of glow layers.
          base_glow_radius: Base radius for glow.
          intensity_decay: Glow intensity decay factor.
          extra_hold_time: Extra hold time (in seconds) after each word is fully revealed.
          fps: Frames per second.
          base_canvas_width, base_canvas_height: Reference canvas dimensions.
        """
        self.scale_w = canvas_width / base_canvas_width
        self.scale_h = canvas_height / base_canvas_height
        self.scale = (self.scale_w + self.scale_h) / 2.0
        
        self.word_data = word_data
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.fps = fps
        
        self.font_size = int(font_size * self.scale)
        self.global_padding = int(global_padding * self.scale)
        self.space_between_words = int(space_between_words * self.scale)
        self.transition_pixels = int(transition_pixels * self.scale)
        self.base_glow_radius = int(base_glow_radius * self.scale)
        
        self.final_color = final_color
        self.bg_color = bg_color
        self.pos = pos
        self.glow_layers = glow_layers
        self.intensity_decay = intensity_decay
        self.extra_hold_frames = int(extra_hold_time * fps)
        
        self.font = ImageFont.truetype(font_path, self.font_size)
    
    def _render_word(self, word):
        """
        Renders a word onto an RGBA image with extra margin for glow.
        Returns (word_img, plain_width).
        """
        margin = self.base_glow_radius * self.glow_layers
        bbox = self.font.getbbox(word)
        word_width = bbox[2] - bbox[0]
        word_height = bbox[3] - bbox[1]
        new_width = word_width + 2 * margin
        new_height = word_height + 2 * margin
        word_img = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(word_img)
        draw.text((margin - bbox[0], margin - bbox[1]), word, font=self.font, fill=(255, 255, 255, 255))
        return word_img, word_width
    
    def generate_frames(self):
        """
        Yields animation frames with wrapped and aligned text.
        Words are split into lines if adding another word would exceed the available width.
        """
        global_frame = 0
        # Create a composite image with an opaque background.
        composite = Image.new("RGBA", (self.canvas_width, self.canvas_height), self.bg_color)
        available_width = self.canvas_width - 2 * self.global_padding
        available_height = self.canvas_height - 2 * self.global_padding

        # Estimate line height (using a typical character and extra margin for glow)
        char_bbox = self.font.getbbox("A")
        base_line_height = char_bbox[3] - char_bbox[1]
        line_height = base_line_height + self.base_glow_radius * self.glow_layers
        vertical_spacing = 10  # adjust as needed

        # Break word_data into lines that fit within available_width.
        lines = []
        current_line = []
        current_line_width = 0
        for (start_time, end_time, word) in self.word_data:
            bbox = self.font.getbbox(word)
            word_width = bbox[2] - bbox[0]
            if current_line:
                # Check if adding this word (plus space) exceeds available width.
                if current_line_width + self.space_between_words + word_width > available_width:
                    lines.append((current_line, current_line_width))
                    current_line = [(start_time, end_time, word, word_width)]
                    current_line_width = word_width
                else:
                    current_line_width += self.space_between_words + word_width
                    current_line.append((start_time, end_time, word, word_width))
            else:
                current_line.append((start_time, end_time, word, word_width))
                current_line_width = word_width
        if current_line:
            lines.append((current_line, current_line_width))

        # Compute total text block height and starting y to center vertically.
        total_text_height = len(lines) * line_height + (len(lines) - 1) * vertical_spacing
        start_y = self.global_padding + (available_height - total_text_height) // 2

        # Animate each line.
        for line_words, line_width in lines:
            # If centered, calculate starting x so the line is centered.
            if self.pos == "center":
                current_x = self.global_padding + (available_width - line_width) // 2
            elif isinstance(self.pos, tuple):
                current_x = self.pos[0]
            else:
                current_x = self.global_padding

            # Animate each word in the line.
            for (start_time, end_time, word, word_width) in line_words:
                duration = end_time - start_time
                reveal_frames = max(int(round(duration * self.fps)), 1)
                word_img, _ = self._render_word(word)

                # Animate reveal for this word.
                for step in range(reveal_frames):
                    frame = composite.copy().convert("RGB")
                    pulsation = 1 + 0.2 * math.sin(2 * math.pi * global_frame / 60)
                    colored_word = generate_letter_overlay(
                        word_img, step, reveal_frames, self.transition_pixels, self.final_color
                    )
                    neon_word = apply_neon_glow(
                        colored_word,
                        glow_layers=self.glow_layers,
                        base_radius=self.base_glow_radius * pulsation,
                        intensity_decay=self.intensity_decay,
                    )
                    # Paste word with appropriate offsets (including margin for glow)
                    frame.paste(
                        neon_word,
                        (int(current_x - self.base_glow_radius * self.glow_layers),
                         int(start_y - self.base_glow_radius * self.glow_layers)),
                        neon_word,
                    )
                    yield frame
                    global_frame += 1

                # Extra hold frames for this word.
                for _ in range(self.extra_hold_frames):
                    frame = composite.copy().convert("RGB")
                    neon_word = apply_neon_glow(
                        generate_letter_overlay(
                            word_img, reveal_frames, reveal_frames, self.transition_pixels, self.final_color
                        ),
                        glow_layers=self.glow_layers,
                        base_radius=self.base_glow_radius,
                        intensity_decay=self.intensity_decay,
                    )
                    frame.paste(
                        neon_word,
                        (int(current_x - self.base_glow_radius * self.glow_layers),
                         int(start_y - self.base_glow_radius * self.glow_layers)),
                        neon_word,
                    )
                    yield frame
                    global_frame += 1

                # Update composite image with the fully revealed word.
                full_word = generate_letter_overlay(
                    word_img, reveal_frames, reveal_frames, self.transition_pixels, self.final_color
                )
                full_neon = apply_neon_glow(
                    full_word,
                    glow_layers=self.glow_layers,
                    base_radius=self.base_glow_radius,
                    intensity_decay=self.intensity_decay,
                )
                composite.paste(
                    full_neon,
                    (int(current_x - self.base_glow_radius * self.glow_layers),
                     int(start_y - self.base_glow_radius * self.glow_layers)),
                    full_neon,
                )
                current_x += word_width + self.space_between_words

            # Move down to the next line.
            start_y += line_height + vertical_spacing
        
        # Optionally, a final hold phase could be added here.
        
####################################
# FFmpeg Video Writer
####################################
def write_video_ffmpeg(frame_generator, output_path, width, height, fps=30, audio_path=None):
    """
    Pipes frames from frame_generator to ffmpeg to create a video.
    If audio_path is provided, it will be muxed.
    """
    command = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
    ]
    if audio_path:
        command.extend([
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            output_path
        ])
    else:
        command.extend([
            "-an",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            output_path
        ])
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for frame in frame_generator:
        frame_np = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        try:
            process.stdin.write(frame_np.tobytes())
        except BrokenPipeError:
            break
    process.stdin.close()
    process.wait()


def typing_gen_trans_sub_std(
    text: str,
    audio: Audio,
    timestamps: List[Tuple[int, int, str]],
    file_info: UserDict,
    output_file: Path|str
) -> Video:
    width = file_info.width
    height = file_info.height
    padding = file_info.padding
        
    animator = NeonWordAnimator(
        word_data=timestamps,
        font_path=file_info.font_name,
        font_size=file_info.font_size,
        canvas_width=width,
        canvas_height=height,
        final_color= (255, 174, 66, 255),
        bg_color=(0,0,0,0),
        pos="center",
        global_padding=padding,
        space_between_words=10,
        transition_pixels=60,
        glow_layers=8,
        base_glow_radius=20,
        intensity_decay=0.8,
        extra_hold_time=0.2,
        fps=file_info.fps,
        base_canvas_width=width,
        base_canvas_height=height
    )
    output_video = "neon_word_video.mp4"
    frame_gen = animator.generate_frames()
    write_video_ffmpeg(frame_gen, output_file, width, height, file_info.fps, str(audio))
    return Video(output_file)

def typing_gen_trans_sub(
    text: str,
    audio: Audio,
    timestamps: List[Tuple[int, int, str]],
    file_info: UserDict,
    output_file: Path|str
) -> Video:
    width = file_info.width
    height = file_info.height
    padding = file_info.padding
    font_color = hex_to_rgba(file_info.text_color)
    
    return sub(
        font_path = file_info.font_name,
        font_size = file_info.font_size,
        word_data = timestamps,
        width = width,
        height = height,
        text_color = (255, 174, 66, 255),
        shadow_color = (50,50,50,120),
        border_color = (0,0,0,255),
        animate_from_start=True,
        output_path = str(output_file),
        fps = file_info.fps,
        padding = padding,
        border_thickness=2,
        bg_music= str(audio)
    )