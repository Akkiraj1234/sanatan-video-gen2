# ----------------------------------------------------------------------------------
# Custom Exception Handling for video_gen
# ----------------------------------------------------------------------------------
# This file defines custom exception classes used in the `video_gen` project.
# Instead of using generic exceptions, we define specific errors to make debugging easier.
#
# Usage Example:
# --------------
# try:
#     raise ConfigNotFoundError()
# except ConfigNotFoundError as e:
#     print(f"Error: {e}")
#
# Available Errors:
# -----------------
# - VideoGenError (Base class for all custom errors)
# - ConfigNotFoundError (Raised when no configuration file is found)
# - InvalidConfigError (Raised when the config file has invalid data)
# - MissingDependencyError (Raised when a required package is missing)
# - AssetNotFoundError (Raised when an important file is missing)
# - TTSModelError (Raised for Text-to-Speech (TTS) issues)
# - VideoProcessingError (Raised when video generation fails)
# ----------------------------------------------------------------------------------

class VideoGenError(Exception):
    """Base exception class for all video_gen errors."""
    pass

class ConfigNotFoundError(VideoGenError):
    """Raised when no configuration file is found in the specified paths."""
    def __init__(self, message="Configuration file not found in the given paths."):
        super().__init__(message)

class InvalidConfigError(VideoGenError):
    """Raised when a configuration file is found but contains invalid data."""
    def __init__(self, message="Configuration file contains invalid data."):
        super().__init__(message)

class MissingDependencyError(VideoGenError):
    """Raised when a required dependency is missing."""
    def __init__(self, dependency_name):
        message = f"Missing required dependency: {dependency_name}. Please install it."
        super().__init__(message)

class AssetNotFoundError(VideoGenError):
    """Raised when a required asset (e.g., model file) is missing."""
    def __init__(self, asset_path):
        message = f"Required asset not found: {asset_path}. Please check the asset directory."
        super().__init__(message)

class TTSModelError(VideoGenError):
    """Raised when there is an issue with the Text-to-Speech (TTS) model."""
    def __init__(self, message="Error occurred while processing the TTS model."):
        super().__init__(message)

class VideoProcessingError(VideoGenError):
    """Raised when an error occurs during video processing."""
    def __init__(self, message="An error occurred while processing the video."):
        super().__init__(message)

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass
