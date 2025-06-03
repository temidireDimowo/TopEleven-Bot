"""
Resource farming automation module.
Handles automated collection of resources, rewards, and repetitive tasks.
"""

import logging
import time
from typing import List, Dict, Optional
from pathlib import Path
import datetime
from Modules.Bot.config import BotConfig, ClickType
from Modules.Bot.image_handler import ImageHandler
from Modules.Bot.input_handler import InputHandler
import pyautogui


class ResourceFarmer:
    """Handles automated resource farming tasks."""
    
    def __init__(self, config: BotConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.image_handler = ImageHandler(config, logger)
        self.input_handler = InputHandler(config, logger)
        self.farming_active = False
        
        # Resource farming patterns will use directory structure from config
        self.resource_patterns = {
            'skip_popup': ['skip*.png', 'skip_ad*.png'],
            'close_popup': ['close*.png', 'x_button*.png', 'dismiss*.png'],
            'collect_rewards': ['collect*.png', 'claim*.png', 'reward*.png'],
            'daily_bonus': ['daily*.png', 'bonus*.png'],
            'rest_icon': ['rest_icon*.png', 'rest_button*.png']
        }

    def take_screenshot(name: str = "Screenshot"+str(datetime.datetime.now())):
        screenshot = pyautogui.screenshot(name)
        screenshot.save(self.config.log_dir)

    def start_farming(self) -> bool:
        """
        Start the resource farming process with specific sequence:
        1. Click on rest_icon_dark_background.png
        2. Wait for watch_ads_green.png to appear and click it
        3. Sleep for 61 seconds
        4. Try to skip ads using skip directory
        5. If no skip images found, try close directory
        
        STOPS immediately if rest icon image file is not found.
        """
        self.farming_active = True
        self.logger.info("🌾 Starting resource farming sequence...")
        
        # Step 1: Check if rest icon file exists first
        rest_icon_path = str(Path(self.config.top_eleven_dir) / "rest_icon_dark_background.png")
        
        # Check if the file exists before trying to load it
        if not Path(rest_icon_path).exists():
            self.logger.error(f"❌ Rest icon image file not found: {rest_icon_path}")
            self.logger.error("🛑 Stopping farming sequence - required image file missing")
            self.farming_active = False
            return False
        
        # self.logger.error(f"This is the path for the rest icon {rest_icon_path}")

        # Try to load the rest icon image
        rest_icon_image = self.image_handler.load_image(rest_icon_path)
        
        if rest_icon_image is None:
            self.logger.error(f"❌ Failed to load rest icon image: {rest_icon_path}")
            self.logger.error("🛑 Stopping farming sequence - could not load required image")
            self.farming_active = False
            return False
        
        # Try to find the rest icon on screen
        point = self.image_handler.find_image_on_screen(rest_icon_image)
        if point is None:
            self.logger.warning("⚠️ Rest icon not found on screen - may not be visible yet")
            self.logger.warning("🛑 Stopping farming sequence - rest icon not available")
            self.farming_active = False
            return False
            
        self.logger.info("✅ Step 1: Found and clicking rest icon")
        if not self.input_handler.click_at_point(point):
            self.logger.error("❌ Failed to click rest icon")
            self.logger.error("🛑 Stopping farming sequence - click failed")
            self.farming_active = False
            return False
        
        self.logger.info("⏳ Step 1.5: Sleep for 5 seconds waiting for watch ads button to appear...")
        time.sleep(5)

        # Step 2: Wait for watch ads button to appear and click it
        watch_ads_path = str(Path(self.config.top_eleven_dir) / "watch_ads_green_windowed.png")
        self.logger.info("⏳ Step 2: Waiting for watch ads button to appear...")
        
        if not self.image_handler.wait_for_image(watch_ads_path, timeout=30):
            self.logger.error("❌ Watch ads button did not appear within 30 seconds")
            self.logger.error("🛑 Stopping farming sequence - watch ads button timeout")
            self.farming_active = False
            return False
            
        watch_ads_image = self.image_handler.load_image(watch_ads_path)
        if watch_ads_image is None:
            self.logger.error(f"❌ Watch ads image not found: {watch_ads_path}")
            self.logger.error("🛑 Stopping farming sequence - watch ads image missing")
            self.farming_active = False
            return False
            
        point = self.image_handler.find_image_on_screen(watch_ads_image)
        if point is None:
            self.logger.warning("⚠️ Watch ads button not found on screen")
            self.logger.warning("🛑 Stopping farming sequence - watch ads button not visible")
            self.farming_active = False
            return False
            
        self.logger.info("✅ Step 2: Found and clicking watch ads button")
        if not self.input_handler.click_at_point(point):
            self.logger.error("❌ Failed to click watch ads button")
            self.logger.error("🛑 Stopping farming sequence - watch ads click failed")
            self.farming_active = False
            return False
            
        # Step 3: Sleep for 61 seconds
        self.logger.info("😴 Step 3: Sleeping for 61 seconds...")
        time.sleep(61)
        
        # Step 4: Try to skip ads using skip directory
        self.logger.info("🔄 Step 4: Attempting to skip ads...")
        skip_found = self._iterate_through_directory_images(self.config.skip_dir, "skip")
        
        # Step 5: If no skip images found, try close directory
        if not skip_found:
            self.logger.info("🔄 Step 5: No skip ads found, trying close ads...")
            close_found = self._iterate_through_directory_images(self.config.close_dir, "close")
            
            if(close_found):
                self.logger.info("🔄 Step 6: Sleeping for 65s Closed one add, checking if there are two ads...")
                time.sleep(65)
                close_found = self._iterate_through_directory_images(self.config.close_dir, "close")
            else:
                self.logger.warning("⚠️ No skip or close ads found")
        else:
            self.logger.info("🔄 Step 5: Skip ads found, trying close ads after 65 seconds...")
            time.sleep(65)
            close_found = self._iterate_through_directory_images(self.config.close_dir, "close")

        
        self.logger.info("✅ Farming sequence completed successfully")
        return True
        
    def _iterate_through_directory_images(self, directory: str, action_type: str) -> bool:
        """
        Iterate through all images in a directory and try to click them.
        
        Args:
            directory: Directory path to search for images
            action_type: Type of action for logging ("skip" or "close")
            
        Returns:
            True if any image was found and clicked, False otherwise
        """
        if not directory:
            self.logger.warning(f"{action_type.title()} directory not configured")
            return False
            
        directory_path = Path(directory)
        if not directory_path.exists():
            self.logger.warning(f"{action_type.title()} directory does not exist: {directory}")
            return False
        
        # Get all image files in the directory
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
        image_files = []
        
        for extension in image_extensions:
            image_files.extend(directory_path.glob(extension))
        
        if not image_files:
            self.logger.info(f"No image files found in {action_type} directory: {directory}")
            return False
        
        self.logger.info(f"Found {len(image_files)} images in {action_type} directory image files in a an array {image_files}")
        
        # Try each image file
        for image_file in sorted(image_files):
            try:
                # Load image using relative path from images_dir
                try:
                    # relative_path = image_file.relative_to("Assets" / Path(self.config.images_dir))
                    # image = self.image_handler.load_image(str(relative_path))
                    image = self.image_handler.load_image(str(image_file))

                except Exception as e:
                    # If not relative to images_dir, use absolute path
                    image = self.image_handler.load_image(str(image_file))
                    self.logger.error(f"Error loading image out of images in dir using relative path{e}")

                if image is None:
                    self.logger.debug(f"Could not load image: {image_file.name}")
                    continue
                
                # Try to find the image on screen
                point = self.image_handler.find_image_on_screen(image)
                if point is not None:
                    self.logger.info(f"✅ Found {action_type} button: {image_file.name}")
                    if self.input_handler.click_at_point(point):
                        self.logger.info(f"✅ Successfully clicked {action_type} button")
                        time.sleep(1)  # Brief pause after clicking
                        return True
                    else:
                        self.logger.warning(f"Failed to click {action_type} button: {image_file.name}")
                else:
                    self.logger.debug(f"Image not found on screen: {image_file.name}")
                    
            except Exception as e:
                self.logger.error(f"Error processing {action_type} image {image_file.name}: {e}")
                continue
        
        self.logger.info(f"No {action_type} buttons found on screen")
        return False

    def stop_farming(self) -> None:
        """Stop the resource farming process."""
        self.farming_active = False
        self.logger.info("🛑 Stopping resource farming...")
        
    def find_and_click_pattern(self, pattern_name: str, search_directory: str = None) -> bool:
        """
        Find and click images matching a specific pattern.
        
        Args:
            pattern_name: Name of the pattern from resource_patterns
            search_directory: Specific directory to search in (optional)
            
        Returns:
            True if found and clicked, False otherwise
        """
        if pattern_name not in self.resource_patterns:
            self.logger.warning(f"Unknown pattern: {pattern_name}")
            return False
            
        patterns = self.resource_patterns[pattern_name]
        
        # Use specific directory or default to images_dir
        if search_directory:
            search_dir = Path(search_directory)
        else:
            search_dir = Path(self.config.images_dir)
        
        for pattern in patterns:
            matching_files = list(search_dir.glob(pattern))
            for image_file in sorted(matching_files):
                # Get relative path from images_dir for image_handler
                try:
                    relative_path = image_file.relative_to(Path(self.config.images_dir))
                    image = self.image_handler.load_image(str(relative_path))
                except ValueError:
                    # If not relative to images_dir, use full path
                    image = self.image_handler.load_image(str(image_file))
                    
                if image is None:
                    continue
                    
                point = self.image_handler.find_image_on_screen(image)
                if point is not None:
                    self.logger.info(f"🎯 Found {pattern_name}: {image_file.name}")
                    return self.input_handler.click_at_point(point)
                    
        return False
        
    def skip_and_close_ads(self) -> bool:
        """
        Skip and close ads using patterns from config directories.
        
        Returns:
            True if any ad was closed, False otherwise
        """
        ads_handled = False
        
        # Try to skip ads using skip_dir from config
        if self.find_and_click_pattern('skip_popup', self.config.skip_dir):
            self.logger.info("✅ Skipped ad")
            ads_handled = True
            time.sleep(1)  # Brief pause after skipping
            
        # Try to close ads using close_dir from config
        if self.find_and_click_pattern('close_popup', self.config.close_dir):
            self.logger.info("✅ Closed ad")
            ads_handled = True
            time.sleep(1)  # Brief pause after closing

        # Try to close ads using close_dir from config
        if self.find_and_click_pattern('close_popup', self.config.close_dir):
            self.logger.info("✅ Closed ad")
            ads_handled = True
            time.sleep(1)  # Brief pause after closing
            
        return ads_handled
        
    # def collect_daily_rewards(self) -> bool:
    #     """
    #     Collect daily login rewards and bonuses.
        
    #     Returns:
    #         True if rewards were collected, False otherwise
    #     """
    #     self.logger.info("🎁 Attempting to collect daily rewards...")
        
    #     rewards_collected = False
        
    #     # Look for daily bonus in top eleven directory
    #     if self.find_and_click_pattern('daily_bonus', self.config.top_eleven_dir):
    #         self.logger.info("✅ Collected daily bonus")
    #         rewards_collected = True
    #         time.sleep(2)  # Wait for reward dialog
            
    #     # Look for general collect rewards
    #     if self.find_and_click_pattern('collect_rewards', self.config.top_eleven_dir):
    #         self.logger.info("✅ Collected rewards")
    #         rewards_collected = True
    #         time.sleep(2)  # Wait for reward dialog
            
    #     return rewards_collected
        
    def run_farming_cycle(self) -> Dict[str, bool]:
        """
        Run a complete farming cycle.
        Only proceeds if the rest icon image file exists and is found.
        
        Returns:
            Dictionary with cycle results
        """
        if not self.farming_active:
            return {}
            
        results = {
            'ads_handled': False,
            'rewards_collected': False,
            'rest_clicked': False,
            'cycle_time': time.time(),
            'sequence_completed': False
        }
        
        self.logger.info("🔄 Running farming cycle...")
        
        # Handle ads first
        results['ads_handled'] = self.skip_and_close_ads()
        
        # Collect any available rewards
        # results['rewards_collected'] = self.collect_daily_rewards()
        
        # Try to run the main farming sequence
        rest_success = self.start_farming()
        results['rest_clicked'] = rest_success
        results['sequence_completed'] = rest_success
        
        if rest_success:
            self.logger.info("✅ Farming sequence completed successfully")
        else:
            self.logger.warning("⚠️ Farming sequence failed - rest icon not available")
            self.logger.info("🔄 Will retry in next cycle...")
            
        return results
        
    def continuous_farming(self, cycle_interval: int = 10) -> None:
        """
        Run continuous farming with specified interval.
        
        Args:
            cycle_interval: Seconds between farming cycles
        """
        self.logger.info(f"🔁 Starting continuous farming (interval: {cycle_interval}s)")
        
        # Variable for top eleven greens
        green_count = 25
        while self.farming_active and green_count>0:
            try:
                results = self.run_farming_cycle()
                
                if results:
                    self.logger.info(f"📊 Farming cycle results: {results}")
                    green_count += 1
                    
                    # If sequence didn't complete due to missing rest icon, 
                    # still continue but log the issue
                    if not results.get('sequence_completed', False):
                        self.logger.info("⏰ Rest icon not available this cycle, will try again next time")
                
                if self.farming_active:  # Check again before sleeping
                    self.logger.info(f"⏰ Waiting {cycle_interval}s until next cycle..., green count is {green_count}")
                    time.sleep(cycle_interval)
                    
            except Exception as e:
                self.logger.error(f"Error in farming cycle taking screenshot for further debugging: {e}")
                self.take_screenshot("Error in farming ")
                
        self.logger.info("🏁 Continuous farming stopped")

