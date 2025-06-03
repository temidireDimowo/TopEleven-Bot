"""
Logging configuration for the Game Automation Bot.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import BotConfig
import pyautogui


class BotLogger:
    """Handles logging configuration and setup for the bot."""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.logger: Optional[logging.Logger] = None
        
    def setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging configuration."""
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('GameAutomationBot')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            log_dir / f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for user-friendly output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(
            log_dir / "errors.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        
        return self.logger
        
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        if self.logger is None:
            return self.setup_logging()
        return self.logger
    
