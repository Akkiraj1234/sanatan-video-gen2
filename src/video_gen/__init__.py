from video_gen.logger import logging_init, set_logging_level
from video_gen.settings import setting_init


def init(
    
) -> None:
    # setting up logging and setting
    logging_init()
    setting = setting_init()
    set_logging_level(setting.DEBUG)
    

__all__ = ['init']