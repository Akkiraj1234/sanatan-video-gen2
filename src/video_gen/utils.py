from __future__ import annotations
from typing import Literal, Union, Tuple, Dict, List
from pathlib import Path
import os

def project_root() -> Path:
    """
    Returns the absolute path of the project root directory.
    """
    return Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

