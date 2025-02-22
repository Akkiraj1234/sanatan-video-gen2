from video_gen.audio_gen.timestamps import get_timestamps
from video_gen.utils import Media
from video_gen.settings import setting
from typing import List, Tuple
import regex as re
import functools
import logging


class TTS:
    """
    Generate a Text-to-Speech (TTS) audio file and save it in the temporary file path.

    Args:
        script (str): The text to be converted to speech.
        lang (str, optional): The language of the text. Defaults to "en".

    Returns:
        str: The path of the generated wav audio file.
    """
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = True
    
    @staticmethod
    def create(script: str, output_path: str = "output.mp4") -> Media:
        raise NotImplementedError
    
    @staticmethod
    def create_with_timestamp(script: str, output_path: str = "output.mp4") -> Tuple[List[Tuple[float, float, str]], Media]:
        raise NotImplementedError
    
    @staticmethod
    def get_timestamps_model_name() -> str:
        if  setting.TTS_ELEVNLABS_MODEL_ID in TTS._SUPPORTED_TIMESTAMPS_MODEL:
            return setting.TTS_ELEVNLABS_MODEL_ID
        
        elif bool(TTS._SUPPORTED_TIMESTAMPS_MODEL):
            return TTS._SUPPORTED_TIMESTAMPS_MODEL[-1]

        raise ValueError(f"Invalid timestamp model: {setting.TIMESTAMPS_MODLE}")

    @staticmethod
    def get_model_timestamps() -> callable:
        model_name = TTS.get_timestamps_model_name()
        return get_timestamps(model_name)


def convert_to_word_timestamps(characters: List[str], start_times: List[float], end_times: List[float]) -> List[Tuple[float, float, str]]:
    """
    Converts character-level timestamps to word-level timestamps.
    Handles Hindi and English words properly.
    """
    timestamps = []
    current_word = ""
    word_start_time = None
    word_end_time = None

    for i, char in enumerate(characters):
        if re.match(r'[\s\p{Z}\p{P}]', char): # Space or punctuation -> finalize word
            if current_word:
                timestamps.append((word_start_time, word_end_time, current_word))
                current_word = ""
            word_start_time = None
        else:
            if not current_word:  # New word starts
                word_start_time = start_times[i]
            current_word += char
            word_end_time = end_times[i]

    # Add last word if exists
    if current_word:
        timestamps.append((word_start_time, word_end_time, current_word))

    return timestamps


def log_execution(func):
    """
    Decorator to log execution details of audio generation functions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        the main wrapper
        """
        class_name, func_name = func.__qualname__.split(".")
        script_preview = (kwargs.get("script", args[0])[:50] + "...") if args else "No script provided"
        logger = logging.getLogger(func.__qualname__)
        
        logger.info(f"Using TTS Model: {class_name} ... | func name {func_name}")
        logger.info(f"Starting audio generation for script: '{script_preview}'")
        
        try:
            result = func(*args, **kwargs)
            path = result[1] if isinstance(result, tuple) else result
            logger.info(f"[SUCCESS] Audio successfully generated and saved at: {result}")
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to generate audio in {class_name}. Error: {e}")
            raise
        
        return result
    return wrapper

