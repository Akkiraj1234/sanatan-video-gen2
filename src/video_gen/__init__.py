from video_gen.logger import setup_logging
from video_gen.video_gen import generate_video


def init():
    setup_logging()


_all__ = ['init', 'generate_video']