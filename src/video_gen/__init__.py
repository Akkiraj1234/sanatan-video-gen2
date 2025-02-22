from video_gen.utils import project_root
from video_gen.settings import setting_init
from video_gen.logger import logging_init
from video_gen.video_gen import generate_video
from dotenv import load_dotenv


def init(                                                                                                                                                         
    debug: bool = False,
    log_to_console: bool = True
) -> None:
    """
    insialize new insaince
    """
    root = project_root()
    setting = setting_init(root)
    logging_init(debug or setting.debug, log_to_console)
    load_dotenv()
    # setup audio
    # setup image_gen
    # video_gen then
    


_all__ = ['init', 'generate_video']