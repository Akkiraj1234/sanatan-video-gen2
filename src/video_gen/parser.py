from video_gen.editor.media import Video
from colorama import Fore, Style
import re

def parse_file(file_path):
    """
    Parse the file and return a list of task lists.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Find all blocks that start with [title: ...]
    blocks = re.findall(r'\[title:\s*(.*?)\](.*?)(?=\n\[title:|\Z)', content, re.DOTALL)
    
    tasks_list = []
    
    for title, block_content in blocks:
        tasks = []
        # Default metadata values
        metadata = {
            'frame': 30,
            'size': (1080, 1920),
            'file_type': 'mp4',
            'file_name': title,
            'template': None,
            'bg_audio': None
        }
        media_items = []
        texts = []

        # Process each line in the block
        for line in block_content.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                
                if key == 'size':
                    w, h = map(int, value.split('x'))
                    metadata['size'] = (w, h)
                elif key == 'frame':
                    metadata['frame'] = int(value)
                elif key == 'file_type':
                    metadata['file_type'] = value
                elif key == 'template':
                    metadata['template'] = value
                elif key.startswith('audio'):
                    metadata['bg_audio'] = value
                elif key.startswith('video') or key.startswith('image'):
                    # Decide on media type based on the key name
                    media_type = 'video' if 'video' in key.lower() else 'image'
                    # Create a Video (or Image) object here. For simplicity, we'll assume Video.
                    media_items.append({media_type: Video(value)})
                elif key.startswith('text'):
                    # Allow multiple texts; if it's a list-like string, evaluate it.
                    if value.startswith('[') and value.endswith(']'):
                        texts.extend(eval(value))
                    else:
                        texts.append(value)

        # Distribute texts among the media items
        if media_items:
            # Calculate how many texts per media item (ensuring at least 1 per item)
            per_item = len(texts) // len(media_items)
            if per_item == 0:
                per_item = 1
            for i, item in enumerate(media_items):
                start = i * per_item
                # For the last item, assign all remaining texts
                end = (i + 1) * per_item if i < len(media_items) - 1 else len(texts)
                item['text'] = texts[start:end]
        
        tasks.append(metadata)
        tasks.extend(media_items)
        tasks_list.append(tasks)
    
    return tasks_list

def print_task(tasks, detail: int = 2):
    """Print tasks in a visual format with colored output."""
    metadata = tasks[0]
    media_items = tasks[1:]
    
    # Color configuration
    TITLE = Fore.LIGHTCYAN_EX
    META = Fore.GREEN
    MEDIA_HEADER = Fore.MAGENTA
    PAIR = Fore.BLUE
    TEXT = Fore.MAGENTA
    VALUE = Fore.CYAN
    AUDIO = Fore.BLUE
    ICON_VIDEO = Fore.RED
    ICON_IMAGE = Fore.GREEN

    # Metadata section
    print(f"{Style.RESET_ALL}▌ {TITLE}Title: {VALUE}{metadata['title']}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}├─ {META}Size: {VALUE}{metadata['width']}x{metadata['height']}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}├─ {META}Frame Rate: {VALUE}{metadata['frame']}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}├─ {META}File Type: {VALUE}{metadata['file_type']}{Style.RESET_ALL}")
    
    if detail < 1:
        return

    # Media items section
    print(f"{Style.RESET_ALL}├─ {MEDIA_HEADER}Media Items:{Style.RESET_ALL}")
    for i, item in enumerate(media_items, 1):
        media_type = 'video' if 'video' in item else 'image'
        icon = '🎥' if media_type == 'video' else '🖼'
        icon_color = ICON_VIDEO if media_type == 'video' else ICON_IMAGE
        
        print(f"{Style.RESET_ALL}│  ╰─ {icon_color}{icon}{Style.RESET_ALL} {PAIR}Pair {i}: {VALUE}{item[media_type]}{Style.RESET_ALL}")
        texts = ', '.join(item.get('text', []))
        print(f"{Style.RESET_ALL}│     ╰─ {TEXT}Texts: {VALUE}{texts or 'None'}{Style.RESET_ALL}")
        
        if detail >= 2:
            transition = item.get('transition', "no transition")
            effect = ', '.join(item['effect']) if item.get('effect') else 'no effect'
            print(f"{Style.RESET_ALL}│     ╰─ {TEXT}Transition: {VALUE}{transition}{Style.RESET_ALL}")
            print(f"{Style.RESET_ALL}│     ╰─ {TEXT}Effect: {VALUE}{effect}{Style.RESET_ALL}")

    # Audio section
    print(f"{Style.RESET_ALL}├─ {AUDIO}Audio Files: {VALUE}{metadata.get('bg_audio', 'None')}{Style.RESET_ALL}")
    print(f"{Style.RESET_ALL}╰─{'─' * 40}{Style.RESET_ALL}\n")

def demo_json_data():
    return [
        [
            {
                "title":"hanumanji",
                "width":1080,
                "height":720,
                "frame":30,
                "file_type":"mp4"
            },
            {
                "video":"/home/akkiraj/Desktop/sanatan-video-gen2/media/image/shrihanuman_v_1.jpg",
                "text":["श्री हनुमान जी की कृपा से असंभव भी संभव है।", "संकट मोचक हनुमान, भक्तों के कष्ट हरने वाले।", "राम नाम की शक्ति से जीवन में हर बाधा दूर होती है।"],
                "transition": "fade",
                "effect":["scale-down", "flower-rain"]
            },
            {
                "video":"/home/akkiraj/Desktop/sanatan-video-gen2/media/image/shrihanuman_v_2.jpg",
                "text": ["जय श्री राम!", "श्री हनुमान जी की असीम कृपा सदैव बनी रहे।"],
                "transition": "fade",
                "effect":["scale-down", "flower-rain"]
            },
            {
                "video":"/home/akkiraj/Desktop/sanatan-video-gen2/media/image/shrihanuman_v_3.jpg",
                "text":["हनुमान जी की भक्ति से अजेय बनो।"],
                "transition": "dissolve",
                "effect":["scale-down", "white-flower-rain"]
            },
            {
                "video":"/home/akkiraj/Desktop/sanatan-video-gen2/media/image/shrihanuman_v_3.jpg",
                "text":["इस तरह के वीडियो के लिए सनातन का पालन करें", "देखने के लिए धन्यवाद"],
                "effect":["fade", "white-flower-rain"]
            }
        ],
        [
            {
                "title":"radhaji",
                "width":720,
                "height":1080,
                "frame":60,
                "file_type":"mp4"
            },
            {
                "video":"/home/akkiraj/Desktop/sanatan-video-gen2/media/video/video2.mp4",
                "text":["श्री हनुमान जी की कृपा से असंभव भी संभव है?", ":countdown:3:"],
                "transition": "fade"
            },
            {
                "video":"/home/akkiraj/Desktop/sanatan-video-gen2/media/video/video1.mp4",
                "text": ["श्री हनुमान जी की कृपा से असंभव भी संभव है।", "संकट मोचक हनुमान, भक्तों के कष्ट हरने वाले।", "राम नाम की शक्ति से जीवन में हर बाधा दूर होती है।"],
                "transition": "fade"
            },
        ]
    ]