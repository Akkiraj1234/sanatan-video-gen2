from argparse import ArgumentParser, Namespace
from video_gen import generate_video
from video_gen.utils import TempFile  
from video_gen import init
import logging
import json
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
        help="Path to the json file containing video generation settings or content."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (logs more details)."
    )
    return parser.parse_args()


def execute(file_path:str) -> None:
    """
    Executes a sequence of tasks based on the provided JSON file.

    This function attempts to generate a video and read a JSON file containing tasks.
    It processes each task by invoking the `create` method of a generated video object
    and logs any errors encountered during file reading, task processing, or video generation.
    If the file is not found or the JSON is invalid, the function logs an appropriate error.

    Args:
        file_path (str): The path to the JSON file containing the tasks to be processed.

    Returns:
        None: This function does not return any value. It performs actions like logging errors 
        and processing tasks based on the contents of the given JSON file.
    """
    try:
        engion = generate_video()
        
        with open(file_path, "r", encoding="utf-8") as json_fp:
            try:
                json_data = json.load(json_fp)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from the file: {e}")
                raise
            except Exception as e:
                logging.error(f"An unexpected error occurred while reading the JSON file: {e}")
                raise
        
        for task in json_data:
            try:
                engion.execute(task)
            except Exception as e:
                logging.error(f"Error processing task {task}: {e}")
                raise
            return #-------------------------
            
        engion.summary()
    
    except FileNotFoundError:
        logging.error(f"The file at {file_path} was not found.")
        raise
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise
    
    finally:
        TempFile.cleanup()


def main() -> int:
    """
    The main entry point for executing the program.

    This function parses command-line arguments, initializes the video generation system,
    and invokes the `execute` function to process the tasks in the specified JSON file.
    It returns 0 to indicate successful execution.

    Returns:
        int: Returns 0 to indicate the program has completed successfully.
    """
    args = parse_arguments() 
    
    init(args.debug)         #inisalize video_gen 
    execute(args.file_path)  #execute the code
    return 0

if __name__ == "__main__":
    sys.exit(main())