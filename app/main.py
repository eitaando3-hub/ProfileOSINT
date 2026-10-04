"""Main entry point and initialization with splash screen."""
import logging
import sys
import threading
import tkinter as tk
from pathlib import Path

from app.config.logger import setup_logging
from app.config.settings import global_settings
from app.ui.main_window import MainWindow
from app.utils.progress import get_progress_tracker

logger = logging.getLogger(__name__)


def create_splash_screen():
    """Create a splash screen with progress display."""
    splash = tk.Tk()
    splash.title("ProfileOSINT")
    splash.geometry("400x200")
    splash.resizable(False, False)
    splash.attributes("-topmost", True)

    # Center window
    splash.update_idletasks()
    w = splash.winfo_width()
    h = splash.winfo_height()
    x = (splash.winfo_screenwidth() // 2) - (w // 2)
    y = (splash.winfo_screenheight() // 2) - (h // 2)
    splash.geometry(f"+{x}+{y}")

    # Title
    title = tk.Label(splash, text="ProfileOSINT", font=("Arial", 24, "bold"))
    title.pack(pady=20)

    # Version
    version = tk.Label(splash, text=f"v{global_settings.version}", font=("Arial", 10))
    version.pack()

    # Progress bar
    progress_var = tk.DoubleVar(value=0)
    progress_bar = tk.Canvas(splash, height=20, bg="white", highlightthickness=1)
    progress_bar.pack(pady=20, padx=20, fill="x")

    # Status label
    status_var = tk.StringVar(value="初期化中...")
    status = tk.Label(splash, textvariable=status_var, font=("Arial", 10))
    status.pack()

    def update_progress(percent, message):
        """Update progress bar and status."""
        progress_var.set(percent)
        status_var.set(message or "処理中...")
        # Draw progress bar
        progress_bar.delete("all")
        w = progress_bar.winfo_width()
        h = progress_bar.winfo_height()
        filled = (w * percent) / 100
        progress_bar.create_rectangle(0, 0, filled, h, fill="#4CAF50", outline="")
        splash.update()

    return splash, update_progress


def main():
    """Initialize and run the application."""
    # Setup logging
    setup_logging(str(global_settings.log_dir), logging.INFO)
    logger.info(f"Starting {global_settings.app_name} v{global_settings.version}")
    logger.info(f"Data directory: {global_settings.data_dir}")

    try:
        # Create splash screen
        splash, update_progress = create_splash_screen()
        progress = get_progress_tracker()
        progress.set_callback(update_progress)

        # Simulate initialization steps
        progress.start(4)
        progress.step("ロギング初期化...")
        splash.update()

        progress.step("設定ロード中...")
        splash.update()

        progress.step("UI構築中...")
        splash.update()

        # Create root window
        root = tk.Tk()
        app = MainWindow(root)
        logger.info("Main window created successfully")

        progress.finish()
        splash.after(500, splash.destroy)  # Hide splash after 500ms
        splash.update()

        # Run event loop
        root.mainloop()
        logger.info("Application closed")

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
