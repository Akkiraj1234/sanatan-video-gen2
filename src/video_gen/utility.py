from typing import Union, Iterable
from collections import UserDict
from googletrans import Translator
from pathlib import Path
import os
import uuid

OS_NAME = os.name

class Media:
    pass

DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class assets:
    temp_path = os.path.join(DIR, "assets", "temp")
    font_path = os.path.join(DIR, "assets","font","Mangal Regular.ttf")
    ffmpeg  = os.path.join(DIR, "ffmpeg","ffmpeg")
    ffprobe = os.path.join(DIR, "ffmpeg","ffprobe")

def is_inpath(executable: str) -> bool:
    """
    Check if the given executable is in the directories listed 
    in the PATH environment variable.

    Args:
        executable: Name of the executable file to check.
        return: True if the executable is found else False.
    """
    # Get the PATH environment variable and split it into directories
    path_directories = os.getenv("PATH", "").split(os.pathsep)
    
    return any(
        (Path(directory) / executable).exists()
        for directory in path_directories
    )

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
        if is_inpath(path):
            return 
        raise FileNotFoundError(f"{name} not found at: {path}")

    if not os.path.isfile(path):
        raise PermissionError(f"{name} path is not a file: {path}")
    
def translate_text(text, target_language='en'):
    translator = Translator()
    detected_language = translator.detect(text).lang
    translated = translator.translate(text, src=detected_language, dest=target_language)

    return translated.text


def generate_unique_path(temp_path:str, file_type:str) -> str:
    return(os.path.join(temp_path, f"{uuid.uuid4()}.{file_type}"))

def validate_file(file_path:str) -> bool:
    return os.path.exists(file_path)


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