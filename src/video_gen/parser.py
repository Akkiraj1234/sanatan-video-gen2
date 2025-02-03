import logging

# logging configuration
logger = logging.getLogger(__name__)


def process_input_file(file_path: str) -> None:
    """
    Reads and processes the content of the specified input file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logger.info("Successfully read the file content.")
            # print("File content:\n", content)
            
    except FileNotFoundError:
        logger.error("Error: The file '%s' was not found.", file_path)
        
    except Exception as e:
        logger.exception("An unexpected error occurred while reading the file: %s", e)

import re
from collections import namedtuple

class Video:
    """Dummy class to represent media files"""
    def __init__(self, path):
        self.path = path
        
    def __repr__(self):
        return f"Video('{self.path}')"

def parse_file(file_path):
    """Parse the file and return an iterator of task lists"""
    with open(file_path, 'r') as f:
        content = f.read()

    blocks = re.findall(r'\[title:\s*(.*?)\](.*?)(?=\n\[title:|\Z)', content, re.DOTALL)
    
    for title, block_content in blocks:
        tasks = []
        metadata = {
            'frame': 30,
            'size': (1920, 1080),
            'file_type': 'mp4',
            'file_name': title,
            'template': None,
            'bg_audio': None
        }
        media_items = []
        texts = []
        current_texts = []

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
                    media_type = 'video' if 'video' in key else 'image'
                    media_items.append({media_type: Video(value)})
                elif key.startswith('text'):
                    if value.startswith('[') and value.endswith(']'):
                        texts.extend(eval(value))
                    else:
                        texts.append(value)

        # Distribute texts to media items
        if media_items:
            per_item = len(texts) // len(media_items) or 1
            for i, item in enumerate(media_items):
                start = i * per_item
                end = (i+1) * per_item if i < len(media_items)-1 else len(texts)
                item['text'] = texts[start:end]

        tasks.append(metadata)
        tasks.extend(media_items)
        
        yield iter(tasks)

def print_tasks(task_iter):
    """Print tasks in the visual format"""
    for tasks in task_iter:
        task_list = list(tasks)
        metadata = task_list[0]
        media_items = task_list[1:]
        
        print(f"▌ Title: {metadata['file_name']}")
        print(f"├─ Template: {metadata['template']}")
        print(f"├─ Size: {metadata['size'][0]}x{metadata['size'][1]}")
        print(f"├─ Frame Rate: {metadata['frame']}")
        print(f"├─ File Type: {metadata['file_type']}")
        
        print("├─ Media Items:")
        for i, item in enumerate(media_items, 1):
            media_type = 'video' if 'video' in item else 'image'
            icon = '🎥' if media_type == 'video' else '🖼'
            texts = ', '.join(item.get('text', []))
            print(f"│  ╰─ {icon} Pair {i}: {item[media_type].path}")
            print(f"│     ╰─ Texts: {texts or 'None'}")

        print(f"├─ Audio Files: {metadata['bg_audio'] or 'None'}")
        print("╰─" + "─" * 40 + "\n")