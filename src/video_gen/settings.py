from video_gen.utils import (
    sstrip, 
    write_json,
    Path,
    AttrDict
)
from video_gen.error import (
    VideoGenError,
    ConfigNotFoundError
)
import json

# ----------------------------------------------------------------------------------
# Configuration Management for video_gen
# ----------------------------------------------------------------------------------
# This file is responsible for loading the configuration settings from a file.
# Once loaded, we can access the `setting` instance to retrieve valid configuration values.
#
# How to Initialize the Setting Instance:
# --------------------------------------
# To initialize settings, we need to call `setting_init()`, which sets up the configuration.
# It takes the following arguments:
# 
# 1. `create` (bool) [Default: True]  
#    - If `True`, a new config file will be created if none is found.
#
# 2. `create_default_path` (str) [Default: Home Directory]  
#    - Specifies a custom path for the default configuration file.
#
# 3. `add_new_path` (bool) [Default: False]  
#    - If `True`, a new path will be added to the configuration path list.
#    - The newly added path will be checked first before existing paths.
#
# Default Configuration Paths:
# ----------------------------
# - Current Directory (`"."`)
# - Home Directory (`~/.video_gen`)
#
# How to Use:
# -----------
# - Call `setting.DEBUG` (bool) to check if debugging is enabled.
# - Call `setting.VIDEO_ENGINE` to get the selected video engine.
# ----------------------------------------------------------------------------------



# List of directories where configuration files may be located
CONFIG_PATHS = [".", Path.home().joinpath(".video_gen")]

# Default configuration settings
DEFAULT_SETTINGS = {
    "VIDEO_ENGINE": "gen1",
    "DEBUG": False,  # Whether debugging is enabled
    "TTS_MODEL": "GTTSModel",  # Alternative: "ElevenLabsModel1"
    "TIMESTAMPS_MODEL": "basic1",  # Model used for generating timestamps
    "TTS_LANG": "hi",  # Default language for TTS
    "TTS_ELEVENLABS_VOICE_ID": "y6Ao4Y93UrnTbmzdVlFc",  # Voice ID for ElevenLabs TTS
    "TTS_ELEVENLABS_MODEL_ID": "eleven_turbo_v2_5",  # Model ID for ElevenLabs TTS
    "ASSETS_PATH": str(Path.home() / "video-gen/assets"),  # Path for storing assets
    "TEMP_PATH": str(Path.home() / "video-gen/temp"),  # Temporary storage directory
    "SETTING_LOG_PATH": str(Path.home() / "video-gen/error.log"),  # Error log file
}

class Setting:
    """Singleton class for managing application settings.
    
    This ensures that only one instance of the settings exists at a time.
    """

    _instance = None  # Singleton instance

    def __new__(cls, paths=None):
        """Ensures only one instance of the settings class exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(paths or CONFIG_PATHS)
        return cls._instance 

    def _initialize(self, paths) -> None:
        """
        Initializes the settings instance.

        Args:
            paths (list): List of directories to search for a configuration file.
        """
        self.paths = paths
        self.config = self.load_config()

    def load_config(self):
        """
        Loads configuration from the first available file in the provided paths.

        Returns:
            dict: Configuration settings.

        Raises:
            ConfigNotFoundError: If no valid config file is found.
        """
        # Future: Load from config files in self.paths
        return DEFAULT_SETTINGS


# ----------------------------------------------------------------------------------
# Initializing Settings
# ----------------------------------------------------------------------------------
# We create a singleton instance of the settings class.
# The settings instance is stored in `_Setting`, and an `AttrDict` wrapper is used
# to allow easy attribute-style access (e.g., setting.DEBUG instead of setting["DEBUG"]).
# ----------------------------------------------------------------------------------

# Initialize the singleton settings instance
_Setting = Setting()
setting = AttrDict(_Setting.config)  # Enables dot notation for accessing settings
