from video_gen.logger import setup_logging
from video_gen.video_gen import generate_video


def init(
    debug: bool = False,
    log_to_console: bool = True,
) -> None:
    setup_logging(debug, log_to_console)


_all__ = ['init', 'generate_video']