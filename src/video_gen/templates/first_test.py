from video_gen.editor.edit import Editor
from video_gen.editor.media import Image, Video, Audio
from settings import setting

# Initialize editor and media objects
editor = Editor()
images = [
    Image("image1.jpg"),
    Image("image2.png"),
    Image("image3.webp")
]

# 1. Create basic slideshow
basic_video = editor.create_slideshow(
    images=images,
    output_path="basic_slideshow.mp4",
    duration=3.0,  # 3 seconds per image
    fps=24
)

# 2. Create advanced slideshow with effects
advanced_video = editor.create_slideshow(
    images=images,
    output_path="advanced_slideshow.mp4",
    duration=5.0,  # 5 seconds per image
    fps=30
).apply_filterchain(
    output_path="with_effects.mp4",
    filter_complex="""
    [0:v] split [base][zoom];
    [zoom] scale=iw*1.1:ih*1.1, boxbuf=2, fade=out:50:30 [blurred];
    [base][blurred] overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2
    """
)

# 3. Add background music
music = Audio("background_music.mp3")
final_video = editor.add_background_music(
    video=advanced_video,
    audio=music,
    output_path="final_video.mp4",
    volume=0.4  # Reduce music volume to 40%
)

# 4. Add opening/closing effects
title_card = Image("title.png")
end_card = Image("credits.png")

edited_video = editor.concatenate(
    inputs=[
        title_card.to_video(duration=2.0),  # Display title for 2 seconds
        final_video,
        end_card.to_video(duration=3.0)     # Display credits for 3 seconds
    ],
    output_path="edited_final.mp4"
)

print(f"Created final video: {edited_video.file_path}")
print(edited_video.get_summary())