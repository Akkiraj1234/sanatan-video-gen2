from video_gen.parser import parse_file, print_tasks
from video_gen.engion import gen_video
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
    for task in tasks:
        try:
            print_tasks(task)
            gen_video(task)
        except Exception as e:
            print("ERROR: coude'nt genrate video \n",e)
            continue
    
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










# check_file_path = "/home/akkiraj/Desktop/sanatan-video-gen2/test-ffmpeg-engion/video3.mp4"

# media = Video(check_file_path)
# print(media.summary)
# # print(json.dumps(media.STREAMS,indent=4))

# check_file_path = "/home/akkiraj/Desktop/sanatan-video-gen2/test-ffmpeg-engion/kanao1.png"

# media = Video(check_file_path)
# print(media.summary)
# # print(json.dumps(media.STREAMS,indent=4))
