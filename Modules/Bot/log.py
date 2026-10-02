"""
Logging configuration for the Game Automation Bot.
"""

import logging
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import BotConfig


class UILogHandler(logging.Handler):
    """Routes log records to the UI event queue as structured events."""

    def __init__(self, event_queue: queue.Queue):
        super().__init__()
        self._eq = event_queue
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record: logging.LogRecord):
        level = record.levelname.lower()
        if level in ('critical', 'error'):
            level = 'error'
        elif level == 'warning':
            level = 'warning'
        elif level == 'debug':
            level = 'info'
        try:
            self._eq.put_nowait({
                'type': 'log',
                'level': level,
                'message': self.format(record),
            })
        except queue.Full:
            pass


class BotLogger:
    """Handles logging configuration and setup for the bot."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.logger: Optional[logging.Logger] = None

    def setup_logging(self) -> logging.Logger:
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('TopElevenBot')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        detailed_fmt = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_fmt = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(message)s',
            datefmt='%H:%M:%S'
        )

        file_handler = logging.FileHandler(
            log_dir / f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_fmt)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_fmt)

        error_handler = logging.FileHandler(
            log_dir / "errors.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_fmt)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)

        return self.logger

    def add_ui_handler(self, event_queue: queue.Queue) -> None:
        """Attach a UILogHandler so log messages stream to the UI."""
        if self.logger:
            handler = UILogHandler(event_queue)
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        if self.logger is None:
            return self.setup_logging()
        return self.logger
