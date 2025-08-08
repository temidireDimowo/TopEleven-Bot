"""
Input handling for mouse clicks and keyboard events.
"""

import logging
import time
from typing import Callable

import pyautogui
import pydirectinput
import pynput
import pyscreeze

from .config import BotConfig, ClickType


class InputHandler:
    """Handles mouse clicks and keyboard input for the bot."""
    
    def __init__(self, config: BotConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.keyboard_listener = None
        
        # Setup pyautogui settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

    def click_at_point(self, point: pyscreeze.Point, click_type: ClickType = ClickType.DEFAULT) -> bool:
        """Perform click at specified point with error handling."""
        try:
            # Move to position
            pyautogui.moveTo(
                x=point.x, 
                y=point.y, 
                duration=self.config.move_duration
            )
            
            # Perform click based on type
            if click_type == ClickType.BLUESTACKS:
                pydirectinput.doubleClick()
            else:
                # pyautogui.click()
                pyautogui.doubleClick()
                
            self.logger.info(f" Clicked at ({point.x}, {point.y}) using {click_type.value} method")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click at ({point.x}, {point.y}): {e}")
            return False

    def setup_key_handler(self, toggle_callback: Callable, shutdown_callback: Callable) -> None:
        """Setup keyboard event handlers."""
        def on_key_press(key) -> None:
            try:
                if key == pynput.keyboard.Key.f2:
                    toggle_callback()
                elif key == pynput.keyboard.Key.f3:
                    self.logger.info("F3 pressed - shutting down bot")
                    shutdown_callback()
                    
            except Exception as e:
                self.logger.error(f"Error in key handler: {e}")

        # Start keyboard listener in daemon mode
        self.keyboard_listener = pynput.keyboard.Listener(on_key_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        self.logger.debug("Keyboard listener started")
        
    def stop_key_handler(self) -> None:
        """Stop the keyboard listener."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.logger.debug("Keyboard listener stopped")
            
    def key_boardtype(self, characters: tuple, type_interval: float = 0.05) -> bool:
        """
        Type a sequence of characters with configurable interval.
        
        Args:
            characters: Tuple of characters/strings to type
            type_interval: Delay between each character (seconds)
            
        Returns:
            True if typing successful, False otherwise
        """
        try:
            self.logger.debug(f"Typing characters: {characters}")
            
            for char in characters:
                if isinstance(char, str):
                    if len(char) == 1:
                        # Single character
                        pyautogui.press(char)
                    else:
                        # Multi-character string or special key
                        if char.lower() in ['enter', 'tab', 'space', 'backspace', 'delete', 
                                          'shift', 'ctrl', 'alt', 'escape', 'home', 'end',
                                          'pageup', 'pagedown', 'up', 'down', 'left', 'right']:
                            # Special key
                            pyautogui.press(char.lower())
                        else:
                            # Multi-character string - type each character
                            pyautogui.write(char, interval=type_interval)
                else:
                    # Convert to string and type
                    pyautogui.write(str(char), interval=type_interval)
                    
                # Wait between characters/strings
                if type_interval > 0:
                    time.sleep(type_interval)
                    
            self.logger.info(f" Successfully typed {len(characters)} character(s)/string(s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to type characters {characters}: {e}")
            return False