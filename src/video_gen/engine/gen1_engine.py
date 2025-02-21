from typing import List, Dict
from video_gen.audio_gen import Tts, get_timestamps
from video_gen.editor.media import Video, Audio
from video_gen.editor.effects import effect_get
from video_gen.editor.edit import edit, add_video_info
from video_gen.subtitles_gen import  gen_trans_sub
from video_gen.utils import generate_unique_path, os, AttrDict, clean_files, assets, print_task, copy_file
from video_gen.editor.clips import countdown_video
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
        self.semi_clip = []
    
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
            'font_size': info.get('font_size', 50),
            'bg_audio': info.get('bg_audio', None),
            'watermark': info.get('watermark', None),
            'end_video': info.get('end_video', None)
        })

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
    
    def _assets_work(self, task:str, file_info, duration:int) -> Video:
        """_summary_

        Args:
            task (str): _description_
            file_info (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            Video: _description_
        """
        try:
            media = Video(task['video'])
            video_effect = task.get('effect', [])
        except KeyError as e:
            raise ValueError('the format is not correct cloudnet find media and effect')
        
        video = media
        for effect in video_effect:
            effect = effect_get.get(effect)
            video = effect(
                input_path = video,
                output_path = generate_unique_path(
                    temp_path = assets.temp_path,
                    file_type = "mp4"
                ),
                total_duration = duration
            )

        if video_effect == []:
            video = effect_get.get('no_effect')(
                input_path = media,
                output_path = generate_unique_path(
                    temp_path = assets.temp_path,
                    file_type = "mp4"
                ),
                duration = duration
            )
            
        return video
    
    def analyze_text(self, task:List[str]) -> None:
        extra = ''
        list_text = []
        for text in task:
            if text.startswith(":") and text.endswith(":"):
                extra = text[1:-1]
                continue
            
            list_text.append(text)
            
        return extra, list_text
    
    def _subtile_creation(self, task, file_info):
        """_summary_

        Args:
            texts (_type_): _description_
            file_info (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            texts = task['text']
        except KeyError as e:
            raise ValueError('the format is not correct cloudnet find text')
        
        extra, texts = self.analyze_text(texts)
        
        # creating nano clips
        nano_clips:List[Video] = []
        for text in texts:
            nano_clip = self._nano_clip_creation(text, file_info)
            nano_clips.append(nano_clip)
        print(texts)
            
        if extra == "countdown":
            nano_clips.append(
                countdown_video(
                    count=3,
                    width=720,
                    height=1080,
                    output_file = generate_unique_path(
                    temp_path = assets.temp_path,
                    file_type="mov"
                    ),
                    audio = os.path.join("/home/akkiraj/Desktop/sanatan-video-gen2/assets/sound_effect", "sfxCountdown.mp3")
                )
            )
        
        # creating the transparent clip
        semi_clip = edit.concatenate_by_video(
            videos = nano_clips,
            output_path = generate_unique_path(
                temp_path = assets.temp_path,
                file_type="mov"
            )
        )
        clean_files(nano_clips)
        return semi_clip
    
    def _clip_creation(self, task:Dict, file_info) -> List[Video]:
        """
        Handles the creation of nano clips with various video and compositing effects.

        Args:
            task (Dict): Dictionary containing clip creation details.

        Returns:
            List[Dict]: List of created clip metadata.
        """
        # adding all the effects in media as showed in pipeline
        semi_clip = self._subtile_creation(task, file_info)
        self.semi_clip.append(semi_clip)
        semi_media = self._assets_work(task, file_info, semi_clip.duration)
        
        # creating final video by merging them
        # clip = edit.overlay_video_image(
        #     base_video = semi_media,
        #     overlay_video = semi_clip,
        #     output_path = generate_unique_path(
        #         temp_path = assets.temp_path,
        #         file_type = "mp4"
        #     )
        # )
        # clean_files(semi_clip)
        # clean_files(semi_media)
        return semi_media
    
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
        print("creating concatenate_steam")
        main = edit.concatenate_steam(
            *clips,
            output_path = generate_unique_path(
                temp_path = assets.temp_path,
                file_type = "mp4"
            ),
            transition_duration=1,
            transition_effect="fade"
        )
        print("creating concatenate_by_video")
        clips = edit.concatenate_by_video(
            self.semi_clip,
            output_path = generate_unique_path(
                temp_path = assets.temp_path,
                file_type = "mov"
            )
        )
        print("creating overlay_video_image")
        return edit.overlay_video_image(
            base_video = main,
            overlay_video = clips,
            output_path = generate_unique_path(
                temp_path = assets.temp_path,
                file_type = "mp4"
            )
        )
    
    def _final_video(self, video: Video, video_info) -> None:
        """
        Handles finalization steps such as watermarking, background music, 
        and exporting the video in different formats.

        Args:
            video (Video): The final video ready for export.
        """
        print(video_info)
        return add_video_info(
            video = video,
            output_path = os.path.join(assets.temp_path,f'{video_info.title}.{video_info.file_type}'),
            watermark = video_info.get('watermark', None),
            bg_audio = video_info.get('bg_audio', None),
            end_video = video_info.get('end_video', None)   
        )
    
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
        self.semi_clip =[]
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
            raise
            
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