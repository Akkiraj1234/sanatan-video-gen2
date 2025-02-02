import logging

# logging configuration
logger = logging.getLogger(__name__)


def process_input_file(file_path: str) -> None:
    """
    Reads and processes the content of the specified input file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logger.info("Successfully read the file content.")
            print("File content:\n", content)
            
    except FileNotFoundError:
        logger.error("Error: The file '%s' was not found.", file_path)
        
    except Exception as e:
        logger.exception("An unexpected error occurred while reading the file: %s", e)
        