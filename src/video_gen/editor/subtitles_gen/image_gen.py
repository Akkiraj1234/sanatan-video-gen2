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


# def create_image_with_word(
#     word: str,
#     image_size: tuple[int, int],
#     position: tuple[int, int],
#     font: ImageFont, 
#     anchor: str = "nw",
#     color: tuple[int, int, int, int] = (255, 255, 255, 255), 
#     bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
#     output_path: str = "output_image.png"
# ) -> None:
#     """
#     Create a new RGBA image with a transparent background and draw a word on it.

#     Args:
#         word (str): The word to draw.
#         image_size (tuple[int, int]): Size of the image (width, height).
#         position (tuple[int, int]): (x, y) position on the image to place the word.
#         font_path (str): Path to the font file (e.g., .ttf).
#         font_size (int): Font size of the text.
#         color (tuple[int, int, int, int]): RGBA color of the text (default is black, fully opaque).
#         output_path (str): Path to save the output image.

#     Returns:
#         None: The function saves the created image to `output_path`.
#     """
#     image = Image.new("RGBA", image_size, bg_color) 
#     draw = ImageDraw.Draw(image)

#     draw.text(position, word, font=font, fill=color,anchor = anchor)
#     image.save(output_path,)
#     print(f"Image with word '{word}' created and saved to {output_path}.")

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

# def run_word_data_mode(word_data, font, width, height, background_color, padding,
#                        text_color, shadow_color, shadow_offsets, border_thickness, border_color, fps,
#                        final_hold_fraction=0.3):
#     """
#     Generator for word-data mode: for each word (with its time interval),
#     yield frames that gradually reveal the word letter-by-letter.
    
#     For the final word, the animation runs faster (using fewer frames) and then holds the final frame
#     for the remaining frames (as determined by final_hold_fraction).
#     """
#     accumulated_text = ""
#     total_words = len(word_data)
#     for idx, (start_time, end_time, word) in enumerate(word_data):
#         is_last_word = (idx == total_words - 1)
#         total_interval = end_time - start_time
#         num_frames = max(int(round(total_interval * fps)), 1)
#         if is_last_word:
#             animate_frames = max(1, int(round(num_frames * (1 - final_hold_fraction))))
#             hold_frames = num_frames - animate_frames
#         else:
#             animate_frames = num_frames
#             hold_frames = 0
        
#         # Animate the current word letter-by-letter
#         for frame_idx in range(1, animate_frames + 1):
#             fraction = frame_idx / animate_frames
#             partial_word = word[:max(1, int(len(word) * fraction))]
#             current_text = (accumulated_text + " " + partial_word).strip() if accumulated_text else partial_word
#             frame = create_text_frame(current_text, font, width, height, background_color, padding,
#                                       text_color, shadow_color, shadow_offsets, border_thickness, border_color)
#             yield frame, 1.0 / fps
#         # Finalize the word
#         accumulated_text = (accumulated_text + " " + word).strip() if accumulated_text else word
#         # If last word, hold final frame for hold_frames; otherwise, yield one final frame
#         frame = create_text_frame(accumulated_text, font, width, height, background_color, padding,
#                                   text_color, shadow_color, shadow_offsets, border_thickness, border_color)
#         if is_last_word:
#             for _ in range(hold_frames):
#                 yield frame, 1.0 / fps
#         else:
#             yield frame, 1.0 / fps
def run_word_data_mode(word_data, font, width, height, background_color, padding,
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

def fallback_word_data_mode(word_data, font, width, height, background_color, padding,
                       text_color, shadow_color, shadow_offsets, border_thickness, border_color, fps,
                       final_hold_fraction=0.3):
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

def typing_effect(font_path, font_size, width, height, 
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
        frame_gen = run_word_data_mode(word_data, font, width, height, background_color, padding,
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
    
    return typing_effect(
        font_path = file_info.font_name,
        font_size = file_info.font_size,
        word_data = timestamps,
        width = width,
        height = height,
        text_color = (255, 174, 66, 255),
        shadow_color = (50,50,50,120),
        border_color = (0,0,0,255),
        animate_from_start=False,
        output_path = str(output_file),
        fps = file_info.fps,
        padding = padding,
        border_thickness=2,
        bg_music= str(audio)
    )


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
    font_color = hex_to_rgba(file_info.text_color)
    
    return typing_effect(
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



# Example usage for word_data mode:
# if __name__ == "__main__":
#     FONT_PATH = "some-ebold.ttf"  # Ensure the font file exists
#     word_data_example = [
#         (0.0, 0.498, 'इसके'),
#         (0.498, 0.996, 'कारण'),
#         (0.996, 1.495, 'उनका'),
#         (1.495, 1.993, 'कंठ'),
#         (1.993, 2.492, 'नीला'),
#         (2.492, 2.99, 'हो'),
#         (2.99, 3.489, 'गया'),
#         (3.489, 3.987, 'और'),
#         (3.987, 4.486, 'उन्हें'),
#         (4.486, 4.984, "'नीलकंठ'"),
#         (4.984, 5.483, 'कहा'),
#         (5.483, 5.981, 'जाने'),
#         (5.981, 6.48, 'लगा।')
#     ]
#     normal_color = (255, 255, 255, 255)
    
#     # To generate a transparent MOV video (~6.48 sec) with background music and a text border:
#     typing_effect(
# text="", 
# font_path=FONT_PATH, 
# font_size=50,
# width=720, 
# height=1080,
# text_color=normal_color, 
# shadow_color=(50,50,50,255), 
# background_color=(0,0,0,0),
# animate_from_start=True, 
# output_path='output.mov', 
# fps=30,
# word_data=word_data_example, 
# padding=40, 
# border_thickness=2,
# border_color=(0,0,0,255),
# bg_music=None)