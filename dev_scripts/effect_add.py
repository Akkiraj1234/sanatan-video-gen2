import sys
import os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video_gen_path = os.path.join(path,"src")
sys.path.append(video_gen_path)

from video_gen.editor.edit import remove_green_screen_and_save_as_mov
effect_list = [
    '/home/akkiraj/Desktop/sanatan-video-gen2/assets/effects/Rose petals falling green screen [_Di04vHCVxs].webm'
]


remove_green_screen_and_save_as_mov(*effect_list)