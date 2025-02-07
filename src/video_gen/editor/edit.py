from video_gen.editor.media import Video, Audio
from video_gen.editor.ffmpeg import FFmpeg
from typing import List, Dict, Literal
ffmpeg = FFmpeg()

class edit:
    
    def __init__(self):
        pass
    
    
    def concatenate_by_image(self) -> Video:
        
        pass
    
    


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

 

def concatenate_steam(
    *videos: Video,
    output_path: str,
    transition_effect:VALID_TRANSITIONS|None = None,
    transition_duration: int = 2
) -> Video:
    """
    Concatenates video
    """
    size = "720x1080"
    cmd = []
    frame_rate = 24
    
    for video in videos:
        cmd.extend(['-i', str(video.file_path)])
    
    # Apply scale filter so no error raise
    filter_complex = []
    for idx in range(len(videos)):
        filter_complex.append(f"[{idx}:v]scale={size},fps={frame_rate},settb=AVTB[vid{idx}]")
    
    
    # Generate xfade transitions method
    xfade = lambda id1,id2,out,offset: filter_complex.append(
         f"[{id1}][{id2}]xfade=transition={transition_effect}:"
        +f"duration={transition_duration}:offset={offset}[{out}]"
    )
    # 1. creating first videos
    nidx = ('v0',videos[0].properties['duration']-transition_duration)
    xfade('vid0','vid1',nidx[0],nidx[1])
    nidx = (nidx[0], nidx[1] + videos[1].properties['duration']-transition_duration)
    
    # 2. creating remain videos
    for idx in range(2,len(videos)):
        xfade(nidx[0], f'vid{idx}', f'v{idx-1}', nidx[1])
        nidx = (f'v{idx-1}', nidx[1] + videos[idx].properties['duration']-transition_duration)
    
    # final output
    filter_complex.append(f"[{nidx[0]}]format=yuv420p[final]")
    cmd.extend(['-filter_complex', '"' + '; '.join(filter_complex) + '"'])
    cmd.extend(['-map', '[final]', output_path])
    
    print(' '.join(cmd))
    ffmpeg.run('ffmpeg', cmd, False)
    return Video(output_path)


