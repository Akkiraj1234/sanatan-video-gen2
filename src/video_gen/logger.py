from typing import Union, Optional
from colorama import init, Fore, Style
from pathlib import Path
import logging
import sys

# Initialize colorama for Windows support
init()

VIDEO_GEN_ERROR_LEVEL = 60
logging.addLevelName(VIDEO_GEN_ERROR_LEVEL, "VIDEO_GEN_ERROR")


class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter that applies color coding to log messages based on severity.

    Attributes:
        level_colors (dict): Maps log levels to their corresponding color codes.
        message_colors (dict): Maps log levels to message-specific color codes.
        ITALIC (str): ANSI escape sequence for italic text.
        RESET_ITALIC (str): ANSI sequence to reset italic formatting.
        time_color (str): Color code for timestamps.
        name_color (str): Color code for logger names.
        reset (str): ANSI sequence to reset all styles.

    Methods:
        format(record): Formats a log message with color codes.
    """

    level_colors = {
        "DEBUG": Fore.BLUE + Style.BRIGHT,
        "INFO": Fore.GREEN + Style.BRIGHT,
        "WARNING": Fore.YELLOW + Style.BRIGHT,
        "ERROR": Fore.RED + Style.BRIGHT,
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
        "VIDEO_GEN_ERROR": Fore.CYAN + Style.BRIGHT
    }

    message_colors = {
        "DEBUG": Fore.LIGHTBLUE_EX,
        "INFO": Fore.LIGHTGREEN_EX,
        "WARNING": Fore.LIGHTYELLOW_EX,
        "ERROR": Fore.LIGHTRED_EX,
        "CRITICAL": Fore.LIGHTMAGENTA_EX,
        "VIDEO_GEN_ERROR": Fore.LIGHTCYAN_EX
    }

    ITALIC = "\033[3m"
    RESET_ITALIC = "\033[0m"
    time_color = Fore.LIGHTBLACK_EX + ITALIC
    name_color = Fore.LIGHTBLUE_EX
    reset = Style.RESET_ALL

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record with appropriate color codes.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message.
        """
        formatted_message = super().format(record)
        formatted_message = formatted_message.replace(
            record.levelname, f"{self.level_colors.get(record.levelname, Fore.WHITE)}{record.levelname}{self.reset}"
        )
        formatted_message = formatted_message.replace(
            record.msg, f"{self.message_colors.get(record.levelname, Fore.WHITE)}{record.msg}{self.reset}"
        )
        formatted_message = formatted_message.replace(
            str(record.asctime), f"{self.time_color}{record.asctime}{self.RESET_ITALIC}{self.reset}"
        )
        formatted_message = formatted_message.replace(
            record.name, f"{self.name_color}{record.name}{self.reset}"
        )
        return formatted_message
    

class CustomFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        if hasattr(record, 'custom_lineno'):
            record.lineno = record.custom_lineno
        if hasattr(record, 'custom_name'):
            record.name = record.custom_name
        return True
    
class ExcludeCustomLevelFilter(logging.Filter):
    """
    Filter to exclude custom log levels from console output.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno != VIDEO_GEN_ERROR_LEVEL

class CustomLogger(logging.Logger):
    """
    Custom Logger class that includes video_gen_error method.
    """
    def video_gen_error(self, message: str, *args, **kwargs) -> None:
        """
        Logs messages at the custom VIDEO_GEN_ERROR level.
        """
        if self.isEnabledFor(VIDEO_GEN_ERROR_LEVEL):
            self._log(VIDEO_GEN_ERROR_LEVEL, message, args, **kwargs)

logging.setLoggerClass(CustomLogger)


def logging_file_handler(logger: logging.Logger, log_path: Union[str, Path]) -> None:
    """
    Creates and configures a file handler for logging.
    """
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s [ %(lineno)d ] : %(message)s"
    )
    file_handler.addFilter(CustomFilter())
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def logging_error_handler(logger: logging.Logger, log_path: Union[str, Path]) -> None:
    """
    Creates and configures an error file handler.
    """
    error_file_handler = logging.FileHandler(log_path, mode="a")
    error_file_handler.setLevel(VIDEO_GEN_ERROR_LEVEL)
    error_formatter = logging.Formatter(
        "// %(asctime)s - %(name)s - %(levelname)s [ %(lineno)d ] : %(message)s"
    )
    error_file_handler.setFormatter(error_formatter)
    logger.addHandler(error_file_handler)


def logging_console_handler(logger: logging.Logger, debug: bool = True) -> None:
    """
    Creates and configures a console handler for logging.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s [ %(lineno)d ] : %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(ExcludeCustomLevelFilter())
    console_handler.addFilter(CustomFilter())
    logger.addHandler(console_handler)
    

def logging_init(
    logging_file_path: Optional[Union[str, Path]] = None,
    logging_error_file_name: str = "error.log",
    logging_file_name: str = "app.log",
    log_to_file: bool = True,
    log_to_console: bool = True,
    error_log: bool = True,
    console_debug: bool = False,  #currently set to False so at start it will be no log message..
) -> None:
    """
    Initializes logging configuration for the application.

    Args:
        logging_file_path (Optional[Union[str, Path]], optional): Directory to store logs.
            Defaults to the directory where Python was called.
        logging_error_file_name (str, optional): Name of the error log file. Defaults to "error.log".
        logging_file_name (str, optional): Name of the general log file. Defaults to "app.log".
        log_to_file (bool, optional): Whether to enable logging to a file. Defaults to True.
        log_to_console (bool, optional): Whether to enable logging to the console. Defaults to True.
        error_log (bool, optional): Whether to log errors to a separate file. Defaults to True.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
    """
    # If logging path is not provided, use the directory where Python was called
    logging_file_path = (
        Path(logging_file_path).resolve()
        if logging_file_path and Path(logging_file_path).exists()
        else Path.cwd()
    )

    logger = logging.getLogger()
    #fr its Debug will change later to WARNING
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Avoid duplicate handlers when re-initializing logging
    if logger.hasHandlers():
        logger.handlers.clear()

    # settting up the handler
    if log_to_file:
        logging_file_handler(logger, logging_file_path / logging_file_name)

    if error_log:
        logging_error_handler(logger, logging_file_path / logging_error_file_name)

    if log_to_console:
        logging_console_handler(logger, console_debug)

    # first loggin message to confirm insialization
    logger.debug(f"Logging setup complete. Logs will be saved to {logging_file_path / logging_file_name}")


def set_logging_level(debug: bool, all_handeler:bool = False) -> None:
    """
    Updates the logging level dynamically.

    Args:
        debug (bool): If True, sets logging level to DEBUG; otherwise, sets it to WARNING.
        all_handeler (bool): if update all handeler or not
    """
    logger = logging.getLogger()
    new_level = logging.DEBUG if debug else logging.WARNING
    logger.setLevel(new_level)

    if not all_handeler:
        return
    
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):  # Only update console handler
            handler.setLevel(new_level)

    logger.debug(f"Logging level changed to {'DEBUG' if debug else 'WARNING'}")
