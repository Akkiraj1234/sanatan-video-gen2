from video_gen.utils import project_root
import logging
import json


# log path and files and new level
log_path = project_root() / 'app.log'
error_log_path = project_root() / 'error.log'
VIDEO_GEN_ERROR_LEVEL = 60
logging.addLevelName(VIDEO_GEN_ERROR_LEVEL, "VIDEO_GEN_ERROR")


class ExcludeCustomLevelFilter(logging.Filter):
    """
    Filter to exclude custom log level from being shown in console.
    """
    def filter(self, record):
        return record.levelno != VIDEO_GEN_ERROR_LEVEL


def _video_gen_error(self, message: str, *args, **kwargs) -> None:
    if self.isEnabledFor(VIDEO_GEN_ERROR_LEVEL):
        self._log(VIDEO_GEN_ERROR_LEVEL, message, args, **kwargs)


def setup_logging(debug: bool = False, log_to_console: bool = True, error_log:bool = True) -> None:
    """
    Configures application logging, including custom logging for video generation errors.

    Args:
        - debug (bool, optional): Enables debug-level logging if True; otherwise, logs warnings and errors. Defaults to False.
        - log_to_console (bool, optional): Enables logging to the console if True. Defaults to True.
    """
    # Attach custom method to the logger
    logging.Logger.video_gen_error = _video_gen_error    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    logger.propagate = False

    # Remove existing handlers if setup_logging() is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler (always logs everything)
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s [ %(lineno)d ] : %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    # file_handler.addFilter(ExcludeCustomLevelFilter())
    logger.addHandler(file_handler)

    # Console handler (optional)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(ExcludeCustomLevelFilter())
        logger.addHandler(console_handler)
    
    # Handler for Video Generation Error Logging (JSON)
    if error_log:
        error_file_handler = logging.FileHandler(error_log_path, mode="a")
        error_file_handler.setLevel(VIDEO_GEN_ERROR_LEVEL)
        error_formatter = logging.Formatter(
            "// %(asctime)s - %(name)s - %(levelname)s [ %(lineno)d ] : %(message)s"
        )
        error_file_handler.setFormatter(error_formatter)
        logger.addHandler(error_file_handler)

    # Logging setup confirmation
    logger.info(f"Logging setup complete. Logs will be saved to {log_path}")