from video_gen.editor.media import Audio
from video_gen.audio_gen.base import TTS
from video_gen.utils import SafeFile
from typing import List, Tuple
import elevenlabs, base64
import regex as re



class ElevenLabsModel1(TTS):
    """
    Generate a Text-to-Speech (TTS) audio file and save it in the temporary file path.
    """
    slow = False 
    lang = "hi"  
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = True
    
    @staticmethod
    def create(script:str, output_path:str = "output.mp4", **kw) -> Audio:
        """
        Generate speech and save as an audio file.
        """
        voice_id = "Sm1seazb4gs7RSlUVw7c"
        model_id = "eleven_turbo_v2_5"
        output_format= "mp3_22050_32"
        
        client = elevenlabs.ElevenLabs(api_key=kw.get("api_key"))
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
        with SafeFile(output_path):
            with open(output_path,"wb") as f:
                for chunk in response:
                    if chunk: f.write(chunk)
                    
        return Audio(output_path)

    @staticmethod
    def create_with_timestamp(script:str, output_path:str = "output.mp4", **kw) -> Tuple[List[Tuple[float, float, str]], Audio]:
        """
        Generate speech and return timestamps.
        """
        # Generate the audio file
        audio = ElevenLabsModel1.create(script=script, output_path=output_path, **kw)

        # Get the function for generating timestamps
        timestamp_func = ElevenLabsModel1.get_model_timestamps() 
        ts = timestamp_func(script, audio) 
        
        return (ts, audio)


class ElevenLabsModel2(TTS):
    """
    Generate a Text-to-Speech (TTS) audio file and save it in the temporary file path.
    Uses ElevenLabs' built-in timestamp generation.
    """
    slow = False 
    lang = "hi"  
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = True  # Set to True since ElevenLabs provides timestamps
    
    @staticmethod
    def create(script: str, output_path: str = "output.mp4", **kw) -> Audio:
        """
        Generate speech and save as an audio file.
        """
        voice_id = "Sm1seazb4gs7RSlUVw7c"
        model_id = "eleven_turbo_v2_5"
        output_format = "mp3_22050_32"
        
        client = elevenlabs.ElevenLabs(api_key=kw.get("api_key"))
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
        
        with SafeFile(output_path):
            with open(output_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)
                        
        return Audio(output_path)
    
    @staticmethod
    def create_with_timestamp(script: str, output_path: str = "output.mp3", **kw) -> Tuple[List[Tuple[float, float, str]], Audio]:
        """
        Generate speech and return timestamps for words.
        """
        voice_id = "Sm1seazb4gs7RSlUVw7c"
        model_id = "eleven_multilingual_v2"
        output_format = "mp3_44100_128"

        client = elevenlabs.ElevenLabs(api_key="sk_ffb96bd78eea95a7a6acff61a39f1da2c7162eeae5bf12c9")
        response = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id,
            output_format=output_format,
            text=script,
            model_id=model_id,
        )
        
        audio_base64 = response.get("audio_base64")
        if not audio_base64:
            raise ValueError("Missing 'audio_base64' key in API response.")

        #save the file
        audio_data = base64.b64decode(audio_base64)
        with SafeFile(output_path), open(output_path, "wb") as f:
            f.write(audio_data)

        # Extract timestamp data safely
        alignment = response.get("normalized_alignment", {})
        characters = alignment.get("characters", [])
        start_times = alignment.get("character_start_times_seconds", [])
        end_times = alignment.get("character_end_times_seconds", [])

        if not characters or not start_times or not end_times:
            raise ValueError("Missing alignment data in API response. cant genrate timestamps")

        # Convert character-level timestamps to word-level timestamps
        word_timestamps = ElevenLabsModel2._convert_to_word_timestamps(characters, start_times, end_times)
        return word_timestamps, Audio(output_path)

    @staticmethod
    def _convert_to_word_timestamps(characters: List[str], start_times: List[float], end_times: List[float]) -> List[Tuple[float, float, str]]:
        """
        Converts character-level timestamps to word-level timestamps.
        Handles Hindi and English words properly.
        """
        words = []
        current_word = ""
        word_start_time = None
        word_end_time = None

        for i, char in enumerate(characters):
            if re.match(r'[\s\p{Z}\p{P}]', char): # Space or punctuation -> finalize word
                if current_word:
                    words.append((word_start_time, word_end_time, current_word))
                    current_word = ""
                word_start_time = None
            else:
                if not current_word:  # New word starts
                    word_start_time = start_times[i]
                current_word += char
                word_end_time = end_times[i]

        # Add last word if exists
        if current_word:
            words.append((word_start_time, word_end_time, current_word))

        return words
    
    
    

#data exaple


# {
#     "audio_base64": "//uQxAAAEf2S9UeI2IoJNGJ0kw+UBAJAAAJxUNMnh0MkV+xq9XqxWK......".
#     "alignment": {
#         "characters": ["H", "e", "l", "l", "o", " ", "W", "o", "r", "l", "d"], 
#         "character_start_times_seconds": [0.0, 0.244, 0.36, 0.406, 0.476, 0.534, 0.615, 0.662, 0.755, 0.813, 0.894], 
#         "character_end_times_seconds" : [0.244, 0.36, 0.406, 0.476, 0.534, 0.615, 0.662, 0.755, 0.813, 0.894, 1.3]
#     }, 
#     "normalized_alignment": {
#         "characters": [ " ", "H", "e", "l", "l", "o", " ", "W", "o", "r", "l", "d", " "],
#         "character_start_times_seconds": [0.0, 0.174, 0.244, 0.36, 0.406, 0.476, 0.534, 0.615, 0.662, 0.755, 0.813, 0.894, 0.952], 
#         "character_end_times_seconds": [0.174, 0.244, 0.36, 0.406, 0.476, 0.534, 0.615, 0.662, 0.755, 0.813, 0.894, 0.952, 1.3]
#     }
# }
