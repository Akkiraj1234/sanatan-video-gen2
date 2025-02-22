from video_gen.editor.media import Audio
from video_gen.utils import SafeFile
from video_gen.audio_gen.base import TTS
from typing import List, Tuple
import elevenlabs



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
        voice_id = "Ag50Eld5oCoZVliw70iY"
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
    """
    slow = False 
    lang = "hi"  
    _SUPPORTED_TIMESTAMPS_MODEL = ["basic1"]
    _TIMESTAMPS = False
    
    @staticmethod
    def create(script:str, output_path:str = "output.mp4") -> Audio:
        """
        Generate speech and save as an audio file.
        """
        raise NotImplementedError

    @staticmethod
    def create_with_timestamp(script:str, output_path:str = "output.mp4") -> Tuple[List[Tuple[float, float, str]], Audio]:
        """
        Generate speech and return timestamps.
        """
        raise NotImplementedError
