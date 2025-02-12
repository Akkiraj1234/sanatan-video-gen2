from video_gen.editor.media import Audio, Video
from video_gen.editor.ffmpeg import FFmpeg
from typing import Literal
import os


countdown_effects = Literal[
    "fade"
]
ffmpeg = FFmpeg()
dir_path = '/home/akkiraj/Desktop/sanatan-video-gen2'

def countdown(
    media:Video, 
    countdown:int = 3,
    backward:bool = True,
    effect:countdown_effects = 'fade'
    ) -> Video:
    
    cmd = []
    duration = countdown
    audio_path = os.path.join(dir_path,'media','audio','countdown-been.wav')
    
    # adding command one by one to cmd
    cmd.extend(['-i',str(media)])
    cmd.extend(['-i',audio_path])
    
    cmd.append('-filter_complex')
    filter_complex = []
    filter_complex.append(f"[0:v]loop={int(countdown//media.duration)}:30:0,trim=start=0:duration={duration}[v1];")
    #calculating for video resizing
    d = (duration/countdown)/2
    filter_complex.append('[v1]')
    for num in range(countdown):
        filter_complex.append(
            f"fade=in:st={(d*2)*num}:d={d},fade=out:st={((d*2)*num)+d}:d={d}"
        )
    filter_complex.extend(['[v2]'])
    cmd.append(''.join(filter_complex))
    cmd.extend(['-map','[v2]', os.path.join(dir_path,'output.mp4')])
    print('ffmpeg',' '.join(cmd))
    lol = ffmpeg.run('ffmpeg',cmd)
    print(lol.stderr)
    
if __name__ == "__main__":
    countdown(
        Video('/home/akkiraj/Desktop/sanatan-video-gen2/media/video/video1.mp4',)
    )