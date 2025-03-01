from video_gen.utils import (
    write_json,
    get_json_data,
    Path,
    AttrDict
)
from video_gen.error import ConfigError
from typing import List, Dict, Optional, Union, Any
from threading import Lock
import sys


# List of directories where configuration files may be located
_CONFIG_PATHS = [".", Path.home().joinpath(".video_gen")]

# Default configuration settings
DEFAULT_SETTINGS = {
    "VIDEO_ENGINE": "gen1",
    "DEBUG": False,  
    "TTS_MODEL": "GTTSModel", 
    "TIMESTAMPS_MODEL": "basic1", 
    "TTS_LANG": "hi",  
    "TTS_ELEVENLABS_VOICE_ID": "y6Ao4Y93UrnTbmzdVlFc",  
    "TTS_ELEVENLABS_MODEL_ID": "eleven_turbo_v2_5", 
    "ASSETS_PATH": str(Path.home() / "video-gen/assets"),  
    "TEMP_PATH": str(Path.home() / "video-gen/temp"),  
    "SETTING_LOG_PATH": str(Path.home() / "video-gen/error.log"), 
}

# the dict to store loaded info
_loaded_dict: Optional[AttrDict] = None
_config_path: Optional[Path] = None

def check_paths_exists(path_list: List[Union[str, Path]], file_name: str) -> Optional[Path]:
    """
    Checks if a file exists in any of the given directories.
    return path or none if cant find any
    
    Raises:
        ValueError: If a path is not a valid string or Path object.
    """
    for path in path_list:
        if not isinstance(path, (str, Path)):
            raise ValueError("Each path should be a string or Path object.")

        path = Path(path) 
        if (path / file_name).exists():
            print(f"Config file found at: {path / file_name}")
            return path / file_name
        
    print("No existing config file found.")
    return None


def create_path_FA(paths: List[Union[str, Path]], config_name: str, config_data: Dict[str, any]) -> Path:
    """
    Tries to create a configuration file in the given list of directories, starting with the first one.
    If the file is created successfully, returns the path. If any error occurs, moves to the next path.

    Args:
        paths (List[str]): List of directories to try creating the config file.
        config_name (str): Name of the configuration file to create.
        config_data (Dict): Data to be written to the configuration file.

    Returns:
        Path: The path where the configuration file was successfully created.

    Raises:
        ConfigError: If the configuration file cannot be created in any of the given directories.
    """
    config_error_list = []
    for path in paths:
        path = Path(path)
        config_file_path = path / config_name
        
        try: 
            if not path.parent.exists():    # If the parent directory exists, 
                continue                    # create the main folder if it does not exist.
            path.mkdir(parents=True, exist_ok=True)
            # Finally, write JSON to the config file path.
            write_json(config_file_path, config_data)
            print(f"Config file successfully created at: {config_file_path}")
            return config_file_path
        
        except Exception as e:
            config_error_list.append(f"Failed to create config at {str(config_file_path)}: {e}\n")
            continue
        
    raise ConfigError(f"Failed to create configuration file in any of the provided paths : \n{''.join(config_error_list)}")


def setting_init(
    paths_list: Optional[List[Union[str, Path]]] = None,
    create: bool = True,
    location_first_priority: str = '.'
) -> AttrDict:
    """
    Initializes and loads configuration settings from a file.
    
    If no configuration file is found, a new one is created based on the given priority rules.

    Args:
        paths_list (List, optional): 
            - Additional directories to check before default paths.
            - Defaults to CONFIG_PATHS if not provided.

        create (bool, optional): 
            - If True, creates a new config file if none exists.
            - The file is created at `location_first_priority`, 
              or the first path in `paths_list` if not set.
            - If no valid path is found, an error is raised.
            - Defaults to True.

        location_first_priority (str, optional): 
            - The preferred directory to create the config file if needed.
            - Defaults to the current directory (`"."`).

    Returns:
        AttrDict: A dictionary-like object containing configuration settings.
    """
    config_name = "config.json"
    path_list =  (paths_list if paths_list else []) + _CONFIG_PATHS
    config_path = check_paths_exists(path_list, config_name)
    
    if (not create) and config_path is None:
        raise ConfigError("Configuration file not found and creation is disabled.")
    
    elif create and config_path is None:
        print("No config file found. Attempting to create a new one.")
        config_path = create_path_FA(
            paths = [location_first_priority] + path_list,
            config_name = config_name, 
            config_data = DEFAULT_SETTINGS
        )
    
    # saving the info..
    global _config_path, _loaded_dict
    _config_path = config_path
    _loaded_dict = AttrDict(get_json_data(config_path))
    print(f"Config settings loaded from: {_config_path}")
    return _loaded_dict
    

def setting_reload() -> None:
    """
    Reloads the settings from the stored configuration file.
    
    This updates the singleton Setting instance.
    """
    if _config_path is None:
        raise ConfigError("Settings not initialized. Call setting_init() first.")
    
    global _loaded_dict
    _loaded_dict = AttrDict(get_json_data(_config_path))
    print("Settings reloaded successfully.")


def setting_update(new_data: Dict[str, Any]) -> None:
    """
    Updates the configuration file with new data and then reloads settings.
    
    Note: This is the only external method that modifies configuration data.
    """
    global _loaded_dict   #line 166
    
    if _config_path is None:
        raise ConfigError("Settings not initialized. Call setting_init() first.")
    
    copyied_data = dict(_loaded_dict)  
    copyied_data.update(new_data) 
    
    write_json(_config_path, copyied_data)
    _loaded_dict = AttrDict(copyied_data)
    print(f"Settings updated: {copyied_data}")


class Setting:
    """
    A singleton class that holds configuration settings as a read-only property.
    
    The settings data (and meta-information such as the config file path) can only be changed
    via the external functions (setting_init, setting_reload, setting_update).
    
    Direct modification (by assignment or deletion) is not permitted.
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Setting, cls).__new__(cls)
        return cls._instance

    def __setattr__(self, name, value):
        """
        Allow assignments to attributes that begin with an underscore.
        """
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            
        else:
            raise AttributeError(
                "Direct modification of settings is not allowed. "
                "Use setting_update() to update configuration."
            )

    def __delattr__(self, name):
        """
        not allowed to delete.
        """
        raise AttributeError("Deletion of settings is not allowed.")

    def __getattr__(self, name):
        """
        This method is called only if the attribute wasn't found the usual ways.
        """
        if _loaded_dict is None:
            raise AttributeError("Settings not initialized. Call setting_init() first.")
        
        return _loaded_dict.get(name, None)

    @property
    def setting_file_path(self):
        if _config_path is None:
            raise ConfigError("Settings not initialized. Call setting_init() first.")
        
        return _config_path

    def __dir__(self):
        if _loaded_dict is None:
            return []
        
        return list(_loaded_dict.keys())

    def __iter__(self):
        if _loaded_dict is None:
            raise ConfigError("Settings not initialized. Call setting_init() first.")
        
        return iter(_loaded_dict.items())

setting = Setting()


# functions to only be accessed
__all__ = ['setting_init', 'setting_reload', 'setting_update', 'DEFAULT_SETTINGS', 'setting']

# # It's to help encapsulate some attributes that shouldn't be accessed directly
# class RestrictedModule:
#     def __init__(self, module):
#         self._module = module

#     def __getattr__(self, name):
#         if name not in self._module.__all__:
#             raise AttributeError(f"Access to '{name}' is restricted!")

#         return getattr(self._module, name)

# sys.modules[__name__] = RestrictedModule(sys.modules[__name__])

