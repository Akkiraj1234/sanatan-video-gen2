from video_gen.utils import sstrip, write_json, Path, AttrDict
import json


# Default settings
_default_settings = {
    "video_engine": "gen1",
    "debug": False,
    "tts_model": "ElevenLabsModel2",
    "timestamp_model": "basic1",
}

class Setting:
    """
    A singleton class that manages application settings.

    - Ensures only a single instance exists (singleton pattern).
    - Prevents modification after initialization.
    - Allows settings to be accessed as attributes directly.
    """

    _instance = None
    _initialized = False
    

    
    def __new__(cls, settings_dict=None):  # Accept settings_dict in __new__
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            
            # Initialize settings here
            if settings_dict is not None:
                cls._instance._initialize(settings_dict)  # Manually initialize
        
        return cls._instance

    def _initialize(self, settings_dict = None):
        """ Initializes settings if not already initialized. """
        if not self._initialized:
            for key, value in settings_dict.items():
                object.__setattr__(self, sstrip(key), value)
            self._initialized = True 

    def __setattr__(self, key, value):
        """ Prevents modification after initialization. """
        if self._initialized:
            raise AttributeError("Settings are immutable after initialization")
        super().__setattr__(key, value)
    #-------------------------------------------------
    def __init__(self, settings_dict = None):
        """
        Initializes settings if not already initialized.
        """
        if not self._initialized:
            for key, value in settings_dict.items():
                object.__setattr__(self, sstrip(key), value)
                
            self._initialized = True 
        
    def __setattr__(self, key, value):
        """
        Prevents modification of settings after initialization.
        """
        if self._initialized:
            raise AttributeError("Settings are immutable after initialization")

        super().__setattr__(key, value)


def update_missing_key(json_path:Path, loaded_settings:dict) -> None:
    """ 
    If missing keys are found, they are written back to the JSON file.
    """
    missing_keys = {k: v for k, v in _default_settings.items() if k not in loaded_settings}
    if not missing_keys:
        return
    
    updated_settings = {**loaded_settings, **_default_settings}
    write_json(json_path, updated_settings)
    

def setting_init(root_path: Path):
    """
    Loads settings from a JSON file, falling back to defaults if missing.
    """
    json_path = root_path / "settings.json"
    loaded_settings = {}
    extra_info = {
        "SETTING_LOG_PATH": json_path
    }

    if json_path.exists():
        try:
            with open(json_path, "r") as f:
                loaded_settings = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {json_path} is corrupted. Using default settings and writing new JSON file.")

    # Merge loaded settings with defaults (defaults take precedence)
    final_settings = _default_settings.copy()
    final_settings.update({**loaded_settings, **extra_info})
    update_missing_key(json_path, loaded_settings)
    
    return Setting(final_settings)



setting = AttrDict(
    {
        "VIDEO_ENGION": "gen1",
        "DEBUG": False,
        "TTS_MODLE": "ElevenLabsModel1", #"GTTSModel", #,ElevenLabsModel1
        "TIMESTAMPS_MODLE": "basic1",
        "TTS_Lang": "hi",
        "TTS_ELVENLABS_VOICE_ID": "y6Ao4Y93UrnTbmzdVlFc", #"FmBhnvP58BK0vz65OOj7", #"Sm1seazb4gs7RSlUVw7c",
        "TTS_ELEVNLABS_MODEL_ID": "eleven_turbo_v2_5",
        "ASSETS_PATH": Path("/home/akkiraj/Desktop/video-gen/assets"),
        "temp_path": Path("/home/akkiraj/Desktop/video-gen/temp"),
        "TEMP_PATH": Path("/home/akkiraj/Desktop/video-gen/temp"),
        "SETTING_LOG_PATH": Path('/home/akkiraj/Desktop/video-gen/error.log')
    }
)