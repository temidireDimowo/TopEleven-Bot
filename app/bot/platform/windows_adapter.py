"""Windows platform adapter — launches BlueStacks via Windows search."""

import time
import logging
from app.bot.platform.base import PlatformAdapter
from Modules.Bot.config import BotConfig


class WindowsAdapter(PlatformAdapter):

    def is_platform_supported(self) -> bool:
        import sys
        return sys.platform == "win32"

    def launch_app(self) -> bool:
        """Open Windows search → type 'top eleven' → press Enter → maximize."""
        try:
            import keyboard
            self.logger.info("Opening Windows search...")
            keyboard.press_and_release('win')
            time.sleep(2)

            import pyautogui
            for char in "top eleven":
                pyautogui.press(char) if len(char) == 1 else pyautogui.write(char)
                time.sleep(0.05)
            time.sleep(2)

            pyautogui.press('enter')
            time.sleep(5)

            keyboard.press_and_release('win+up')
            self.logger.info("BlueStacks launch initiated, fullscreen applied")
            return True

        except Exception as e:
            self.logger.error(f"Windows launch_app failed: {e}")
            return False

    def wait_for_ready(self, timeout: int = 120) -> bool:
        """Wait for BlueStacks window to appear, or fall back to timed wait."""
        from Modules.bluestacks import BlueStacksBot
        bot = BlueStacksBot(self.config, self.logger)
        result = bot.wait_for_bluestacks_ready(timeout)
        if not result:
            self.logger.warning("BlueStacks not detected — using 60s fallback wait")
            time.sleep(60)
        return True

    def maximize_window(self) -> bool:
        try:
            import keyboard
            keyboard.press_and_release('win+up')
            return True
        except Exception as e:
            self.logger.error(f"maximize_window: {e}")
            return False

    def press_escape(self) -> bool:
        try:
            import keyboard
            keyboard.press_and_release('esc')
            return True
        except Exception as e:
            self.logger.error(f"press_escape: {e}")
            return False
