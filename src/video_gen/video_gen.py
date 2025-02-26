from video_gen.engine import get_engine
from video_gen.settings import setting
from video_gen.utils import List, Dict, Tuple, Path, print_task, log_video_gen_error
import logging

logger = logging.getLogger(__name__)
# 1. write log level messae here


class generate_video:
    
    def __init__(self):
        self.engion = get_engine(name = setting.VIDEO_ENGION)()
        self.failed_tasks = []
        self.passed_tasks = []
        self.count = 0
        self.total = 0
        
    def execute(self, data: List[Dict]) -> None:
        """
        Executes the video generation process.
        """
        logger.debug(f"Executing video generation with data: ")
        try:
            path, code, msge = self.engion.create(data)
            logger.info(f"Video created successfully: {path}")
            self.passed_tasks.append((data, code, msge))
            self.count += 1
            
        except Exception as e:
            logger.error(f"Error during video creation: {e}")
            log_video_gen_error(data, e)
            self.failed_tasks.append((data, str(e)))
            raise e
            
        finally:
            logger.debug("Buffer cleaned after video generation.")
    
    def summary(self) -> None:
        """
        Prints a summary of completed and failed video creations.
        """
        print(f"Total {self.count} video(s) have been created out of {self.total} videos.")
        if not self.failed_tasks:
            return
        
        print(f"{len(self.failed_tasks)} video(s) could not be created.\n\n")
        for task in self.failed_tasks:
            print(f"Error: {task[1]}")
            print_task(task[0], 0)
            
        logger.warning(f"{len(self.failed_tasks)} video(s) failed to create. Check the error.log for details. Path: {setting.SETTING_LOG_PATH}")