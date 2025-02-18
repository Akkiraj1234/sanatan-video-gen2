from video_gen.utils import log_file_path
import logging

def setup_logging(debug: bool = False, log_to_console: bool = True) -> None:
    """
    Configures application logging.

    Args:
        - debug (bool, optional): Enables debug-level logging if True; otherwise, logs warnings and errors. Defaults to False.
        - log_to_console (bool, optional): Enables logging to the console if True. Defaults to True.

    Note: 
        - Logs are saved to 'app.log' in the project directory.
    """
    log_path = log_file_path()
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
    logger.addHandler(file_handler)

    # Console handler (optional)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Logging setup confirmation
    logger.info(f"Logging setup complete. Logs will be saved to {log_path}")
    