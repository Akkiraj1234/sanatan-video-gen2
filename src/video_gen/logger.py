from video_gen.utils import project_root
import logging
import sys
from colorama import init, Fore, Style

# Initialize colorama for Windows support
init()

# Log paths and custom log level
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

def logging_init(debug: bool = False, log_to_console: bool = True, error_log: bool = True) -> None:
    """
    Configures application logging, including custom logging for video generation errors.
    """
    logging.Logger.video_gen_error = _video_gen_error    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    logger.propagate = False

    # Remove existing handlers if logging_init() is called multiple times
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
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
        
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
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
                reset = Style.RESET_ALL
                
                formatted_message = super().format(record)
                formatted_message = formatted_message.replace(record.levelname, f"{level_colors.get(record.levelname, Fore.WHITE)}{record.levelname}{reset}")
                formatted_message = formatted_message.replace(record.msg, f"{message_colors.get(record.levelname, Fore.WHITE)}{record.msg}{reset}")
                formatted_message = formatted_message.replace(str(record.asctime), f"{time_color}{record.asctime}{RESET_ITALIC}{reset}")
                
                return formatted_message
        
        console_formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s [ %(lineno)d ] : %(message)s"
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
