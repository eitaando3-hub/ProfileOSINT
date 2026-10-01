"""Application entry point and initialization."""
import logging
import sys
import tkinter as tk
from pathlib import Path

from app.config.logger import setup_logging
from app.config.settings import global_settings
from app.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def main():
    """Initialize and run the application."""
    # Setup logging
    setup_logging(str(global_settings.log_dir), logging.INFO)
    logger.info(f"Starting {global_settings.app_name} v{global_settings.version}")
    logger.info(f"Data directory: {global_settings.data_dir}")

    try:
        # Create root window
        root = tk.Tk()
        app = MainWindow(root)
        logger.info("Main window created successfully")

        # Run event loop
        root.mainloop()
        logger.info("Application closed")

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
