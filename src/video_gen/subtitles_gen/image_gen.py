from typing import List, Tuple, Dict, Optional

from video_gen.utils import UserDict, Path, clean_files, assets
from video_gen.editor.media import Video, Audio
from video_gen.editor.edit import edit
from PIL import Image, ImageFont, ImageDraw
import os


def create_image_with_word(
    word: str,
    image_size: tuple[int, int],
    position: tuple[int, int],
    font: ImageFont, 
    anchor: str = "nw",
    color: tuple[int, int, int, int] = (255, 255, 255, 255), 
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
    output_path: str = "output_image.png"
) -> None:
    """
    Create a new RGBA image with a transparent background and draw a word on it.

    Args:
        word (str): The word to draw.
        image_size (tuple[int, int]): Size of the image (width, height).
        position (tuple[int, int]): (x, y) position on the image to place the word.
        font_path (str): Path to the font file (e.g., .ttf).
        font_size (int): Font size of the text.
        color (tuple[int, int, int, int]): RGBA color of the text (default is black, fully opaque).
        output_path (str): Path to save the output image.

    Returns:
        None: The function saves the created image to `output_path`.
    """
    image = Image.new("RGBA", image_size, bg_color) 
    draw = ImageDraw.Draw(image)

    draw.text(position, word, font=font, fill=color,anchor = anchor)
    image.save(output_path)
    print(f"Image with word '{word}' created and saved to {output_path}.")

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
    padding: int = 20,
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
    image_size = (720, 1080)
    width, height = image_size
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
    
    image = Image.new("RGBA", image_size, bg_image)
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
            output_folder = assets.temp_path
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