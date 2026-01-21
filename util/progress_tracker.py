import time

from discord import Message


class ProgressTracker:
    """
    A utility class for displaying progress updates during long-running operations.
    Provides rate-limited message updates with a mobile-friendly progress bar.
    
    Last docstring edit: -FoxyHunter V4.5.0
    Last class edit: -FoxyHunter V4.5.0
    """
    
    def __init__(self, min_update_interval: float = 3.0):
        """
        Initialize the progress tracker.
        
        :param min_update_interval: Minimum seconds between message edits (rate limiting)
        """
        self._message: Message | None = None
        self._min_update_interval = min_update_interval
        self._last_update_time = 0.0
        self._status_text: str = ""
        self._progress_percent: float = 0.0
        self._force_next_update = False
    
    def set_message(self, message: Message):
        """Set the message to edit for progress updates."""
        self._message = message
    
    def _build_progress_bar(self, percent: float, width: int = 20) -> str:
        """
        Build a mobile-friendly progress bar.
        
        :param percent: Progress percentage (0-100)
        :param width: Width of the progress bar in characters
        :return: Progress bar string
        """
        percent = max(0, min(100, percent))
        filled = int(width * percent / 100)
        empty = width - filled
        bar = "▓" * filled + "░" * empty
        return f"{bar} {percent:.0f}%"
    
    def _format_message(self) -> str:
        """Format the progress message with status text and progress bar."""
        lines = [self._build_progress_bar(self._progress_percent)]
        if self._status_text:
            lines.append(self._status_text)
        content = "\n".join(lines)
        return f"```\n{content}\n```"
    
    def update(self, status: str = None, progress: float = None, force: bool = False):
        """
        Update the status text and/or progress percentage.
        Use newlines in status for multiple lines.
        Changes are queued and sent on next send_update() call.
        
        :param status: Status text (use newlines for multiple lines)
        :param progress: Progress percentage (0-100)
        :param force: Force the next update regardless of rate limiting
        """
        if status is not None:
            self._status_text = status
        if progress is not None:
            self._progress_percent = progress
        if force:
            self._force_next_update = True
    
    async def send_update(self) -> bool:
        """
        Send a progress update if enough time has passed since the last update.
        
        :return: True if update was sent, False if skipped due to rate limiting
        """
        if self._message is None:
            return False
        
        current_time = time.time()
        elapsed = current_time - self._last_update_time
        
        if not self._force_next_update and elapsed < self._min_update_interval:
            return False
        
        try:
            await self._message.edit(content=self._format_message())
            self._last_update_time = current_time
            self._force_next_update = False
            return True
        except Exception:
            # Message edit failed, continue without crashing
            return False
    
    async def force_update(self):
        """Force an immediate update regardless of rate limiting."""
        self._force_next_update = True
        await self.send_update()
    
    async def complete(self, final_message: str = None):
        """
        Mark the operation as complete with an optional final message.
        
        :param final_message: Optional message to display on completion
        """
        if final_message:
            self._status_text = final_message
        self._progress_percent = 100.0
        await self.force_update()
