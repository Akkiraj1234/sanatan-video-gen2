from video_gen.audio_gen import get_TTSModel
from video_gen.editor.media import Video, Audio
from video_gen.assets import Assets
from video_gen.settings import setting
from video_gen.editor import (
    edit, 
    gen_trans_sub,
    typing_gen_trans_sub,
    typing_gen_trans_sub_std,
    effect_get,
    add_video_info
)
from video_gen.utils import (
    generate_unique_path,
    os, AttrDict,
    clean_files, 
    print_task,
    copy_file,
    TempFile,
    SafeFile
)
from typing import List, Dict


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
        self.temp_file = TempFile()
        self.texttospeach = get_TTSModel()
        self.failed_tasks = []  # Stores failed tasks along with error messages
        self.semi_clip = []
        self.count = 0          # Number of successfully created videos
        self.total = 0          # Total attempted video creations
    
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
            'height': info.get('height', 1280),
            'fps': info.get('fps', 24),
            'title': info.get('title', 'no_title'),
            'file_type': info.get('file_type', 'mp4'),
            'font_name': Assets.Font.getpath(info.get('font', None)),
            'font_size': info.get('font_size', 70),
            'bg_audio': info.get('bg_music', None),
            'watermark': info.get('watermark', None),
            'end_video': info.get('end_video', None),
            'padding': info.get('padding', 100),
            'text_color': info.get('text_color', '#FFFF00')
        })

    def _nano_clip_creation(self, text:str, file_info) -> Video:
        """
        the dict should contain media info and text
        if not raise value error
        """
        # generating the music
        
        
        timestamps, audio = self.texttospeach.create_with_timestamp(
            script = text,
            output_path = self.temp_file.create_unique_file("mp3")
        )
        
        # mov = gen_trans_sub(
        mov = typing_gen_trans_sub_std(
            text = text,
            audio = audio,
            timestamps = timestamps,
            file_info = file_info,
            output_file = self.temp_file.create_unique_file("mov"),
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
            v_postion = task.get('v_postion', 'center')
        except KeyError as e:
            raise ValueError('the format is not correct cloudnet find media and effect')
        
        video = media
        for effect in video_effect:
            effect = effect_get.get(effect)
            video = effect(
                input_path = video,
                output_path = self.temp_file.create_unique_file("mov"),
                total_duration = duration,
                position = v_postion
            )

        if video_effect == []:
            video = effect_get.get('no_effect')(
                input_path = media,
                output_path = self.temp_file.create_unique_file("mp4"),
                duration = duration,
                width = file_info.width,
                height = file_info.height,
                position = v_postion
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
        
        if extra and extra is not None:
            nano_clips.append(
                Assets.Clips.get(extra)(
                    count=3,
                    width=file_info.width,
                    height=file_info.height,
                    output_file = self.temp_file.create_unique_file("mov"),
                    audio = os.path.join("/home/akkiraj/Desktop/QuestionAnswerAssets/QuestionAnswerAssets", "sfxCountdown.wav"),
                    font_path = file_info.font_name,
                    color = file_info.text_color
                )
            )
        
        semi_clip = edit.concatenate_by_video(
            videos = nano_clips,
            output_path = self.temp_file.create_unique_file('mov')
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
        main = edit.concatenate_stream(
            *clips,
            output_path = self.temp_file.create_unique_file("mp4"),
            transition_duration=1,
            transition_effect=None,
            width = fine_info.width,
            height = fine_info.height
        )
        print("creating concatenate_by_video")
        clips = edit.concatenate_by_video(
            self.semi_clip,
            output_path = self.temp_file.create_unique_file("mov")
        )
        print("creating overlay_video_image")
        return edit.overlay_video_image(
            base_video = main,
            overlay_video = clips,
            output_path = self.temp_file.create_unique_file("mp4"),
        )
    
    def _final_video(self, video: Video, video_info) -> None:
        """
        Handles finalization steps such as watermarking, background music, 
        and exporting the video in different formats.

        Args:
            video (Video): The final video ready for export.
        """
        return add_video_info(
            video = video,
            output_path = os.path.join(setting.temp_path,f'{video_info.title}.{video_info.file_type}'),
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
        path = None
        code = 1
        try:
            print_task(task, 1)  # Log the task details
            path = self.pipeline(task)
            print(f"Video successfully created and saved at: {path}\n\n")
            self.count += 1
            
        except Exception as e:
            self.failed_tasks.append([task, str(e)])
            print(f"Error occurred while creating video: {e}")
            print("Please check the task details and try again.\n")
            code = 0
            raise
            
        finally:
            self.total += 1
            return path, code, 'no message yet'
    
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