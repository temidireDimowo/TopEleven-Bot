"""
Image handling and screen detection for the Game Automation Bot.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import time
import pyautogui
import pyscreeze
import PIL.Image

from .config import BotConfig


class ImageHandler:
    """Handles image loading, caching, and screen detection."""
    
    def __init__(self, config: BotConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.cache: Dict[str, PIL.Image.Image] = {}
        
    def load_image(self, path: str) -> Optional[PIL.Image.Image]:
        """Load and cache image files."""
        try:
            # if path in self.cache:
            #     return self.cache[path]
            # if path
            # full_path = Path(self.config.images_dir) / path
            # if not full_path.exists():
            #     self.logger.error(f"Image file not found: {full_path}")
            #     return None
                
            # image = PIL.Image.open(full_path)

            image = PIL.Image.open(path)
            self.cache[path] = image
            self.logger.debug(f"Loaded and cached image: {path}")
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to load image {path}: {e}")
            return None

    def find_image_on_screen(self, image: PIL.Image.Image) -> Optional[pyscreeze.Point]:
        """Find image on screen with error handling."""
        try:
            result = pyautogui.locateOnScreen(
                image, 
                grayscale=True, 
                confidence=self.config.confidence
            )
            
            if result is None:
                return None
                
            center_point = pyautogui.center(result)
            self.logger.debug(f"Image found at coordinates: ({center_point.x}, {center_point.y})")
            return center_point
            
        except pyautogui.ImageNotFoundException:
            return None
        except Exception as e:
            self.logger.error(f"Error during image search: {e}")
            return None
            
    def clear_cache(self) -> None:
        """Clear the image cache."""
        self.cache.clear()
        self.logger.debug("Image cache cleared")

    def wait_for_image(self, image_path, timeout: int = 60) -> bool:
        """
        Wait for Image to be ready for automation.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if Image is ready, False if timeout
        """
        self.logger.info("Waiting for Image to be ready...")
        
        start_time = time.time()
        self.image_path = image_path
        
        check_count = 0
        while time.time() - start_time < timeout:
            check_count += 1
            self.logger.debug(f"🔍 Image at {image_path} ready check #{check_count}")
        
            # Look for Image in window
            window_image = self.load_image(self.image_path)
            if window_image:
                point = self.find_image_on_screen(window_image)
                if point:
                    self.logger.info("Image is ready!")
                    return True
        
            time.sleep(3)  # Check every 2 seconds
        
        self.logger.warning(f"Image not ready after {timeout} seconds")
        return True