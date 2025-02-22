from video_gen.editor.media import Audio
from video_gen.utils import SafeFile, api_key, disable_logging
from video_gen.settings import setting
from video_gen.audio_gen.base import (
    TTS,
    convert_to_word_timestamps, 
    log_execution
)
from typing import List, Tuple, Dict
import elevenlabs
import base64, logging

# remove elevenlabs logging message
disable_logging("elevenlabs")
disable_logging("httpcore")
disable_logging("httpx")
logger = logging.getLogger(__name__)


VOICE_SETTING = elevenlabs.VoiceSettings(
    stability=0.0,
    similarity_boost=1.0,
    style=0.0,
    use_speaker_boost=True
)


class ElevenLabsModel1(TTS):
    """
    Generate a Text-to-Speech (TTS) audio file using ElevenLabs API.
    """
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = True
    output_format = "mp3_22050_32"
    
    @staticmethod
    @log_execution
    def create(script: str, output_path: str = "output.mp4", **kw) -> Audio:
        """
        Generate speech from text and save it as an audio file.
        
        Args:
            script (str): The input text to be converted into speech.
            output_path (str, optional): The path to save the generated audio file.
            **kw: Additional keyword arguments such as voice_id.
        
        Returns:
            Audio: An Audio object representing the saved audio file.
        """
        
        voice_id = kw.get("voice_id", setting.TTS_ELVENLABS_VOICE_ID)
        client = elevenlabs.ElevenLabs(api_key = api_key("ELEVENLABS_API_KEY"))
        
        response = client.text_to_speech.convert(
            text=script,
            voice_id=voice_id,
            model_id=setting.TTS_ELEVNLABS_MODEL_ID,
            output_format=ElevenLabsModel1.output_format,
            voice_settings=VOICE_SETTING
        )
        with SafeFile(output_path):
            with open(output_path, "wb") as f:
                for chunk in response:
                    if chunk: f.write(chunk)
        
        return Audio(output_path)

    @staticmethod
    @log_execution
    def create_with_timestamp(script: str, output_path: str = "output.mp4", **kw) -> Tuple[List[Tuple[float, float, str]], Audio]:
        """
        Generate speech and extract timestamps for each word.
        
        Args:
            script (str): The input text.
            output_path (str, optional): The path to save the audio file.
            **kw: Additional keyword arguments.
        
        Returns:
            Tuple[List[Tuple[float, float, str]], Audio]: Timestamps and the Audio object.
        """
        audio = ElevenLabsModel1.create(script, output_path=output_path, **kw)
        timestamps = ElevenLabsModel1.generate_timestamps(script, audio)
        return timestamps, audio

    @staticmethod
    def generate_timestamps(script: str, audio: Audio) -> List[Tuple[float, float, str]]:
        """
        Generate timestamps for words in the given audio.
        
        Args:
            script (str): The input text.
            audio (Audio): The corresponding audio file.
        
        Returns:
            List[Tuple[float, float, str]]: Word-level timestamps.
        """
        timestamp_func = ElevenLabsModel1.get_model_timestamps()
        return timestamp_func(script, audio)



class ElevenLabsModel2(TTS):
    """
    A more advanced ElevenLabs TTS model with built-in timestamp generation.
    """
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = True
    output_format = "mp3_22050_32"
    
    @staticmethod
    @log_execution
    def create(script: str, output_path: str = "output.mp4", **kw) -> Audio:
        """
        Generate speech and save it as an audio file.
        """
        voice_id = kw.get("voice_id", setting.TTS_ELVENLABS_VOICE_ID)
        client = elevenlabs.ElevenLabs(api_key = api_key("ELEVENLABS_API_KEY"))
        
        response = client.text_to_speech.convert(
            text=script,
            voice_id=voice_id,
            model_id=setting.TTS_ELEVNLABS_MODEL_ID,
            output_format=ElevenLabsModel2.output_format,
            voice_settings=VOICE_SETTING
        )
        with SafeFile(output_path):
            with open(output_path, "wb") as f:
                for chunk in response:
                    if chunk: f.write(chunk)
        
        return Audio(output_path)
    
    @staticmethod
    @log_execution
    def create_with_timestamp(script: str, output_path: str = "output.mp3", **kw) -> Tuple[List[Tuple[float, float, str]], Audio]:
        """
        Generate speech and extract timestamps.
        """
        voice_id = kw.get("voice_id", setting.TTS_ELVENLABS_VOICE_ID)
        client = elevenlabs.ElevenLabs(api_key = api_key("ELEVENLABS_API_KEY"))
        
        response = client.text_to_speech.convert_with_timestamps(
            text=script,
            voice_id=voice_id,
            output_format=ElevenLabsModel2.output_format,
            model_id=setting.TTS_ELEVNLABS_MODEL_ID,
            voice_settings=VOICE_SETTING
        )
        audio_base64 = response.get("audio_base64")
        if not audio_base64:
            raise ValueError("Missing 'audio_base64' in API response.")
        
        audio_data = base64.b64decode(audio_base64)
        with SafeFile(output_path), open(output_path, "wb") as f:
            f.write(audio_data)
        audio = Audio(output_path)
        
        # genrating timstamps
        try: 
            timestamps = ElevenLabsModel2.extract_timestamp(response)
        except ValueError as e:
            logger.warning(f"failed to generate timestamps: {e}")
            logger.info("Falling back to ElevenLabsModel1 for timestamp generation...")
            timestamps = ElevenLabsModel1.generate_timestamps(script, audio)
        
        return timestamps, audio

    @staticmethod
    def extract_timestamp(response: Dict) -> List[Tuple[float, float, str]]:
        """
        Extract timestamps from API response.
        """
        alignment = response.get("normalized_alignment", {})
        characters = alignment.get("characters", [])
        start_times = alignment.get("character_start_times_seconds", [])
        end_times = alignment.get("character_end_times_seconds", [])
        
        if not characters or not start_times or not end_times:
            raise ValueError("Missing alignment data in API response.")
        
        return convert_to_word_timestamps(characters, start_times, end_times)

