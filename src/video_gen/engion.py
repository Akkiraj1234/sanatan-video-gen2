from video_gen.audio_gen import Tts, get_timestamps
from video_gen.subtitles_gen import generate_flow_image
from video_gen.editor.edit import edit
from video_gen.utility import generate_unique_path, os

demo = [
    {
        'frame': 30,
        'size': (720, 1080),
        'file_type': 'mp4',
        'file_name': 'demo1',
        'template': 'demo_template.temp1',
        'bg_audio': '/home/akkiraj/Desktop/sanatan-video-gen2/media/audio/video3.mp4'
    },
    {
        'video': "Video: 1080x1920 @ 30.0 fps (h264), Format: mov,mp4,m4a,3gp,3g2,mj2, File Size: 3181727",
        'text': ['this is demo text']
    },
    {
        'video': "Video: 720x1280 @ 29.97 fps (h264), Format: mov,mp4,m4a,3gp,3g2,mj2, File Size: 1859997", 
        'text': ['this is demo text2', 'this is demo text3']
    }
]

font_path = "/home/akkiraj/Desktop/sanatan-video-gen2/media/font/Mangal Regular.ttf"
temp_folder = "/home/akkiraj/Desktop/sanatan-video-gen2/media/temp"

def gen_video(task:list) :
    size = task[0]['size']
    frame = task[0]['frame']
    file_name = task[0]['file_name']
    bg_audio = task[0]['bg_audio']
    template = task[0]['template']
    file_type = task[0]['file_type']
    
    # video creation set up
    tts = Tts()
    editor = edit()
    final_clip = []
    
    for clip_info in task[1:]:
        media = clip_info.get("video",None)
        texts = clip_info.get("text",None)
        
        if media is None or texts is None:
            print("media and video dont have pair")
            continue
        
        subtitles_clip = []
        
        for text in texts:
            audio = tts.create(text)
            timestamps = get_timestamps(text, audio)
            frame_paths = generate_flow_image(
                text = text,
                font_size = 50,
                font_path = font_path,
                output_folder = temp_folder
            )
            video = editor.concatenate_by_image(
                audio = audio,
                timestamps = timestamps,
                images = frame_paths,
                output_path = generate_unique_path(
                    temp_path=temp_folder,
                    file_type="mov"
                )
            )
            os.remove(audio.file_path)
            for path in frame_paths:
                os.remove(str(path)) 
            subtitles_clip.append(video)
        
        # concatenating those 2 or more videos
        main_sub_video = editor.concatenate_by_video(
            videos = subtitles_clip,
            output_path = generate_unique_path(
                    temp_path=temp_folder,
                    file_type="mov"
            )
        )
        
        
        _ = input("lets not be too fast")
        
        # print(audio.file_path)
        # print(timestamps)
        # for path in frame_paths:
        #     print(path) 
        # _ = input("here is till test if works or not")
            
    
    
    



