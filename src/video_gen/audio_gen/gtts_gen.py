from video_gen.audio_gen.base import TTS, log_execution
from video_gen.utils import SafeFile, disable_logging
from video_gen.editor.media import Audio
from video_gen.settings import setting
from typing import List, Tuple
import gtts, logging

# logging work
disable_logging('gtts')
logger = logging.getLogger(__name__)


class GTTSModel(TTS):
    """
    Generate a Text-to-Speech (TTS) audio file and save it in the temporary file path.
    """
    slow = False 
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = True
    
    @staticmethod
    @log_execution
    def create(script:str, output_path:str = "output.mp4", **kw) -> Audio:
        """
        Generate speech and save as an audio file.
        """
        tts = gtts.gTTS(
            text = script,
            lang = setting.TTS_Lang, 
            slow = GTTSModel.slow,
            lang_check = True,
        )
        with SafeFile(output_path):
            tts.save(output_path)
            
        return Audio(output_path)

    @staticmethod
    @log_execution
    def create_with_timestamp(script:str, output_path:str = "output.mp4", **kw) -> Tuple[List[Tuple[float, float, str]], Audio]:
        """
        Generate speech and return timestamps.
        """
        # Generate the audio file
        audio = GTTSModel.create(script=script, output_path=output_path, **kw)
        
        # Get the function for generating timestamps
        timestamp_func = GTTSModel.get_model_timestamps() 
        timestamp = timestamp_func(script, audio) 
        
        return (timestamp, audio)
