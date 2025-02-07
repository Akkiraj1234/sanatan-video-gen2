from video_gen.editor.media import Video
import re


def process_input_file(file_path: str) -> None:
    """
    Reads and processes the content of the specified input file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print("Successfully read the file content.")
            
    except FileNotFoundError:
        print("Error: The file '%s' was not found.", file_path)
        
    except Exception as e:
        print("An unexpected error occurred while reading the file: %s", e)



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

def print_tasks(tasks):
    """Print tasks in a visual format from the list of tasks."""
    metadata = tasks[0]
    media_items = tasks[1:]
    
    print(f"▌ Title: {metadata['file_name']}")
    print(f"├─ Template: {metadata['template']}")
    print(f"├─ Size: {metadata['size'][0]}x{metadata['size'][1]}")
    print(f"├─ Frame Rate: {metadata['frame']}")
    print(f"├─ File Type: {metadata['file_type']}")
    print("├─ Media Items:")
    for i, item in enumerate(media_items, 1):
        # Decide the media type by checking for the key in the dictionary
        if 'video' in item:
            media_type = 'video'
            icon = '🎥'
        else:
            media_type = 'image'
            icon = '🖼'
        texts = ', '.join(item.get('text', []))
        # Assuming the Video (or Image) object has a .path attribute
        print(f"│  ╰─ {icon} Pair {i}: {item[media_type].file_path}")
        print(f"│     ╰─ Texts: {texts or 'None'}")
    print(f"├─ Audio Files: {metadata['bg_audio'] or 'None'}")
    print("╰─" + "─" * 40 + "\n")

