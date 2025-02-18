from video_gen.editor.media import Audio
from video_gen.utils import generate_unique_path, assets
from typing import List, Tuple

# importing other modules
try:
    import gtts
except (ModuleNotFoundError, ImportError):
    gtts = None

try: 
    import elevenlabs
except (ModuleNotFoundError, ImportError):
    elevenlabs = None


# main code
def get_timestamps(text: str, audio: Audio) -> List[Tuple[int, int, str]]:
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
        timestamps.append((start_time, end_time, word))

    return timestamps


def TTS_gtts(script:str, output_path: str = "output.mp4") -> str:
    """
    Generate a Text-to-Speech (TTS) audio file and save it in the temporary file path.

    Args:
        script (str): The text to be converted to speech.
        lang (str, optional): The language of the text. Defaults to "en".

    Returns:
        str: The path of the generated wav audio file.
    """
    slow = False # will add setting later
    lang = "hi" # will add setting later
    
    try:
        tts = gtts.gTTS(
            text = script,
            lang = lang,
            slow = slow,
            lang_check = True
        )
        tts.save(output_path)
        return Audio(output_path)
    
    except gtts.gTTSError as e:
        raise e from None 
    

def TTS_elevenlabs(script:str, output_path:str = "output.mp4") -> tuple[str,List[int]]|str:
    voice_id = "Ag50Eld5oCoZVliw70iY" # 1. nsuWityFzyjklsOeHYMt # 2. Ag50Eld5oCoZVliw70iY
    model_id = "eleven_turbo_v2_5"
    output_format= "mp3_22050_32"
    api_key = "sk_9dadd4b84c2879c59a5e6078977235c224ccc8aa5ca1d797"
    
    # api key setup
    client = elevenlabs.ElevenLabs(api_key=api_key)
    response = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format=output_format,
        model_id=model_id,
        text=script,
        voice_settings=elevenlabs.VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True
        )
    )
    
    with open(output_path,"wb") as f:
        for chunk in response:
            if chunk: f.write(chunk)
    
    return Audio(output_path)


def get_tts(name:str) -> tuple[callable,bool]:
    info = {
        "gtts": (TTS_gtts,bool(gtts)),
        "elevenlabs": (TTS_elevenlabs, bool(elevenlabs))
    }
    
    return info.get(name,(TTS_gtts,bool(gtts)))

    
class Tts:
    def __init__(self, tts_use:str = None):
        if tts_use is None:
            tts_use = "gtts" # will use settings
        
        self.tts, works = get_tts(tts_use)
        if not works:
            raise BadStreamFile("unable to import tts "+tts_use)
    
    def create(self, script, lang = "hi") -> Audio:
        translated_text = script
        output_path = generate_unique_path(assets.temp_path,"mp3") # temp path from settings
        return self.tts(
            script = translated_text,
            output_path = output_path,
        )
    




# some error will move to error.py
class BadStreamFile(Exception):
    def __init__(self, *args):
        super().__init__(*args)