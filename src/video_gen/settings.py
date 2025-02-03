# import configparser
# import os
# import logging

# # Logging setup
# logger = logging.getLogger(__name__)

# # path management for config.ini, change it according to 
# # server and build the wheel again
# DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# CONFIG_PATH = os.path.join(DIR, "config.ini")


# # Other directories
# _medias_path = os.path.join(DIR, "medias")
# _ffmpeg_folder_path = os.path.join(_medias_path, "ffmpeg")
# _ffmpeg_path = os.path.join(_ffmpeg_folder_path, "ffmpeg")
# _ffprobe_path = os.path.join(_ffmpeg_folder_path, "ffprobe")
# _temp_path = os.path.join(_medias_path, "temp")
# _download_path = DIR

# _fonts_path = os.path.join(_medias_path, "fonts")
# _video_path = os.path.join(_medias_path, "videos")
# _audio_path = os.path.join(_medias_path, "audios")
# _image_path = os.path.join(_medias_path, "images")



# class ConfigManager:
#     _instance = None
#     _config_path = CONFIG_PATH
    
#     _default_data = {
#         "app_name": "MyApp",
#         "version": "1.0",
#         "theme": "dark",
#         "language": "en",
#         "debug": "True",
#         "ffmpeg": _ffmpeg_path,
#         "ffprobe": _ffprobe_path,
#         "temp": _temp_path,
#         "download": _download_path,
#         "lang-trans": "hi",
#         "use_method": "elevenlabs"
#     }

#     def __new__(cls):
#         """
#         Singleton instance management.
#         """
#         if cls._instance is None:
#             cls._instance = super(ConfigManager, cls).__new__(cls)
#             cls._instance._config = configparser.ConfigParser()
#             cls._instance._load_config()
#         else:
#             logger.warning("Attempt to create a new instance of ConfigManager is not allowed")
        
#         return cls._instance

#     def _load_config(self):
#         """
#         Loads the configuration file, creates it if missing, and checks for missing keys.
#         """
#         if not os.path.exists(self._config_path):
#             logger.warning("Config file not found. Creating a new one with default values...")
#             self._save_config(self._default_data)
        
#         self._config.read(self._config_path)
#         self._check_missing_keys()  # Ensure all required keys are present

#         # Convert to dictionary
#         self._settings = {section: dict(self._config[section]) for section in self._config.sections()}

#     def _check_missing_keys(self):
#         """
#         Checks for missing sections or keys and adds them from default values if needed.
#         """
#         updated = False

#         for section, keys in self._default_data.items():
#             if not self._config.has_section(section):
#                 logger.warning(f"Missing section [{section}]. Adding it...")
#                 self._config.add_section(section)
#                 updated = True
            
#             for key, value in keys.items():
#                 if not self._config.has_option(section, key):
#                     logger.warning(f"Missing key '{key}' in section [{section}]. Adding default value: {value}")
#                     self._config.set(section, key, value)
#                     updated = True
        
#         if updated:
#             self._save_config(self._config)

#     def _save_config(self, config_data):
#         """
#         Saves the configuration to a file.
#         """
#         for section, options in config_data.items():
#             if section == "DEFAULT":  # Skip adding the DEFAULT section manually
#                 continue
#             if not self._config.has_section(section):
#                 self._config.add_section(section)
#             for key, value in options.items():
#                 self._config.set(section, key, value)
        
#         with open(self._config_path, "w", encoding="utf-8") as file:
#             self._config.write(file)
#         logger.info("Config file updated with missing keys")

#         # Update in-memory settings
#         self._settings = {
#             section: dict(self._config[section]) for section in self._config.sections()
#         }
        
#     def get_settings(self):
#         """
#         Returns a copy of the configuration settings.
#         """
#         return self._settings.copy()

#     def update_info(self, new_data:dict):
#         """
#         Updates the configuration with new values.
#         """
#         if not isinstance(new_data, dict):
#             raise ValueError("Config data must be a dictionary.")
        
#         for section, values in new_data.items():
#             if section not in self._settings:
#                 self._settings[section] = {}
#             self._settings[section].update(values)
        
#         self._save_config(self._settings)
        
# class DotDict(dict):
#     """ Dictionary that allows dot notation access. """
#     def __getattr__(self, attr):
#         if attr in self:
#             value = self[attr]
#             return DotDict(value) if isinstance(value, dict) else value
#         raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")

# class AssetsManager(ConfigManager):
#     def __getattr__(self, attr):
#         """
#         If an attribute is not found normally, check in settings.
#         Allows accessing settings with dot notation.
#         """
#         settings = self.get_settings()
#         if attr in settings:
#             return DotDict(settings[attr])  # Convert section to DotDict
#         raise AttributeError(f"'AssetsManager' object has no attribute '{attr}'")


# # Create an instance
# setting = AssetsManager()

import configparser
import os
import logging

# Logging setup
logger = logging.getLogger(__name__)

# Path management for config.ini – adjust according to your server/build environment.
DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(DIR, "config.ini")

# Other directories
_ffmpeg_folder_path = os.path.join(DIR, "ffmpeg")
_ffmpeg_path = os.path.join(_ffmpeg_folder_path, "ffmpeg")
_ffprobe_path = os.path.join(_ffmpeg_folder_path, "ffprobe")

_medias_path = os.path.join(DIR, "media")
_temp_path = os.path.join(_medias_path, "temp")
_fonts_path = os.path.join(_medias_path, "font","A_Akhil Normal.ttf")
_download_path = DIR

# _video_path = os.path.join(_medias_path, "videos")
# _audio_path = os.path.join(_medias_path, "audios")
# _image_path = os.path.join(_medias_path, "images")


class ConfigManager:
    _instance = None
    _config_path = CONFIG_PATH

    # Group default configuration values into sections.
    _default_data = {
        "general": {
            "app_name": "MyApp",
            "version": "1.0",
            "theme": "dark",
            "language": "en",
            "debug": "True",
            "lang-trans": "hi",
            "tts_eng": "elevenlabs"
        },
        "paths": {
            "ffmpeg": _ffmpeg_path,
            "ffprobe": _ffprobe_path,
            "temp": _temp_path,
            "download": _download_path,
            "font":_fonts_path
        },
        "api":{
            "elevenlabs": "sk_9dadd4b84c2879c59a5e6078977235c224ccc8aa5ca1d797"
        }
    }

    def __new__(cls):
        """
        Singleton instance management.
        """
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = configparser.ConfigParser()
            cls._instance._load_config()
        else:
            logger.warning("Attempt to create a new instance of ConfigManager is not allowed")
        return cls._instance

    def _load_config(self):
        """
        Loads the configuration file. If missing, creates one with default values.
        Also checks for missing keys.
        """
        if not os.path.exists(self._config_path):
            logger.warning("Config file not found. Creating a new one with default values...")
            # Create sections and set default values
            for section, options in self._default_data.items():
                self._config.add_section(section)
                for key, value in options.items():
                    self._config.set(section, key, str(value))
            self._save_config()
        else:
            self._config.read(self._config_path)
            self._check_missing_keys()

        self._update_settings()

    def _check_missing_keys(self):
        """
        Checks for missing sections or keys in the config file and adds them from default values.
        """
        updated = False
        for section, options in self._default_data.items():
            if not self._config.has_section(section):
                logger.warning(f"Missing section [{section}]. Adding it...")
                self._config.add_section(section)
                updated = True

            for key, value in options.items():
                if not self._config.has_option(section, key):
                    logger.warning(f"Missing key '{key}' in section [{section}]. Adding default value: {value}")
                    self._config.set(section, key, str(value))
                    updated = True

        if updated:
            self._save_config()

    def _save_config(self):
        """
        Saves the current configuration to the config file.
        """
        with open(self._config_path, "w", encoding="utf-8") as file:
            self._config.write(file)
        logger.info("Config file updated with missing keys")
        self._update_settings()

    def _update_settings(self):
        """
        Updates the in-memory settings from the current config.
        """
        self._settings = {
            section: dict(self._config.items(section)) for section in self._config.sections()
        }

    def get_settings(self):
        """
        Returns a copy of the current configuration settings.
        """
        return self._settings.copy()

    def update_info(self, new_data: dict):
        """
        Updates the configuration with new values.
        Expects a dictionary where keys are section names.
        """
        if not isinstance(new_data, dict):
            raise ValueError("Config data must be a dictionary.")

        for section, values in new_data.items():
            if not self._config.has_section(section):
                self._config.add_section(section)
            for key, value in values.items():
                self._config.set(section, key, str(value))

        self._save_config()


class DotDict(dict):
    """Dictionary subclass that supports dot notation access."""
    def __getattr__(self, attr):
        if attr in self:
            value = self[attr]
            # Convert nested dictionaries to DotDict automatically.
            return DotDict(value) if isinstance(value, dict) else value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")


class AssetsManager(ConfigManager):
    def __getattr__(self, attr):
        """
        Allows accessing configuration sections via dot notation.
        For example, if there is a section named 'general', you can do:
            assets_manager.general.app_name
        """
        settings = self.get_settings()
        if attr in settings:
            return DotDict(settings[attr])
        raise AttributeError(f"'AssetsManager' object has no attribute '{attr}'")


# Create a singleton instance for accessing configuration settings.
setting = AssetsManager()