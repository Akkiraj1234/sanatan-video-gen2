from typing import List, Tuple, Literal, Optional
from video_gen.editor.media import Video, Audio
from video_gen.editor.ffmpeg import ffmpeg
from video_gen.utils import assets
import os
import shutil


import cv2
import numpy as np
import os

def countdown_video(
    count=5,
    width=720,
    height=1080,
    font=cv2.FONT_HERSHEY_SIMPLEX,
    output_file = "countdown.mov",
    audio:str|None = None
    ):
    fps = 30  # Frames per second
    duration = 1  # Each number appears for 1 second
    total_frames = fps * duration  # Now only 30 frames per number
    fade_duration = fps * 0.5  # Frames for fade-in and fade-out (0.5 sec)
    output_folder = os.path.join(os.path.dirname(output_file), "frames")

    # Create output folder for frames   
    os.makedirs(output_folder, exist_ok=True)

    frame_index = 0

    for i in range(count, 0, -1):
        for frame in range(total_frames):
            img = np.zeros((height, width, 4), dtype=np.uint8)  # 4 channels (RGBA)

            scale = 1 + 0.5 * np.sin(frame / total_frames * np.pi)  # Zoom in and out effect
            base_font_size = min(width, height) / 20  # Relative font size
            font_scale = scale * (base_font_size / 50)  # Adjust size dynamically
            thickness = max(1, int(scale * (base_font_size / 10)))  # Adjust thickness

            text_size = cv2.getTextSize(str(i), font, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2

            # Fade-in and fade-out effect
            if frame < fade_duration:
                alpha = int((frame / fade_duration) * 255)  # Fade-in
                bg_alpha = int((1 - (frame / fade_duration)) * 100)  # Background fades out
            elif frame > total_frames - fade_duration:
                alpha = int(((total_frames - frame) / fade_duration) * 255)  # Fade-out
                bg_alpha = int(((frame - (total_frames - fade_duration)) / fade_duration) * 100)  # Background fades in
            else:
                alpha = 255  # Fully visible
                bg_alpha = 0  # No background

            # Add semi-transparent black background effect for fade
            if bg_alpha > 0:
                img[:, :, 3] = bg_alpha  # Set transparency channel for background

            cv2.putText(img, str(i), (text_x, text_y), font, font_scale, (0, 255, 0, alpha), thickness, cv2.LINE_AA)

            # Save frame as a PNG image
            frame_filename = os.path.join(output_folder, f"frame_{frame_index:04d}.png")
            cv2.imwrite(frame_filename, img)
            frame_index += 1
    
    # ffmpeg -framerate 30 -i frames/frame_%04d.png -i frames/bg.mp3 -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -c:a aac -b:a 192k -shortest countdown.mov
    cmd = []
    cmd.extend(["-framerate", str(fps)])
    cmd.extend(["-i", os.path.join(output_folder, "frame_%04d.png")])
    if audio:
        cmd.extend(["-i", audio])
    cmd.extend(["-c:v", "prores_ks"])
    cmd.extend(["-profile:v", "4444"])
    cmd.extend(["-pix_fmt", "yuva444p10le"])
    cmd.extend(["-c:a", "aac"])
    cmd.extend(["-b:a", "192k"])
    if audio:
        cmd.extend(["-shortest"])
    cmd.extend(["-y",output_file])
    
    ffmpeg.run("ffmpeg",cmd)
    shutil.rmtree(output_folder)
    return Video(output_file)