from video_gen.audio_gen.timestamps import get_timestamps
from video_gen.utils import Media
from video_gen.settings import setting
from typing import List, Tuple


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
        pass
    
    @staticmethod
    def create_with_timestamp(script: str, output_path: str = "output.mp4") -> Tuple[List[Tuple[float, float, str]], Media]:
        pass
    
    @staticmethod
    def get_timestamps_model_name() -> str:
        if  setting.timestamp_model in TTS._SUPPORTED_TIMESTAMPS_MODEL:
            return setting.timestamp_model
        
        elif bool(setting._SUPPORTED_TIMESTAMPS_MODEL):
            return setting._SUPPORTED_TIMESTAMPS_MODEL[-1]

        raise ValueError(f"Invalid timestamp model: {setting.timestamp_model}")

    @staticmethod
    def get_model_timestamps() -> callable:
        model_name = TTS.get_timestamps_model_name()
        return get_timestamps(model_name)