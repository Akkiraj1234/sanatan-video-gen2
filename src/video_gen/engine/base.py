from video_gen.utils import List, Dict, Tuple, Path

class BaseEngine:
    def create(self, data: List[Dict]) -> Tuple[Path, int, str]:
        """
        This method should be implemented by child classes.
        It should take a list of dictionaries as input and return a tuple containing:
        - Path: The path to the created video file.
        - int: The status code (e.g., 0 for success, 1 for failure).
        - str: A message regarding the success or failure of the video creation.
        """
        raise NotImplementedError("Child classes should implement this method.")

    def clean_buffer(self) -> None:
        """
        This method can be overridden by child classes if needed.
        It should clean up any resources or temporary files used during video creation.
        """
        pass