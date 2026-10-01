"""Config package."""
from app.config.settings import global_settings
from app.config.logger import setup_logging

__all__ = ["global_settings", "setup_logging"]
