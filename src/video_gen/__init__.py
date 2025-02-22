from video_gen.utils import project_root
from video_gen.settings import setting_init
from video_gen.logger import logging_init
from video_gen.audio_gen import discover_tts_models
from video_gen.video_gen import generate_video
from dotenv import load_dotenv


def init(                                                                                                                                                         
    debug: bool = False,
    log_to_console: bool = True
) -> None:
    """
    insialize new insaince
    """
    root = project_root()                                         # getting root window
    setting = setting_init(root)                                  # setting up the setting class to accses data
    logging_init(debug or setting.debug, log_to_console)          # setting up logging info
    load_dotenv()                                                 # loading all the api keys
    discover_tts_models()                                         # setup audio package 
    # setup image_gen
    # video_gen then
    


_all__ = ['init', 'generate_video']