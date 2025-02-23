from __future__ import annotations
from typing import Literal, Union, Tuple, Dict, List, Any, Iterable
from collections import UserDict
from colorama import Fore, Style
from pathlib import Path
import logging
import json
import uuid
import os

logger = logging.getLogger(__name__)


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

def generate_unique_path(temp_path:str, file_type:str|None = None) -> Path:
    """
    genrate a unique path name
    """
    file_type = f".{file_type}" if file_type is not None else ""
    return Path(os.path.join(temp_path, f"{uuid.uuid4()}{file_type}"))

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
    """
    for path in paths:
        if isinstance(path, (list, tuple, set)):  # Handle iterable of paths
            clean_files(*path)
            continue

        try:
            path = str(path)  # Ensure it's a string path
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Deleted file: {path}")
            else:
                logger.warning(f"File not found: {path}")

        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")

def class_only(method):
    def wrapper(cls, *args, **kwargs):
        if not isinstance(cls, type):
            raise TypeError(f"{method.__name__} can only be accsessed via the class. not an instance.")
        return method(cls, *args, **kwargs)
    return wrapper

def disable_logging(module_name: str):
    logger = logging.getLogger(module_name)
    
    # Remove all handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Prevent logs from propagating
    logger.propagate = False
    logger.setLevel(logging.CRITICAL)
    logger.disabled = True


def api_key(name:str) -> str:
    return os.getenv(name)

class Media:
    pass

class TempFile:
    """
    Manages temporary files automatically, ensuring they are 
    deleted even if an error occurs.

    Usage:
    >>> temp = TempFile()
    >>> path = temp.add_file("example.txt")
    >>> del temp

    Ensure cleanup with:
    >>> if __name__ == "__main__":
    >>>     try: main()
    >>>     except Exception: raise
    >>>     finally: TempFile.cleanup()
    """
    _instances = []

    def __init__(self) -> None:
        """
        Create a TempFile instance and track it.
        """
        self.__class__._instances.append(self)
        self.paths = set()
    
    
    @classmethod
    def cleanup(cls) -> None:
        """
        Delete all assets and clean up instance list.
        """
        num = len(cls._instances)
        for instance in cls._instances[:]:
            instance.delete()
        
        cls._instances.clear()
        logger.info(f"All assets cleaned up. Instances removed: {num}")

    def add_file(self, path: Union[str, Path]) -> None:
        """
        Add a file to track.
        """
        path = str(path)
        if os.path.exists(path):
            self.paths.add(path)
        else:
            raise FileNotFoundError(f"File not found: {path}")

    def create_unique_file(self, extension: str = "tmp", path: Union[str, Path] = None) -> Path:
        """
        Create a unique file and track it.
        """
        if path is None:
            path = os.getcwd()  # Default to current directory

        unique_path = generate_unique_path(temp_path = path, file_type = extension)
        self.paths.add(unique_path)
        
        # Ensure the file actually exists
        with open(unique_path, "w") as f:
            pass

        return unique_path

    def delete(self) -> None:
        """
        Delete all tracked files.
        """
        clean_files(self.paths)
        self.paths = set()

    def __del__(self):
        """
        Ensure instance is removed from tracking and files are deleted.
        """
        if self in self.__class__._instances:
            self.__class__._instances.remove(self)
        
        self.delete()

    def __enter__(self):
        """
        Support `with` statement (context manager).
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Auto-delete assets when exiting `with` block.
        """
        self.delete()


import os
from video_gen.utils import TempFile  # Import TempFile class

class SafeFile:
    """
    Safely manage file operations by ensuring files are cleaned up if an error occurs.
    """
    def __init__(self, path:Union[str, Path, List, Tuple]) -> None:
        """
        Initialize the SafeFile instance and track the file path
        """
        if isinstance(path, (str, Path)):
            path = [str(path)]
        elif isinstance(path, (list, tuple)):
            path = list(path)
        else:
            raise TypeError(f"Invalid path type: {type(path)}")
        
        self.path:List[str] = path
        self.temp = TempFile()
        
    def __enter__(self):
        return self 

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"adding to path TempFile path")
            for path in self.path:
                self.temp.add_file(path)
                
        return False 

        
        
class AttrDict(UserDict):
    """_summary_

    Args:
        UserDict (_type_): _description_
    """
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


OS_NAME = os.name
def validate_executable(name: str, path: str):
    """
    Validate that the given executable exists and is a valid file.

    Args:
        name (str): The name of the executable (e.g., "ffmpeg" or "ffprobe").
        path (str): The expected path to the executable.

    Raises:
        FileNotFoundError: If the executable is not found in the given path and is not in the system's PATH.
        PermissionError: If the given path exists but is not a valid file.
    """
    if not os.path.exists(path):
        if path == "ffmpeg" or path == "ffprobe":
            return 
        raise FileNotFoundError(f"{name} not found at: {path}")

    if not os.path.isfile(path):
        raise PermissionError(f"{name} path is not a file: {path}")
    


def validate_file(file_path:str) -> bool:
    return os.path.exists(file_path)


DIR = project_root()
class assets:
    temp_path = os.path.join(DIR, "assets", "temp")
    font_path = os.path.join(DIR, "assets","font","Mangal Regular.ttf")
    ffmpeg  = "ffmpeg"
    ffprobe = "ffprobe"