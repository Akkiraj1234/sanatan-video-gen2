from video_gen.engion import Engine
from video_gen.utility import parse_file, demo_json_data
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

def execute(file_path:str) -> None:
    tasks = parse_file(file_path)
    tasks = demo_json_data() # for demo and debug
    engion = Engine()
    
    for task in tasks:
        engion.create(task)
        
    engion.summary()

def main():
    """
    Main entry point of the application. Parses arguments,
    sets up logging, and starts processing.
    """
    args = parse_arguments()
    # updating logging
    # change_to_debug(args.debug)
    # the main application entry
    execute(args.file_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())