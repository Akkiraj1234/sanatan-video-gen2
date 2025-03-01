from video_gen import init
from video_gen.utils import get_error_details
import logging



def main():
    init()



if __name__ == "__main__":
    try: main()
    except Exception as e:
        module_name, lineno = get_error_details(e)
        logging.error(str(e), extra={'custom_lineno': lineno, 'custom_name': module_name})