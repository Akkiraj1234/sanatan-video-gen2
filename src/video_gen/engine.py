from video_gen.settings import setting
from video_gen.editor.media import Video, Audio, Font
from video_gen.editor.ffmpeg import FFmpeg
from video_gen.editor.edit import Editor
from video_gen.subtitles_gen.image_gen import generate_flow_image
from video_gen.audio_gen import Tts, get_timestamps
from video_gen.utility import generate_unique_path
import os

tasks = iter(
    [
        {
            "frame":30,
            "size":(1080,720),
            "file_type":"mp4",
            "file_name":"hanumanji",
            "template":"temp3",
            "bg_audio":None
        },
        {
            "media":Video("media/image/shrihanuman_h_1.jpg"),
            "text":["this is demo text1", "this is demo text2", "this is demo text3"],
        },
        {
            "media":Video("media/image/shrihanuman_h_2.jpg"),
            "text":["this is another demo text", "this is another last demo text"],
        },
        {
            "media":Video("media/image/shrihanuman_h_3.jpg"),
            "text":["this is last demo text"]
        }
    ]   
)

def generate_demo_video(anything:str):
    clip_paths = []
    video_info = next(tasks)
    frame = video_info.get("frame",30)
    size = video_info.get("size", (1080,720))
    file_type = video_info.get("file_type")
    bg_audio = video_info.get("bg_audio", None)

    # video creation set up
    tts = Tts()
    editor = Editor()

    for clip_info in tasks:
        media = clip_info.get("media",None)
        texts = clip_info.get("text",None)
        
        if media is None or texts is None:
            print("media and video dont have pair")
            continue
        
        texts_clip = []
        for text in texts:
            audio = Audio(tts.create(text))
            timestamps = get_timestamps(text,audio)
            frame_paths = generate_flow_image(
                text,
                50,
                setting.paths.font,
                output_folder=setting.paths.temp
            )
            video = editor.generate_video_clip(
                audio,
                timestamps,
                frame_paths,
                generate_unique_path(
                    setting.paths.temp,
                    "mov"
                )
            )
            os.remove(audio.file_path)
            for path in frame_paths:
                os.remove(path.file_path)
            print(video.file_path)
            texts_clip.append(video)
        print("new line of text")
        


# for paragraph in word_list:
#     audio_path = TTS_gtts(
#         script = paragraph,
#         output_path = assets.image_path
#     )
#     timestamps = get_timestamps(
#         text = paragraph,
#         audio_path = audio_path
#     )
#     image_paths = generate_flow_image(
#         text=paragraph,
#         font_size=50,
#         font_path=assets.font,
#         output_folder = assets.image_path
#     )
#     path = os.path.join(assets.image_path,f"clip{num}.mov")
#     generate_video_clip(
#         audio_path = audio_path,
#         timestamps = timestamps,
#         image_folder = assets.image_path,
#         output_video_path = path
#     )
#     num+=1
#     clips_path.append(path)

# video_path = concatenate_videos(
#     assets.video1,
#     assets.video2,
#     "raw_video.mp4"
# )

# overlay_video = concatenate_transparent_videos(
#     os.path.join(assets.image_path, "clip0.mov"),
#     os.path.join(assets.image_path, "clip1.mov"),
#     "mov_files.mov"
# )
# os.remove(os.path.join(assets.image_path, "clip0.mov"))
# os.remove(os.path.join(assets.image_path, "clip1.mov"))

# print(video_path, overlay_video, "\n\n\n\n\n")

# overlay_and_trim_video(
#     overlay_video,
#     video_path,
#     "final_output.mp4"
# )
# os.remove(video_path)
# os.remove(overlay_video)