from argparse import ArgumentParser, Namespace
from .logger import setup_logging
import logging
import sys

def parse_arguments() -> Namespace:
    """
    Parses command-line arguments for the Video Generation System.
    Returns: argparse.Namespace
    """
    parser = ArgumentParser(
        description="Video Generation System: Process a text file to generate videos."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the text file containing video generation settings or content."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (logs more details)."
    )
    return parser.parse_args()

def process_input_file(file_path: str) -> None:
    """
    Reads and processes the content of the specified input file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logging.info("Successfully read the file content.")
            print("File content:\n", content)
            
    except FileNotFoundError:
        logging.error("Error: The file '%s' was not found.", file_path)
        
    except Exception as e:
        logging.exception("An unexpected error occurred while reading the file: %s", e)
        

def main():
    """
    Main entry point of the application. Parses arguments,
    sets up logging, and starts processing.
    """
    args = parse_arguments()
    setup_logging(args.debug)
    process_input_file(args.file_path)

if __name__ == "__main__":
    sys.exit(main())