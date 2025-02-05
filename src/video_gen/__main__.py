from video_gen.logger import change_to_debug
from video_gen.parser import parse_file, print_tasks
from video_gen.engine import generate_demo_video

from argparse import ArgumentParser, Namespace
import sys


def parse_arguments() -> Namespace:
    """
    Parses command-line arguments for the Video Generation System.
    Returns: argparse.Namespace
    """
    parser = ArgumentParser(
        description="Video Generation System: Process a text file to generate videos.",
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
    # updating logging
    change_to_debug(args.debug)
    
    # the main application entry
    tasks = parse_file(args.file_path)
    print_tasks(tasks)
    generate_demo_video(tasks)
    
    return 0



if __name__ == "__main__":
    sys.exit(main())