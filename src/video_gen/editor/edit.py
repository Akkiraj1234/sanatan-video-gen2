from typing import List, Tuple, Literal, Optional
from video_gen.editor.media import Video, Audio
from video_gen.editor.ffmpeg import ffmpeg
from video_gen.utils import assets
import os



VALID_TRANSITIONS = Literal[
    "fade", "fadeblack", "fadewhite", "distance",
    "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown",
    "smoothleft", "smoothright", "smoothup", "smoothdown",
    "circlecrop","rectcrop","circleclose", "circleopen",
    "horzclose", "horzopen", "vertclose", "vertopen",
    "diagbl", "diagbr", "diagtl", "diagtr", 
    "hlslice", "hrslice", "vuslice", "vdslice",
    "dissolve", "pixelize", "radial", "hblur",
    "wipetl", "wipetr", "wipebl", "wipebr",
    "fadegrays", "squeezev", "squeezeh", "zoomin",
    "hlwind", "hrwind", "vuwind","vdwind",
    "coverleft", "coverright", "coverup ","coverdown",
    "revealleft", "revealright","revealup,"
]

class edit:
    
    @staticmethod
    def concatenate_by_image(
        audio: Audio,
        timestamps: List[Tuple[float,float,str]],
        images: List[Video],
        output_path: str
    ) -> Optional[Video]:
        """
        Generate video clip from images synchronized with audio using timestamps
        Args:
            audio: Audio object to use as soundtrack
            timestamps: List of (start_ms, end_ms, text) for each image
            images: List of Image objects in order
            output_path: Output video path
        """
        if len(timestamps) != len(images):
            print("Mismatch between timestamps and images count")
            return None
        
        list_file = os.path.join(assets.temp_path,"concat.txt")
        with open(list_file,"w",encoding="utf-8") as f:
            for idx, ((start, end, _), image) in enumerate(zip(timestamps, images)):
                duration = (end - start) / 1000  # Convert ms to seconds
                f.write(f"file '{image.file_path}'\n")
                f.write(f"duration {duration:.3f}\n")
            
            # Repeat last frame to match audio length
            f.write(f"file '{images[-1].file_path}'\n")

        # Build FFmpeg command matching old method's settings
        cmd = [
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-i", str(audio),
            "-c:v", "qtrle",              # Use QuickTime Animation (RLE) codec
            "-pix_fmt", "argb",           # Preserve alpha channel
            "-c:a", "aac", "-strict", "experimental",  # Required for AAC in older FFmpeg
            "-shortest", "-y", str(output_path)
        ]

        if not ffmpeg.run('ffmpeg', cmd):
            return None
        os.remove(list_file)
        return Video(output_path)

    @staticmethod
    def convert_video(
        input_video: Video, 
        output_video: str
    ) -> Video:
        cmd = [ '-i', str(input_video) ]
        
        if output_video.endswith('.mp4'):
            cmd.extend(['-c:v', 'libx264','-pix_fmt', 'yuv420p'])
        elif output_video.endswith('.mov'):
            cmd.extend(['-c:v', 'prores_ks','-pix_fmt', 'yuva420p'])
        else:
            raise ValueError("Output video must be either .mp4 or .mov")
        
        cmd.extend(['-c:a', 'aac', output_video])
        ffmpeg.run("ffmpeg",cmd)
        return Video(output_video)

    @staticmethod
    def concatenate_by_video(
        videos: str,
        audio: bool = True,
        output_path = ''
    ) -> Video:
        # Ensure there are at least two videos to concatenate
        if len(videos) <= 1:
            return edit.convert_video(videos[0],output_path)
        
        cmd = []
        for video in videos:
            cmd.extend(['-i', str(video)])
        
        # Prepare the filter_complex argument
        filter_complex = []
        for idx in range(len(videos)):
            filter_complex.append(f"[{idx}:v][{idx}:a]")
        
        
        filter_complex.append(f"concat=n={len(videos)}:v=1:a=1[v][a]")
        cmd.extend(['-filter_complex', ' '.join(filter_complex)])
        cmd.extend(['-map', '[v]', '-map', '[a]','-c:v','prores_ks',output_path])
        ffmpeg.run('ffmpeg',cmd)
        
        return Video(output_path)
    
    @staticmethod
    def overlay_video_image(
        base_video: Video,
        overlay_video: Video, 
        output_path: str
    ) -> Video:
        video_size = f"{overlay_video.width}x{overlay_video.height}"  # Corrected order (width x height)

        cmd = [
            '-i', str(base_video),   # Base video (background)
            '-i', str(overlay_video) # Overlay video
        ]

        filter_complex = (
            f"[0:v]scale={video_size},fps={overlay_video.fps},format=rgba[bg];"
            f"[bg][1:v]overlay=0:0:format=auto[video]"
        )

        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[video]', '-map', '1:a',  # Map video & audio
            '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
            '-shortest', '-y', str(output_path)  # Stop when shorter video ends
        ])
        ffmpeg.run('ffmpeg',cmd,True)
        return Video(output_path)
    
    @staticmethod
    def concatenate_steam(
        *videos: Video,
        output_path: str,
        transition_effect:VALID_TRANSITIONS|None = None,
        transition_duration: int = 1
    ) -> Video:
        """
        Concatenates video
        """
        size = "720x1080"
        cmd = []
        frame_rate = 24
        
        for video in videos:
            cmd.extend(['-i', str(video)])
        
        # Apply scale filter so no error raise
        filter_complex = []
        for idx in range(len(videos)):
            filter_complex.append(f"[{idx}:v]scale={size},fps={frame_rate},settb=AVTB[vid{idx}]")
        
        
        # Generate xfade transitions method
        xfade = lambda id1,id2,out,offset: filter_complex.append(
            (f"[{id1}][{id2}]xfade=transition={transition_effect}:"
            f"duration={transition_duration}:offset={offset}[{out}]")
        )
        # 1. creating first videos
        nidx = ('v0',videos[0].duration-transition_duration)
        xfade('vid0','vid1',nidx[0],nidx[1])
        nidx = (nidx[0], nidx[1] + videos[1].duration-transition_duration)
        
        # 2. creating remain videos
        for idx in range(2,len(videos)):
            xfade(nidx[0], f'vid{idx}', f'v{idx-1}', nidx[1])
            nidx = (f'v{idx-1}', nidx[1] + videos[idx].duration-transition_duration)
        
        audio_concat = "".join([f"[{idx}:a]" for idx in range(len(videos))])
        audio_filter = f"{audio_concat}concat=n={len(videos)}:v=0:a=1[a]"
        filter_complex.append(audio_filter)
        
        # final output
        filter_complex.append(f"[{nidx[0]}]format=yuv420p[final]")
        cmd.extend(['-filter_complex', '; '.join(filter_complex)])
        cmd.extend(['-map', '[final]','-y','-map','[a]', output_path])
        
        ffmpeg.run('ffmpeg', cmd, False)
        return Video(output_path)

    