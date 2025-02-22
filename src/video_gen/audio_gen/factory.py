from video_gen.utils import setting
from video_gen.audio_gen.base import TTS
import importlib
import pkgutil
import inspect
import os

# Store cache
MODEL_CACHE = {}

def discover_tts_models():
    """
    Scans the `video_gen.audio_gen` package and caches model locations.
    This function is called only once, when the cache is empty.
    """
    
    package_name = "video_gen.audio_gen"
    package = importlib.import_module(package_name)
    package_dir = os.path.dirname(package.__file__)

    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        if module_name.startswith("_") or "_gen" not in module_name:
            continue
        
        module = importlib.import_module(f"{package_name}.{module_name}")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, TTS) and obj is not TTS:
                MODEL_CACHE[name] = f"{package_name}.{module_name}"


def get_TTSModel(model_name:str|None = None) -> TTS:
    """
    Loads the requested TTS model class (not instance) with caching.
    """
    if model_name is None:
        model_name = setting.tts_model
    
    if not MODEL_CACHE:
        discover_tts_models()

    if model_name in MODEL_CACHE:
        module_name = MODEL_CACHE[model_name]
        module = importlib.import_module(module_name)
        model_class = getattr(module, model_name)
        return model_class

    raise ValueError(f"TTS model '{model_name}' not found.")
