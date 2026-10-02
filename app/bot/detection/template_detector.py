"""Template-matching detection strategy, wrapping ImageHandler."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import pyscreeze

from app.bot.detection.base import DetectionStrategy
from Modules.Bot.config import BotConfig

# Map YOLO class names → one or more template image paths (relative to project root).
# Multiple paths = multiple visual variants of the same element.
CLASS_TEMPLATES: Dict[str, List[str]] = {
    "token_pack": [
        "Assets/TopEleven/rest_icon_dark_background.png",
    ],
    "watch_ads_general": [
        "Assets/TopEleven/watch_ads_blue.png",
        "Assets/TopEleven/watch_ads_green.png",
        "Assets/TopEleven/watch_ads_green_fullscreen.png",
        "Assets/TopEleven/watch_ads_green_windowed.png",
    ],
    "skip_ad": [
        *[f"Assets/TopEleven/Ads/skip/skip_{i}.png" for i in range(1, 7)],
        "Assets/TopEleven/skip.png",
    ],
    "close_ad": [
        *[f"Assets/TopEleven/Ads/close/close_{i}.png" for i in range(1, 15)],
        "Assets/TopEleven/advertisement-close.png",
    ],
    "top_elven_pop_up": [
        "Assets/pop_ups/pop_up_1.png",
    ],
    "daily_reward": [
        "Assets/TopEleven/daily_reward.png",
    ],
    "windows_button": [
        "Assets/Windows/start_icon_dark_mode.png",
        "Assets/Windows/start_icon_light_mode.png",
    ],
}


class TemplateDetector(DetectionStrategy):

    name = "Template Matching"

    def __init__(self, config: BotConfig, logger: logging.Logger):
        self._config = config
        self._logger = logger
        from Modules.Bot.image_handler import ImageHandler
        self._handler = ImageHandler(config, logger)

    def is_available(self) -> bool:
        return True

    def find_element(
        self,
        class_name: str,
        confidence: float = 0.5,
    ) -> Optional[pyscreeze.Point]:
        templates = CLASS_TEMPLATES.get(class_name, [])
        if not templates:
            self._logger.debug(f"TemplateDetector: no templates for '{class_name}'")
            return None

        for path in templates:
            if not Path(path).exists():
                continue
            try:
                img = self._handler.load_image(path)
                if img is None:
                    continue
                point = self._handler.find_image_on_screen(img)
                if point:
                    return point
            except Exception as e:
                self._logger.debug(f"Template {path}: {e}")

        return None

    def find_elements(
        self,
        class_names: List[str],
        confidence: float = 0.5,
    ) -> List[dict]:
        results = []
        for class_name in class_names:
            pt = self.find_element(class_name, confidence)
            if pt:
                results.append({
                    'class_name': class_name,
                    'confidence': 1.0,
                    'center_point': pt,
                    'detection_method': 'template',
                })
        return results
