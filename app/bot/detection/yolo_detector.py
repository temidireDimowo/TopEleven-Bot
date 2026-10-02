"""YOLO11-based detection strategy, wrapping YOLOImageHandler."""

import logging
from pathlib import Path
from typing import List, Optional
import pyscreeze

from app.bot.detection.base import DetectionStrategy
from Modules.Bot.config import BotConfig


class YOLODetector(DetectionStrategy):

    name = "YOLO11"

    def __init__(self, config: BotConfig, logger: logging.Logger, model_path: str):
        self._config = config
        self._logger = logger
        self._handler = None

        if model_path and Path(model_path).exists():
            try:
                from Modules.Bot.yolo_image_handler import YOLOImageHandler
                self._handler = YOLOImageHandler(config, logger, model_path)
                self._logger.info(f"YOLODetector loaded: {model_path}")
            except Exception as e:
                self._logger.warning(f"YOLODetector failed to load model: {e}")
        else:
            self._logger.warning(f"YOLO model not found at {model_path}")

    def is_available(self) -> bool:
        return self._handler is not None

    def find_element(
        self,
        class_name: str,
        confidence: float = 0.5,
    ) -> Optional[pyscreeze.Point]:
        if not self.is_available():
            return None
        try:
            return self._handler.find_class_on_screen(class_name, confidence_threshold=confidence)
        except Exception as e:
            self._logger.debug(f"YOLODetector.find_element({class_name}): {e}")
            return None

    def find_elements(
        self,
        class_names: List[str],
        confidence: float = 0.5,
    ) -> List[dict]:
        if not self.is_available():
            return []
        try:
            return self._handler.find_objects_on_screen(
                target_classes=class_names,
                confidence_threshold=confidence,
            )
        except Exception as e:
            self._logger.debug(f"YOLODetector.find_elements({class_names}): {e}")
            return []

    def get_model_info(self) -> Optional[dict]:
        if self._handler:
            return self._handler.get_model_info()
        return None

    def save_annotated_screenshot(self, filename: str) -> Optional[str]:
        if self._handler:
            return self._handler.save_annotated_screenshot(filename)
        return None
