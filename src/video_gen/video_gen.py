from video_gen.engine import get_engine
from video_gen.settings import Setting
from video_gen.utils import List, Dict, Tuple, Path, print_task, log_video_gen_error
import logging

# 1. write log level messae here

class generate_video:
    
    def __init__(self):
        self.setting = Setting()
        self.failed_tasks = []
        self.passed_tasks = []
        self.count = 0
        self.total = 0
        self.engion = get_engine(
            name = self.setting.video_engine
        )
        
    def execute(self, data: List[Dict]) -> None:
        """
        """
        try:
            path, code, msge = self.engion.create(data)
            
        except Exception:
            log_video_gen_error()
        
        finally:
            self.engion.clean_buffer()
    
    
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
        print(f"error log saved in {Setting.SETTING_LOG_PATH}")
    
    engion = get_engine()