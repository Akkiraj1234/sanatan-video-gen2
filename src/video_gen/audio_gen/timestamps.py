from video_gen.editor.media import Audio
from typing import List, Tuple
import logging

# logger info 
logger = logging.getLogger(__name__)

def _logg_timestamps(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"Using TIMESTAMP Model: {func_name} ")
        
        try: 
            result = func(*args, **kwargs)
            logger.info(f"[SUCCESS] Time stamps created; prev {result[:3]}...")
        except Exception as e:
            logger.error(f"[ERROR] Failed to generate Time stamps in {func_name}. Error: {e}")
            raise 
        
        return result
    return wrapper

# main methods
def get_timestamps(name:str) -> callable:
    return basic1


@_logg_timestamps
def basic1(text: str, audio: Audio) -> List[Tuple[int, int, str]]:
    """
    Generates timestamps for each word in the text and associates them with an audio file's duration.
    
    Args:
        text (str): The text to be timestamped.
        audio (Audio): An Audio object with a 'duration' attribute in seconds.
    
    Returns:
        list: A list of tuples containing the start and end timestamps in milliseconds for each word.
        
    """
    if not isinstance(audio, Audio):
        raise ValueError("Argument 'audio' should be an instance of Audio")
    
    words = text.split()
    if not words:
        return []
    
    # Convert total duration from seconds to milliseconds
    total_duration_ms = audio.duration * 1000
    word_duration_ms = total_duration_ms / len(words)
    timestamps = []
    
    for idx, word in enumerate(words):
        start_time = int(idx * word_duration_ms)
        end_time = int((idx + 1) * word_duration_ms)
        timestamps.append((start_time/1000, end_time/1000, word))
    # timestamps[-1] = (timestamps[-1][0],timestamps[-1][1] + 4, timestamps[-1][2])
    return timestamps

