"""Mac platform adapter — launches BlueStacks via Spotlight search."""

import subprocess
import time
import logging
from app.bot.platform.base import PlatformAdapter
from Modules.Bot.config import BotConfig


class MacAdapter(PlatformAdapter):

    def is_platform_supported(self) -> bool:
        import sys
        return sys.platform == "darwin"

    def launch_app(self) -> bool:
        """Open Spotlight → type 'BlueStacks' → press Enter."""
        try:
            import pyautogui
            self.logger.info("Opening Spotlight search (Cmd+Space)...")
            pyautogui.hotkey('command', 'space')
            time.sleep(1)
            pyautogui.write("BlueStacks", interval=0.05)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(8)
            self.logger.info("BlueStacks launch initiated via Spotlight")
            return True
        except Exception as e:
            self.logger.error(f"Mac launch_app failed: {e}")
            return False

    def wait_for_ready(self, timeout: int = 120) -> bool:
        self.logger.info(f"Waiting {timeout}s for BlueStacks (Mac fallback)...")
        time.sleep(min(timeout, 60))
        return True

    def maximize_window(self) -> bool:
        try:
            import pyautogui
            pyautogui.hotkey('command', 'control', 'f')
            return True
        except Exception as e:
            self.logger.error(f"maximize_window: {e}")
            return False

    def press_escape(self) -> bool:
        try:
            import pyautogui
            pyautogui.press('escape')
            return True
        except Exception as e:
            self.logger.error(f"press_escape: {e}")
            return False
