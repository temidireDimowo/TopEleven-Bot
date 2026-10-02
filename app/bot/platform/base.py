"""Platform adapter abstract base class."""

import logging
import sys
from abc import ABC, abstractmethod
from Modules.Bot.config import BotConfig


class PlatformAdapter(ABC):

    def __init__(self, config: BotConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger

    @abstractmethod
    def launch_app(self) -> bool: ...

    @abstractmethod
    def maximize_window(self) -> bool: ...

    @abstractmethod
    def press_escape(self) -> bool: ...

    @abstractmethod
    def is_platform_supported(self) -> bool: ...

    @classmethod
    def for_current_platform(cls, config: BotConfig, logger: logging.Logger) -> "PlatformAdapter":
        if sys.platform == "win32":
            from app.bot.platform.windows_adapter import WindowsAdapter
            return WindowsAdapter(config, logger)
        elif sys.platform == "darwin":
            from app.bot.platform.mac_adapter import MacAdapter
            return MacAdapter(config, logger)
        raise RuntimeError(f"Unsupported platform: {sys.platform}")
