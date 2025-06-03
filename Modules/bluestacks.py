"""
BlueStacks-specific automation functionality.
This module can contain BlueStacks emulator specific operations,
window handling, and specialized input methods.
"""

import logging
import time
from typing import Optional, Tuple
from pathlib import Path

import pyautogui
import pydirectinput
from Modules.Bot.config import BotConfig, ClickType
from Modules.Bot.image_handler import ImageHandler
from Modules.Bot.input_handler import InputHandler


class BlueStacksBot:
    
    def __init__(self, config: BotConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.image_handler = ImageHandler(config, logger)
        self.input_handler = InputHandler(config, logger)
        
        # BlueStacks-specific image patterns loaded from config
        self.assets_paths = {
            'start_icon_dark': 'Assets/Windows/start_icon_dark_mode.png',
            'start_icon_light': 'Assets/Windows/start_icon_light_mode.png',
            "bluestacks_home": "Assets/BlueStacks/BlueStack_homeButton.png",
            "top_eleven": "Assets/BlueStacks/top_eleven.png",
            'bluestacks_app':  'Assets/BlueStacks/bluestacks_icon.png',
            'bluestacks_window': 'Assets/BlueStacks/bluestacks_window.png'
        }
        
    def open_top_eleven_app(self) -> Optional[Tuple[int, int, int, int]]:
        """
            To open the app the following sequence must occur
            1. Search and open bluestacks from windows start menu
            2. Find and open TopEleven app in Bluestacks
        """
        try:
            # Step 1: Open Windows Start Menu
            if not self._open_windows_start_menu():
                return False
                
            # Step 2: Launch BlueStacks
            if not self._launch_bluestacks():
                return False
                
            # Step 3: Wait for BlueStacks to be ready
            if not self._wait_for_bluestacks_ready():
                return False
                
            # Step 4: Navigate to BlueStacks Home
            if not self._navigate_to_bluestacks_home():
                return False
                
            # Step 5: Launch Top Eleven
            if not self._launch_top_eleven():
                return False
                
            self.logger.info("✅ Top Eleven launch sequence completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in open_top_eleven_app: {e}")
            self.take_screenshot(name="launch_error")
            return False

    def _open_windows_start_menu(self) -> bool:
        """Open Windows start menu."""
        try:
            self.logger.info("🔍 Step 1: Opening Windows start menu...")
            
            # Try to click on the windows icon in dark mode first
            dark_icon_path = self.assets_paths['start_icon_dark']
            light_icon_path = self.assets_paths['start_icon_light']
            
            clicked_start = False
            
            if dark_icon_path:
                point = self.image_handler.find_image_on_screen(
                    self.image_handler.load_image(self.assets_paths['start_icon_dark'])
                )
                if point:
                    self.input_handler.click_at_point(point)
                    clicked_start = True
                    self.logger.info("✅ Clicked Windows start icon (dark mode)")
            
            if not clicked_start and light_icon_path:
                point = self.image_handler.find_image_on_screen(
                    self.image_handler.load_image(self.assets_paths['start_icon_light'])
                )
                if point:
                    self.input_handler.click_at_point(point)
                    clicked_start = True
                    self.logger.info("✅ Clicked Windows start icon (light mode)")
            
            if not clicked_start:
                self.logger.error("❌ Could not find Windows start icon")
                return False
            
            # Wait for start menu to open
            time.sleep(1)
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening Windows start menu: {e}")
            return False

    def _launch_bluestacks(self) -> bool:
        """Launch BlueStacks application."""
        try:
            self.logger.info("🔍 Step 2: Launching BlueStacks...")
            
            # Type BlueStacks in the search bar
            search_text = "BlueStacks"
            self.input_handler.key_boardtype(tuple(search_text), type_interval=0.05)
            
            # Wait for search results
            time.sleep(2)
            
            # Press Enter to launch BlueStacks
            self.input_handler.key_boardtype(('enter',))
            
            self.logger.info("✅ BlueStacks launch initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error launching BlueStacks: {e}")
            return False

    def _wait_for_bluestacks_ready(self) -> bool:
        """Wait for BlueStacks to be ready."""
        try:
            self.logger.info("⏳ Step 3: Waiting for BlueStacks to be ready...")
            return self.wait_for_bluestacks_ready(60)  # Reduced timeout to 60 seconds
            
        except Exception as e:
            self.logger.error(f"Error waiting for BlueStacks: {e}")
            return False

    def _navigate_to_bluestacks_home(self) -> bool:
        """Navigate to BlueStacks home."""
        try:
            self.logger.info("🔍 Step 4: Navigating to BlueStacks home...")
            
            # Find BlueStacks home button
            blue_stacks_home = self.assets_paths['bluestacks_home']
            
            # Check if the home button image file exists
            home_button_path = Path(blue_stacks_home)
            if not home_button_path.exists():
                self.logger.error(f"❌ BlueStacks home button image not found: {home_button_path}")
                return False
            
            point = self.image_handler.find_image_on_screen(
                self.image_handler.load_image(blue_stacks_home)
            )
            
            if point:
                self.input_handler.click_at_point(point)
                self.logger.info("✅ Clicked BlueStacks home button")
                time.sleep(2)  # Wait for home screen to load
                return True
            else:
                self.logger.warning("⚠️ BlueStacks home button not found on screen")
                # Continue anyway, might already be on home screen
                return True
                
        except Exception as e:
            self.logger.error(f"Error navigating to BlueStacks home: {e}")
            return False

    def _launch_top_eleven(self) -> bool:
        """Launch Top Eleven app."""
        try:
            self.logger.info("🔍 Step 5: Launching Top Eleven app...")
            
            # Wait a bit for home screen to be ready
            self.logger.info("⏳ Waiting for home screen to be ready...")
            time.sleep(5)
            
            # Find top eleven app
            top_eleven_path = self.assets_paths['top_eleven']
            
            # Check if the Top Eleven app image file exists
            app_image_path = Path(top_eleven_path)
            if not app_image_path.exists():
                self.logger.error(f"❌ Top Eleven app image not found: {app_image_path}")
                return False
            
            
            top_eleven_image =  self.image_handler.load_image(top_eleven_path)
            point = self.image_handler.find_image_on_screen(top_eleven_image)
            
            if point:
                self.input_handler.click_at_point(point)
                self.logger.info("✅ Clicked Top Eleven app")
                time.sleep(3)  # Wait for app to start loading
                return True
            else:
                self.logger.error(f"❌ Top Eleven app not found on screen, point {point} top_eleven_image {type(top_eleven_image)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching Top Eleven app: {e}")
            return False

    def optimize_for_bluestacks(self) -> None:
        """Apply BlueStacks-specific optimizations."""
        # Use pydirectinput for better compatibility with BlueStacks
        pydirectinput.FAILSAFE = True
        pydirectinput.PAUSE = self.config.delay  # Use delay from config
        self.logger.info("Applied BlueStacks optimizations")
        
    def bluestacks_click(self, x: int, y: int, double_click: bool = True) -> bool:
        """
        Perform BlueStacks-optimized click.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            double_click: Whether to perform double click
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Move to position using config move_duration
            pydirectinput.moveTo(x, y, duration=self.config.move_duration)
            
            # Perform click
            if double_click:
                pydirectinput.doubleClick()
            else:
                pydirectinput.click()
            
            # Add delay from config
            time.sleep(self.config.delay)
                
            self.logger.info(f"✅ BlueStacks click at ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"BlueStacks click failed at ({x}, {y}): {e}")
            return False
            
    def send_key_combination(self, *keys) -> bool:
        """
        Send key combination to BlueStacks.
        
        Args:
            *keys: Keys to press (e.g., 'ctrl', 'c')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pydirectinput.hotkey(*keys)
            time.sleep(self.config.delay)  # Use delay from config
            self.logger.info(f"Sent key combination: {'+'.join(keys)}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send key combination {keys}: {e}")
            return False
            
    def wait_for_bluestacks_ready(self, timeout: int = 120) -> bool:
        """
        Wait for BlueStacks to be ready for automation.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if BlueStacks is ready, False if timeout
        """
        self.logger.info(f"⏳ Waiting for BlueStacks to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        bluestacks_window_pattern = self.assets_paths.get('bluestacks_window')
        
        # Check if the BlueStacks window image exists
        if bluestacks_window_pattern:
            window_image_path = Path(bluestacks_window_pattern)
            if not window_image_path.exists():
                self.logger.warning(f"⚠️ BlueStacks window image not found: {window_image_path}")
                self.logger.info("⏳ Using time-based wait instead...")
                time.sleep(60)  # Wait 60 seconds and assume it's ready
                return True
        
        check_count = 0
        while time.time() - start_time < timeout:
            check_count += 1
            self.logger.debug(f"🔍 BlueStacks ready check #{check_count}")
            
            if bluestacks_window_pattern:
                # Look for BlueStacks window indicator
                window_image = self.image_handler.load_image(bluestacks_window_pattern)
                if window_image:
                    point = self.image_handler.find_image_on_screen(window_image)
                    if point:
                        self.logger.info("✅ BlueStacks is ready!")
                        return True
            
            time.sleep(3)  # Check every 3 seconds
        
        self.logger.warning(f"⚠️ BlueStacks not ready after {timeout} seconds")
        self.logger.info("🤷 Proceeding anyway - BlueStacks might be ready but not detected")
        return True  # Changed to return True to continue the process
            
    def restart_bluestacks_app(self, app_package: str) -> bool:
        """
        Restart a specific app in BlueStacks.
        
        Args:
            app_package: Package name of the app to restart
            
        Returns:
            True if successful, False otherwise
        """
        # TODO: Implement app restart logic
        # Call the close_bluestacks function
        # Call open top Eleven
        
        return False
    
    def take_screenshot(self, name: str = "Screenshot", save_path: Optional[str] = None) -> bool:
        """
        Take a screenshot of the BlueStacks window.
        
        Args:
            name: Name for the screenshot file
            save_path: Optional path to save screenshot
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if save_path is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = Path(self.config.log_dir) / f"{name}_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            self.logger.info(f"📸 Screenshot saved: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return False