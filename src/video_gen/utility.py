from googletrans import Translator
from pathlib import Path
import os
import uuid

OS_NAME = os.name

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
    if not path.exists():
        if is_inpath(path.name):
            return 
        raise FileNotFoundError(f"{name} not found at: {path}")

    if not path.is_file():
        raise PermissionError(f"{name} path is not a file: {path}")
    
def translate_text(text, target_language='en'):
    translator = Translator()
    detected_language = translator.detect(text).lang
    translated = translator.translate(text, src=detected_language, dest=target_language)

    return translated.text


def generate_unique_path(temp_path:str, file_type:str) -> str:
    return(os.path.join(temp_path, f"{uuid.uuid4()}.{file_type}"))