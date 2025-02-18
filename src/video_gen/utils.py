from __future__ import annotation
from typing import Literal, Union, Tuple, Dict, List
import os

def project_root(self) -> str:
    """
    Returns the absolute path of the project root directory.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def log_file_path(self) -> str:
    """
    Returns the absolute path of the log file.
    """
    return os.path.join(self.project_root(), "app.log")

