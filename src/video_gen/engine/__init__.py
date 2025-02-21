# how this code going to work
# each engion here should take input as 
# TAKE -->  List[Dict] 
# where video info and containg dict added into list
# and the engine should return 
#
# RETURN --> List|Tuple[Path, int, str] 
#  - where the path inside list is video path that its created as final output
#  - and int is status code weather code susessfull or failed
#  - and last should be message reagrading failure or tex and audio
#
# NOTE: 
# - it should handle error by himsef the code
# - it should not raise any error
# - it should return the status code and message
# - it should return the path of video file
# - it should not return any other thing
# - it should not take any insialization at start time.

# from .base import BaseEngine
from video_gen.engine.base import BaseEngine
from typing import Type
import importlib

def get_engine(name: str) -> Type[BaseEngine]:
    """
    Factory function to get the appropriate engine class based on the name.
    """
    try:
        module = importlib.import_module(f"video_gen.engine.{name}_engine")
        engine_class = getattr(module, f"{name.capitalize()}Engine")
        return engine_class
    
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Unknown engine name: {name}") from e

__all__ = ['get_engine', 'BaseEngine']