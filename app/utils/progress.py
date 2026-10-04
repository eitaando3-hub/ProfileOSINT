"""Search progress notification service."""
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class SearchProgressTracker:
    """Tracks and reports progress during search operations."""

    def __init__(self):
        self.current_step = 0
        self.total_steps = 0
        self.callback: Optional[Callable] = None
        self.message = ""

    def set_callback(self, callback: Callable[[int, str], None]) -> None:
        """Set callback function for progress updates.
        
        Args:
            callback: Function(progress_percent, message)
        """
        self.callback = callback

    def start(self, total: int) -> None:
        """Start tracking progress."""
        self.total_steps = max(1, total)
        self.current_step = 0
        self._update()

    def step(self, message: str = "") -> None:
        """Advance progress by one step."""
        self.current_step += 1
        self.message = message
        self._update()

    def set_progress(self, current: int, total: int, message: str = "") -> None:
        """Set exact progress."""
        self.current_step = current
        self.total_steps = max(1, total)
        self.message = message
        self._update()

    def finish(self) -> None:
        """Mark as complete."""
        self.current_step = self.total_steps
        self.message = "完了"
        self._update()

    def _update(self) -> None:
        """Internal update to fire callback."""
        if self.total_steps <= 0:
            return
        percent = int((self.current_step / self.total_steps) * 100)
        if self.callback:
            self.callback(min(100, percent), self.message)
        logger.debug(f"Progress: {percent}% - {self.message}")


# Global progress tracker
global_progress = SearchProgressTracker()


def get_progress_tracker() -> SearchProgressTracker:
    return global_progress
