from video_gen.logger import change_to_debug
from video_gen.parser import process_input_file
from video_gen.engine import a_test

from argparse import ArgumentParser, Namespace
import logging , sys


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


def main():
    """
    Main entry point of the application. Parses arguments,
    sets up logging, and starts processing.
    """
    args = parse_arguments()
    # the debug methods
    change_to_debug(args.debug)
    tasks = process_input_file(args.file_path)
    a_test(tasks)


if __name__ == "__main__":
    sys.exit(main())