from typing import List, Dict
from video_gen.audio_gen import Tts, get_timestamps
from video_gen.subtitles_gen import  gen_trans_sub
from video_gen.editor.edit import edit, concatenate_steam
from video_gen.utility import generate_unique_path, os, AttrDict, clean_files, assets
from video_gen.editor.media import Video, Audio
from video_gen.parser import print_task
import time


class Engine:
    """
    Engine class handles the automated video generation pipeline.
    It follows a structured pipeline that involves gathering video settings,
    creating nano clips, processing video, and finalizing the output.
    """
    def __init__(self) -> None:
        """
        Initializes the Engine with tracking for failed tasks and count statistics.
        """
        self.failed_tasks = []  # Stores failed tasks along with error messages
        self.count = 0          # Number of successfully created videos
        self.total = 0          # Total attempted video creations
        self.texttospeach = Tts()
    
    def _gather_info(self, info: Dict) -> dict:
        """
        Gathers essential video settings from the provided dictionary.

        Args:
            info (Dict): Dictionary containing video configuration parameters.

        Returns:
            dict: A dictionary with validated and defaulted video settings.
        """
        return AttrDict({
            'width': info.get('width', 720),
            'height': info.get('height', 1080),
            'fps': info.get('fps', 24),
            'title': info.get('title', 'no_title'),
            'file_type': info.get('file_type', 'mp4'),
            'font_name': info.get('font', assets.font_path),
            'font_size': info.get('font_size', 50)
        })
    
    def _assets_work(self, media:str) -> Video:
        path = generate_unique_path(
            temp_path = assets.temp_path,
            file_type=str(media).rsplit('.',1)[-1]
        )
        with open(str(media), 'rb') as src_file:
            content = src_file.read()
            with open(path, 'wb') as dest_file:
                # Write the content to the new file
                dest_file.write(content)

        return Video(path)

    def _nano_clip_creation(self, text:str, file_info) -> Video:
        """
        the dict should contain media info and text
        if not raise value error
        """
        # generating the music
        audio = self.texttospeach.create(text)
        timestamps = get_timestamps(text, audio)
        
        mov = gen_trans_sub(
            text = text,
            audio = audio,
            timestamps = timestamps,
            file_info = file_info,
            output_file = generate_unique_path(
                temp_path = assets.temp_path,
                file_type = 'mov'
            ),
        )
        clean_files((audio))
        return mov
    
    def _clip_creation(self, task:Dict, file_info) -> List[Video]:
        """
        Handles the creation of nano clips with various video and compositing effects.

        Args:
            task (Dict): Dictionary containing clip creation details.

        Returns:
            List[Dict]: List of created clip metadata.
        """
        try:
            media = Video(task['video'])
            texts = task['text']
        except KeyError as e:
            raise ValueError('the format is not correct cloudnet find media and text')
        
        # creating nano clips
        nano_clips:List[Video] = []
        for text in texts:
            nano_clip = self._nano_clip_creation(text, file_info)
            nano_clips.append(nano_clip)
        
        
        # adding all the effects in media as showed in pipeline
        semi_media = self._assets_work(media)
        
        # creating the transparent clip
        semi_clip = edit.concatenate_by_video(
            videos = nano_clips,
            output_path = generate_unique_path(
                temp_path = assets.temp_path,
                file_type="mov"
            )
        )
        # creating final video by merging them
        clip = edit.overlay_video_image(
            base_video = semi_media,
            overlay_video = semi_clip,
            output_path = generate_unique_path(
                temp_path = assets.temp_path,
                file_type = "mp4"
            )
        )
        clean_files(nano_clips)
        clean_files(semi_clip)
        clean_files(semi_media)
        return clip
    
    def _clips_creation(self, task:List[Dict], file_info) -> List[Video]:
        clips:List[Video] = []
        
        for clip_info in task:
            clips.append(
                self._clip_creation(clip_info, file_info)
            )
        
        return clips
    
    def _pre_final_processing(self, clips: List['Video'], fine_info) -> 'Video':
        """
        Applies final transformations on the concatenated video before output.

        Args:
            clips (List[Video]): List of processed clips ready for final modifications.

        Returns:
            Video: The processed video after applying final adjustments.
        """
        return concatenate_steam(
            *clips,
            output_path = os.path.join(assets.temp_path,f'{fine_info.title}.{fine_info.file_type}'),
            transition_duration=1,
            transition_effect="smoothleft"
        )
    
    def _final_video(self, video: Video, video_info) -> None:
        """
        Handles finalization steps such as watermarking, background music, 
        and exporting the video in different formats.

        Args:
            video (Video): The final video ready for export.
        """
        return video
    
    def pipeline(self, task:List[Dict]) -> str:
        """
        Main pipeline that orchestrates video creation through defined stages.

        Steps:
        1. Gather video settings using `_gather_info`.
        2. Create mini clips using `_clips_creation`.
        3. Process final modifications using `_pre_final_processing`.
        4. Finalize and export using `_final_video`.

        Args:
            task (List[Dict]): List of tasks defining video generation workflow.

        Returns:
            str: Path or identifier of the generated final video.
        """
        video_info  = self._gather_info(task[0])
        clips:List  = self._clips_creation(task[1:], video_info)
        final_video = self._pre_final_processing(clips, video_info)
        final_video = self._final_video(final_video, video_info)
        clean_files(clips)
        
        return str(final_video)
    
    def create(self, task: List[Dict]) -> None:
        """
        Handles the execution of the video creation pipeline for a given task.
        Tracks success or failure and updates the statistics.

        Args:
            task (List[Dict]): List of tasks defining video generation workflow.
        """
        try:
            print_task(task, 1)  # Log the task details
            start_time = time.time()
            path = self.pipeline(task)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Video creation completed in {execution_time:.2f}s.")
            print(f"Video successfully created and saved at: {path}\n\n")
            self.count += 1
            
        except Exception as e:
            self.failed_tasks.append([task, str(e)])
            print(f"Error occurred while creating video: {e}")
            print("Please check the task details and try again.\n")
            
        finally:
            self.total += 1
    
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