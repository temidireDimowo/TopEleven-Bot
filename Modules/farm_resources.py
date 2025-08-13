"""
Resource farming automation module with YOLO11 support.
Handles automated collection of resources, rewards, and repetitive tasks.
"""

import logging
import time
from typing import List, Dict, Optional
from pathlib import Path
import datetime
from Modules.Bot.config import BotConfig, ClickType
from Modules.Bot.yolo_image_handler import YOLOImageHandler
from Modules.Bot.input_handler import InputHandler
import pyautogui
import os


class ResourceFarmer:
    """Handles automated resource farming tasks using YOLO11 detection."""
    
    def __init__(self, config: BotConfig, logger: logging.Logger, model_path: str = None):
        self.config = config
        self.logger = logger
        self.input_handler = InputHandler(config, logger)
        self.farming_active = True
        
        # Initialize YOLO handler if model path is provided
        if model_path and Path(model_path).exists():
            self.yolo_handler = YOLOImageHandler(config, logger, model_path)
            self.use_yolo = False
            self.logger.info("YOLO11 detection enabled")
        else:
            self.yolo_handler = None
            self.use_yolo = False
            self.logger.warning("YOLO model not available, falling back to traditional detection")
            # Fallback to original image handler
            from Modules.Bot.image_handler import ImageHandler
            self.image_handler = ImageHandler(config, logger)

    def take_screenshot(self, name: str = None):
        """Take a screenshot for debugging."""
        if name is None:
            name = f"Screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.use_yolo:
            # Save annotated screenshot with YOLO detections
            return self.yolo_handler.save_annotated_screenshot(f"{name}.png")
        else:
            # Regular screenshot
            screenshot = pyautogui.screenshot()
            save_path = Path(self.config.screenshot_dir) / f"{name}.png"
            screenshot.save(save_path)
            return str(save_path)

    def start_farming(self) -> bool:
        """
        Start the resource farming process with YOLO11 detection:
        1. Look for token_icon using YOLO
        2. Wait for watch_ads button to appear and click it
        3. Sleep for 61 seconds
        4. Try to skip ads using YOLO detection
        5. If no skip found, try close ads
        """
        self.farming_active = True
        self.logger.info("Starting YOLO-enhanced resource farming sequence...")

        # Step 1: Look for token icon using YOLO
        self.logger.info("Step 1: Looking for token icon using YOLO...")
        
        token_point = self.yolo_handler.find_class_on_screen('token_pack', confidence_threshold=0.1)
        
        if token_point is None:
            self.logger.warning("token icon not found with YOLO - taking debug screenshot")
            token_icon_not_found_count = len([x for x in os.listdir(self.config.screenshot_dir) if (x.startswith("token_icon_not_found"))])
            self.take_screenshot("token_icon_not_found"+f"_{token_icon_not_found_count}")
            self.logger.warning("Stopping farming sequence - token icon not available")
            self.farming_active = False
            return False
            
        self.logger.info("Step 1: Found and clicking token icon")
        if not self.input_handler.click_at_point(token_point):
            self.logger.error("Failed to click token icon")
            self.farming_active = False
            return False
        
        # Step 2: Wait for watch ads button using YOLO
        self.logger.info("Step 2: Waiting for watch ads button to appear...")
        time.sleep(5)  # Brief wait for interface to update
        
        # Watch ads variable
        watch_ads_found = False
        
        ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=0.1)
        if ads_point:
            self.logger.info(f"Step 2: Found watch ads button using class: watch_ads_general")
            if self.input_handler.click_at_point(ads_point):
                watch_ads_found = True
            time.sleep(3)
        
        if not watch_ads_found:
            self.logger.error("Watch ads button not found with YOLO")
            watch_ads_not_found_count = len([x for x in os.listdir(self.config.screenshot_dir) if (x.startswith("watch_ads_not_found"))])
            self.take_screenshot("watch_ads_not_found"+f"_{watch_ads_not_found_count}")
            self.farming_active = False
            return False
            
        # Step 3: Sleep for 61 seconds
        self.logger.info("Step 3: Sleeping for 61 seconds...")
        time.sleep(65)
        
        # Step 4: Try to skip ads using YOLO
        self.logger.info("Step 4: Attempting to skip ads using YOLO...")
        skip_found = self._handle_ads_with_yolo(['skip_ad'])
        
        # Step 5: If no skip found, try close ads
        if not skip_found:
            self.logger.info("Step 5: No skip ads found, trying close ads...")
            close_found = self._handle_ads_with_yolo(['close_ad'])
            
            if close_found:
                # Check if there is a watch_ads_general image, else wait for the second ad close button
                ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=0.45)
                if ads_point:
                    self.logger.info(f"Step 2: Found watch ads button using class: watch_ads_general")
                    if self.input_handler.click_at_point(ads_point):
                        watch_ads_found = True
                    time.sleep(3)
                else:
                    self.logger.info("Step 6: Sleeping for 65s - checking for second ad...")
                    time.sleep(65)
                    self._handle_ads_with_yolo(['close_ad'],['skip_ad'])
            else:
                self.logger.warning("No ads found to close")
        else:
            self.logger.info("Step 5: Skip ads found, checking for close ads after 65 seconds...")
            time.sleep(65)
            self._handle_ads_with_yolo(['close_ad'])
            if close_found:
                # Check if there is a watch_ads_general image, else wait for the second ad close button
                ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=0.45)
                if ads_point:
                    self.logger.info(f"Step 6: Found watch ads button using class: watch_ads_general")
                    if self.input_handler.click_at_point(ads_point):
                        watch_ads_found = True
                    time.sleep(3)
                else:
                    self.logger.info("Step 7: Sleeping for 65s - checking for second ad...")
                    time.sleep(65)
                    self._handle_ads_with_yolo(['close_ad'],['skip_ad'])
        
        self.logger.info("YOLO-enhanced farming sequence completed successfully")
        return True
    
    def farm_token_player(self) -> bool:
        """
        Start the resource farming process with YOLO11 detection:
        1. Look for general_watch_ads button to appear and click it
        2. Sleep for 61 seconds
        3. Try to skip ads using YOLO detection
        4. If no skip found, try close ads
        """
        self.farming_active = True
        self.logger.info("Starting farm token player...")

        # Step 2: Wait for watch ads button using YOLO
        self.logger.info("Step 1: Waiting for watch ads button to appear...")
        time.sleep(5)  # Brief wait for interface to update
        
        # Watch ads variable
        watch_ads_found = False
        
        ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=0.1)
        if ads_point:
            self.logger.info(f"Step 2: Found watch ads button using class: watch_ads_general")
            if self.input_handler.click_at_point(ads_point):
                watch_ads_found = True
            time.sleep(3)
        
        if not watch_ads_found:
            self.logger.error("Watch ads button not found with YOLO")
            watch_ads_not_found_count = len([x for x in os.listdir(self.config.screenshot_dir) if (x.startswith("watch_ads_not_found"))])
            self.take_screenshot("watch_ads_not_found"+f"_{watch_ads_not_found_count}")
            self.farming_active = False
            return False
            
        # Step 3: Sleep for 61 seconds
        self.logger.info("Step 3: Sleeping for 61 seconds...")
        time.sleep(61)
        
        # Step 4: Try to skip ads using YOLO
        self.logger.info("Step 4: Attempting to skip ads using YOLO...")
        skip_found = self._handle_ads_with_yolo(['skip_ad'])
        
        # Step 5: If no skip found, try close ads
        if not skip_found:
            self.logger.info("Step 5: No skip ads found, trying close ads...")
            close_found = self._handle_ads_with_yolo(['close_ad'])
            
            if close_found:
                # Check if there is a watch_ads_general image, else wait for the second ad close button
                ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=0.45)
                if ads_point:
                    self.logger.info(f"Step 2: Found watch ads button using class: watch_ads_general")
                    if self.input_handler.click_at_point(ads_point):
                        watch_ads_found = True
                    time.sleep(3)
                else:
                    self.logger.info("Step 6: Sleeping for 65s - checking for second ad...")
                    time.sleep(65)
                    self._handle_ads_with_yolo(['close_ad'])
            else:
                self.logger.warning("No ads found to close")
        else:
            self.logger.info("Step 5: Skip ads found, checking for close ads after 65 seconds...")
            time.sleep(65)
            self._handle_ads_with_yolo(['close_ad'])
        
        self.logger.info("YOLO-enhanced farming sequence completed successfully")
        return True
   
    def _handle_ads_with_yolo(self, class_names: List[str]) -> bool:
        """
        Handle ads using YOLO detection for specified class names.
        
        Args:
            class_names: List of class names to look for
            
        Returns:
            True if any ad was found and clicked, False otherwise
        """
        try:
            # Find all objects of specified classes
            detected_objects = self.yolo_handler.find_objects_on_screen(
                target_classes=class_names, 
                confidence_threshold=0.1
            )
            
            if not detected_objects:
                self.logger.info(f"No objects found for classes: {class_names}")
                return False
            
            # Click on the best match (highest confidence)
            best_match = max(detected_objects, key=lambda obj: obj['confidence'])
            
            self.logger.info(
                f"Found {best_match['class_name']} with confidence {best_match['confidence']:.2f}"
            )
            
            if self.input_handler.click_at_point(best_match['center_point']):
                self.logger.info(f"Successfully clicked {best_match['class_name']}")
                time.sleep(1)  # Brief pause after clicking
                return True
            else:
                self.logger.warning(f"Failed to click {best_match['class_name']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in YOLO ad handling: {e}")
            return False

    def stop_farming(self) -> None:
        """Stop the resource farming process."""
        self.farming_active = False
        self.logger.info("Stopping resource farming...")
        
    def run_farming_cycle(self) -> Dict[str, bool]:
        """
        Run a complete farming cycle with YOLO11 detection.
        
        Returns:
            Dictionary with cycle results
        """
        if not self.farming_active:
            return {}
            
        results = {
            'ads_handled': False,
            'rewards_collected': False,
            'token_clicked': False,
            'cycle_time': time.time(),
            'sequence_completed': False,
            'yolo_enabled': self.use_yolo
        }
        
        self.logger.info("Running YOLO-enhanced farming cycle...")
        
        # Handle any visible ads first
        if self.use_yolo:
            results['ads_handled'] = self._handle_ads_with_yolo([
                'close_ad', 'close', 'skip_ad', 'skip', 'x_button'
            ])
        
        # Try to run the main farming sequence
        token_success = self.start_farming()
        results['token_clicked'] = token_success
        results['sequence_completed'] = token_success
        
        if token_success:
            self.logger.info("YOLO-enhanced farming sequence completed successfully")
        else:
            self.logger.warning("Farming sequence failed - will retry in next cycle")
            
        return results
        
    def continuous_farming(self, cycle_interval: int = 10) -> None:
        """
        Run continuous farming with YOLO11 detection.
        
        Args:
            cycle_interval: Seconds between farming cycles
        """
        self.logger.info(f"Starting YOLO-enhanced continuous farming (interval: {cycle_interval}s)")
        
        green_count = 0
        max_greens = 25
        
        # Setting farming active to true so that we can farm greens
        # if there is a failure farming state will be set to False 
        self.farming_active = True
        print(self.farming_active)

        while self.farming_active and green_count < max_greens:
            try:
                results = self.run_farming_cycle()
                if results:
                    self.logger.info(f"Farming cycle results: {results}")
                    if results.get('sequence_completed', False):
                        green_count += 1
                        self.logger.info(f"Greens collected: {green_count}/{max_greens}")
                
                if self.farming_active:  # Check again before sleeping
                    self.logger.info(f"Waiting {cycle_interval}s until next cycle...")
                    time.sleep(cycle_interval)
                    
            except Exception as e:
                self.logger.error(f"Error in farming cycle: {e}")
                farming_error_count = len([x for x in os.listdir(self.config.screenshot_dir) if (x.startswith("farming_error"))])
                self.take_screenshot("farming_error"+f"_{farming_error_count+1}")
                
        self.logger.info(f"YOLO-enhanced continuous farming stopped. Total greens: {green_count}")

    def get_detection_info(self) -> Dict:
        """Get information about the current detection method."""
        if self.use_yolo:
            return {
                'detection_method': 'YOLO11',
                'model_info': self.yolo_handler.get_model_info()
            }
        else:
            return {
                'detection_method': 'Traditional Image Matching',
                'model_info': None
            }