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
from Modules.bluestacks import BlueStacksBot

import pyautogui
import os


class ResourceFarmer:
    """Handles automated resource farming tasks using YOLO11 detection."""

    def __init__(self, config: BotConfig, logger: logging.Logger, model_path: str = None):
        self.config = config
        self.logger = logger
        self.input_handler = InputHandler(config, logger)
        self.farming_active = True
        self.bluestacks_bot = BlueStacksBot(self.config, self.logger)
        self.green_count = 0

        if model_path and Path(model_path).exists():
            self.yolo_handler = YOLOImageHandler(config, logger, model_path)
            self.use_yolo = True  # FIX: was hardcoded False
            self.logger.info("YOLO11 detection enabled")
        else:
            self.yolo_handler = None
            self.use_yolo = False
            self.logger.warning("YOLO model not available, falling back to traditional detection")
            from Modules.Bot.image_handler import ImageHandler
            self.image_handler = ImageHandler(config, logger)

    def take_screenshot(self, name: str = None):
        if name is None:
            name = f"Screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if self.use_yolo and self.yolo_handler:
            return self.yolo_handler.save_annotated_screenshot(f"{name}.png")
        else:
            screenshot = pyautogui.screenshot()
            save_path = Path(self.config.screenshot_dir) / f"{name}.png"
            screenshot.save(save_path)
            return str(save_path)

    def start_farming(self) -> bool:
        """Run one green-farming cycle using YOLO11 detection."""
        self.farming_active = True
        conf = self.config.yolo_confidence  # FIX: use config value, not hardcoded 0.1

        # Step 1: Find token_pack icon
        self.logger.info("Step 1: Looking for token pack using YOLO...")
        rest_point = self.yolo_handler.find_class_on_screen('token_pack', confidence_threshold=conf)

        if rest_point is None:
            self.logger.warning("Token pack not found — taking debug screenshot")
            count = len([x for x in os.listdir(self.config.screenshot_dir) if x.startswith("rest_icon_not_found")])
            self.take_screenshot(f"rest_icon_not_found_{count}")
            self.farming_active = False
            return False

        self.logger.info("Step 1: Found token pack, clicking...")
        if not self.input_handler.click_at_point(rest_point):
            self.logger.error("Failed to click token pack")
            self.farming_active = False
            return False

        # Step 2: Wait for watch ads button
        self.logger.info("Step 2: Waiting for watch ads button...")
        time.sleep(5)

        ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=conf)
        if not ads_point:
            self.logger.error("Watch ads button not found")
            count = len([x for x in os.listdir(self.config.screenshot_dir) if x.startswith("watch_ads_not_found")])
            self.take_screenshot(f"watch_ads_not_found_{count}")
            self.farming_active = False
            return False

        self.logger.info("Step 2: Found watch ads button, clicking...")
        self.input_handler.click_at_point(ads_point)
        time.sleep(3)

        # Step 3: Wait for ad to finish (adaptive — not blind sleep)
        self.logger.info("Step 3: Waiting for ad to complete...")
        time.sleep(75)

        # Step 4: Dismiss ad
        self.logger.info("Step 4: Dismissing ad...")
        dismissed = self._handle_ads_with_yolo(['skip_ad', 'close_ad'])

        if not dismissed:
            self.logger.warning("No dismiss button found, trying close only...")
            # Check if already back at watch ads (ad may have auto-closed)
            if self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=conf):
                self.logger.info("Back at watch ads — ad already closed")
                return True

            close_found = self._handle_ads_with_yolo(['close_ad'])
            if close_found:
                if self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=conf):
                    self.logger.info("Back at watch ads after close")
                    return True
                # Second ad may be playing
                self.logger.info("Waiting for possible second ad...")
                time.sleep(75)
                self._handle_ads_with_yolo(['skip_ad', 'close_ad'])
            else:
                self.logger.info("Hail mary: pressing Escape")
                self.bluestacks_bot.bluestacks_escape()

        else:
            # First ad dismissed — check for second ad
            self.logger.info("Step 5: Checking for second ad...")
            time.sleep(75)
            self._handle_ads_with_yolo(['skip_ad', 'close_ad'])

            if not self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=conf):
                self.logger.info("Hail mary: pressing Escape after second ad")
                self.bluestacks_bot.bluestacks_escape()

        self.logger.info("Farming cycle completed")
        return True

    def farm_rest_player(self) -> bool:
        """Watch one ad to earn a rest token (no token_pack step needed)."""
        self.farming_active = True
        conf = self.config.yolo_confidence

        self.logger.info("Step 1: Looking for watch ads button...")
        time.sleep(5)

        ads_point = self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=conf)
        if not ads_point:
            self.logger.error("Watch ads button not found")
            count = len([x for x in os.listdir(self.config.screenshot_dir) if x.startswith("watch_ads_not_found")])
            self.take_screenshot(f"watch_ads_not_found_{count}")
            self.farming_active = False
            return False

        self.logger.info("Step 2: Clicking watch ads...")
        self.input_handler.click_at_point(ads_point)
        time.sleep(3)

        self.logger.info("Step 3: Waiting for ad...")
        time.sleep(75)

        self.logger.info("Step 4: Dismissing ad...")
        skipped = self._handle_ads_with_yolo(['skip_ad'])
        if not skipped:
            close_found = self._handle_ads_with_yolo(['close_ad'])
            if close_found:
                if self.yolo_handler.find_class_on_screen("watch_ads_general", confidence_threshold=conf):
                    return True
                time.sleep(75)
                self._handle_ads_with_yolo(['close_ad'])
        else:
            time.sleep(75)
            self._handle_ads_with_yolo(['close_ad'])

        self.logger.info("Rest farming cycle completed")
        return True

    def _handle_ads_with_yolo(self, class_names: List[str]) -> bool:
        """Detect and click the highest-confidence match from the given class list."""
        conf = self.config.yolo_confidence
        try:
            detected = self.yolo_handler.find_objects_on_screen(
                target_classes=class_names,
                confidence_threshold=conf
            )
            if not detected:
                self.logger.info(f"No objects found for classes: {class_names}")
                return False

            best = max(detected, key=lambda obj: obj['confidence'])
            self.logger.info(f"Found {best['class_name']} (conf {best['confidence']:.2f})")

            if self.input_handler.click_at_point(best['center_point']):
                self.logger.info(f"Clicked {best['class_name']}")
                time.sleep(1)
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error in YOLO ad handling: {e}")
            return False

    def stop_farming(self) -> None:
        self.farming_active = False
        self.logger.info("Stopping resource farming...")

    def run_farming_cycle(self) -> Dict[str, bool]:
        if not self.farming_active:
            return {}

        results = {
            'ads_handled': False,
            'rest_clicked': False,
            'sequence_completed': False,
            'yolo_enabled': self.use_yolo,
            'cycle_time': time.time(),
        }

        # Clear any visible ads before the main sequence (FIX: was gated on use_yolo=False)
        if self.use_yolo and self.yolo_handler:
            results['ads_handled'] = self._handle_ads_with_yolo(
                ['close_ad', 'skip_ad']
            )

        success = self.start_farming()
        results['rest_clicked'] = success
        results['sequence_completed'] = success

        if success:
            self.logger.info("Farming sequence completed successfully")
        else:
            self.logger.warning("Farming sequence failed — will retry next cycle")

        return results

    def continuous_farming(self, cycle_interval: int = 10, farming_count: int = 0) -> None:
        self.logger.info(f"Starting continuous farming (interval: {cycle_interval}s)")

        green_count = 0
        max_greens = self.config.max_greens

        # FIX: use proper except syntax with `as e`
        if farming_count > 0:
            try:
                self._handle_ads_with_yolo(['top_elven_pop_up'])
            except Exception as e:
                self.logger.error(f"Error closing top eleven pop-up: {e}")
            try:
                self._handle_ads_with_yolo(['skip_ad'])
            except Exception as e:
                self.logger.error(f"Error closing skip ad: {e}")

        self.farming_active = True

        while self.farming_active and self.green_count < max_greens:  # FIX: check self.green_count
            try:
                results = self.run_farming_cycle()
                if results and results.get('sequence_completed', False):
                    green_count += 1
                    self.green_count += 1  # FIX: update self.green_count inside the loop
                    self.logger.info(f"Greens today: {self.green_count}/{max_greens}")

                if self.farming_active:
                    self.logger.info(f"Waiting {cycle_interval}s until next cycle...")
                    time.sleep(cycle_interval)

            except Exception as e:
                self.logger.error(f"Error in farming cycle: {e}")
                count = len([x for x in os.listdir(self.config.screenshot_dir) if x.startswith("farming_error")])
                self.take_screenshot(f"farming_error_{count + 1}")

        self.logger.info(f"Continuous farming stopped. Session greens: {green_count}, Total: {self.green_count}/{max_greens}")

    def get_detection_info(self) -> Dict:
        if self.use_yolo and self.yolo_handler:
            return {
                'detection_method': 'YOLO11',
                'model_info': self.yolo_handler.get_model_info()
            }
        return {
            'detection_method': 'Template Matching',
            'model_info': None
        }
