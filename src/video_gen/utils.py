from __future__ import annotations
from typing import Literal, Union, Tuple, Dict, List, Any, Iterable
from collections import UserDict
from colorama import Fore, Style
from pathlib import Path
import logging
import json
import uuid
import os


def project_root() -> Path:
    """
    Returns the absolute path of the project root directory.
    """
    return Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def sstrip(string:str) -> str:
    """
    return str with all whitspace removed
    """
    # return "".join(s for s in string if s not in " \t\n\r")
    return string.translate(str.maketrans("", "", " \t\n\r"))

def generate_unique_path(temp_path:str, file_type:str) -> str:
    """
    genrate a unique path name
    """
    return(os.path.join(temp_path, f"{uuid.uuid4()}.{file_type}"))

def validate_file(file_path:str) -> bool:
    """
    check if a path is currect or not
    """
    return os.path.exists(file_path)

def write_json(file_path: str, data: Dict[Any]) -> None:
    """
    write robust json file with error handeling
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def copy_file(old_location:Path|str, new_location:Path|str) -> Path:
    """
    copy a file to another location
    """
    with open(old_location, 'rb') as src_file:
        content = src_file.read()
        with open(new_location, 'wb') as dest_file:
            # Write the content to the new file
            dest_file.write(content)
    
    return new_location if isinstance(new_location, Path) else Path(new_location)

def log_video_gen_error(data: dict, error_message: str, reason: str) -> None:
    """
    Log a video generation error with the associated data and error message in JSON format.
    
    Args:
        - data (dict): The data related to the video generation process.
        - error_message (str): The error message describing what went wrong.
        - reason (str): The reason explaining why the error happened.
    """
    error_message = f"No error message" if not error_message else f"\n// error_message : {error_message}"
    reason = "no reason" if not reason else f"\n// reason : {reason}"
    try:
        data = f"\n{json.dumps(obj = data,ensure_ascii = False, indent = 4)}"
    except json.JSONDecodeError as e:
        data = f'{{"message": "There is some error showing json data"}}{e}'
    
    logger = logging.getLogger()
    message = (
        f"error_message: {error_message}"
        f"reason: {reason}"
        f"{data}"
    )
    logger.video_gen_error(message)

def print_task(tasks, detail: int = 2) -> None:
    """
    Print tasks in a visual format with colored output.
    """
    metadata = tasks[0]
    media_items = tasks[1:]
    
    # Color configuration
    TITLE = Fore.LIGHTCYAN_EX
    META = Fore.GREEN
    MEDIA_HEADER = Fore.MAGENTA
    PAIR = Fore.BLUE
    TEXT = Fore.MAGENTA
    VALUE = Fore.CYAN
    AUDIO = Fore.BLUE
    ICON_VIDEO = Fore.RED
    ICON_IMAGE = Fore.GREEN

    # Metadata section
    print(f"{Style.RESET_ALL}▌ {TITLE}Title: {VALUE}{metadata['title']}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}├─ {META}Size: {VALUE}{metadata['width']}x{metadata['height']}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}├─ {META}Frame Rate: {VALUE}{metadata['frame']}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}├─ {META}File Type: {VALUE}{metadata['file_type']}{Style.RESET_ALL}")
    
    if detail < 1:
        return

    # Media items section
    print(f"{Style.RESET_ALL}├─ {MEDIA_HEADER}Media Items:{Style.RESET_ALL}")
    for i, item in enumerate(media_items, 1):
        media_type = 'video' if 'video' in item else 'image'
        icon = '🎥' if media_type == 'video' else '🖼'
        icon_color = ICON_VIDEO if media_type == 'video' else ICON_IMAGE
        
        print(f"{Style.RESET_ALL}│  ╰─ {icon_color}{icon}{Style.RESET_ALL} {PAIR}Pair {i}: {VALUE}{item[media_type]}{Style.RESET_ALL}")
        texts = ', '.join(item.get('text', []))
        print(f"{Style.RESET_ALL}│     ╰─ {TEXT}Texts: {VALUE}{texts or 'None'}{Style.RESET_ALL}")
        
        if detail >= 2:
            transition = item.get('transition', "no transition")
            effect = ', '.join(item['effect']) if item.get('effect') else 'no effect'
            print(f"{Style.RESET_ALL}│     ╰─ {TEXT}Transition: {VALUE}{transition}{Style.RESET_ALL}")
            print(f"{Style.RESET_ALL}│     ╰─ {TEXT}Effect: {VALUE}{effect}{Style.RESET_ALL}")

    # Audio section
    print(f"{Style.RESET_ALL}├─ {AUDIO}Audio Files: {VALUE}{metadata.get('bg_audio', 'None')}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}╰─{'─' * 40}{Style.RESET_ALL}\n")


def clean_files(*paths: Union[str, Path, Iterable[Union[str, Path]]]):
    """
    Deletes the given file(s) safely without raising errors.

    Args:
        paths (Union[str, Path, Iterable[Union[str, Path]]]): 
            Single or multiple file paths to delete.

    Prints:
        - A warning message if a file could not be deleted.
        - Nothing if deletion is successful.
    """
    for path in paths:
        if isinstance(path, Media):
            path = str(path)
            
        if isinstance(path, (list, tuple, set)):  # Handle iterable of paths
            clean_files(*path)
            continue
        
        try:
            path = Path(path)  # Convert to Path object
            if path.exists():
                path.unlink()
                print(f"Deleted: {path}")
            else:
                print(f"Warning: File not found: {path}")
        except Exception as e:
            print(f"Error deleting {path}: {e}")


class Media:
    pass


class AttrDict(UserDict):
    def __getattr__(self, key):
        if key in self.data:  # Directly check self.data to avoid recursion
            return self.data[key]
        raise AttributeError(f"Attribute {key} not found")
    
    def __setattr__(self, key, value):
        if key == "data":  # Allow setting 'data' in UserDict
            super().__setattr__(key, value)
        else:
            self.data[key] = value  # Store in self.data to prevent recursion

    def __delattr__(self, key):
        if key in self.data:
            del self.data[key]
        else:
            raise AttributeError(f"Attribute {key} not found")

