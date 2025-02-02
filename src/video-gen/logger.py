from colorama import Fore, Style
import logging 
import os

# path management for app.log, change it according to production
# the DIR path get work for src/videogen type of dir setting that
# this project uses if change change it respectively
# also for production mood set it to ~/viedo-gen
DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGGER_PATH = os.path.join(DIR, "app.log")

# Placeholder	Meaning
# %(asctime)s	Timestamp
# %(levelname)s	Log level (INFO, ERROR, etc.)
# %(name)s	Logger name
# %(message)s	Log message
# %(filename)s	Source filename
# %(funcName)s	Function where log was called
# %(lineno)d	Line number in script

class ColoredFormatter(logging.Formatter):
    """Custom logging formatter with color support for console output."""
    
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,    
        "WARNING": Fore.YELLOW,  
        "ERROR": Fore.RED,     
        "CRITICAL": Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        log_message = super().format(record)
        return f"{log_color}{log_message}{Style.RESET_ALL}"

def setup_logging(debug:bool = False) -> None:
    """
    Configures logging settings for both console and file output.

    Args:
        debug (bool): If True, enables DEBUG level logging for console.
    """
    # Console handler with color
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (no color)
    file_handler = logging.FileHandler(LOGGER_PATH, mode="w")
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] [%(name)s] [%(funcName)s:%(lineno)d] %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # Set log levels
    console_handler.setLevel(logging.WARNING)
    file_handler.setLevel(logging.DEBUG)
    
    if debug: 
        console_handler.setLevel(logging.DEBUG)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler, file_handler]
    )
    
    logging.info(f"Logging setup complete. Logs saved to: {LOGGER_PATH}")
