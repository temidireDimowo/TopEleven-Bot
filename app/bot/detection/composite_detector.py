"""Composite detector: YOLO first, template matching as fallback."""

import logging
from typing import List, Optional
import pyscreeze

from app.bot.detection.base import DetectionStrategy
from app.bot.detection.yolo_detector import YOLODetector
from app.bot.detection.template_detector import TemplateDetector
from Modules.Bot.config import BotConfig


class CompositeDetector(DetectionStrategy):

    name = "Composite (YOLO + Template)"

    def __init__(self, config: BotConfig, logger: logging.Logger):
        self._config = config
        self._logger = logger

        model_path = config.yolo_model_path if config.yolo_enabled else None
        self._yolo = YOLODetector(config, logger, model_path) if model_path else None
        self._template = TemplateDetector(config, logger)

        if self._yolo and self._yolo.is_available():
            self._logger.info("CompositeDetector: YOLO primary, template fallback")
        else:
            self._logger.info("CompositeDetector: template matching only")

    @property
    def name(self) -> str:
        if self._yolo and self._yolo.is_available():
            return "YOLO11 + Template Fallback"
        return "Template Matching"

    def is_available(self) -> bool:
        return True

    def find_element(
        self,
        class_name: str,
        confidence: float = 0.5,
    ) -> Optional[pyscreeze.Point]:
        # Try YOLO first
        if self._yolo and self._yolo.is_available():
            pt = self._yolo.find_element(class_name, confidence)
            if pt is not None:
                return pt

        # Fallback to template matching
        if self._config.fallback_to_traditional:
            return self._template.find_element(class_name, confidence)

        return None

    def find_elements(
        self,
        class_names: List[str],
        confidence: float = 0.5,
    ) -> List[dict]:
        if self._yolo and self._yolo.is_available():
            results = self._yolo.find_elements(class_names, confidence)
            if results:
                return results

        if self._config.fallback_to_traditional:
            return self._template.find_elements(class_names, confidence)

        return []

    @property
    def yolo_detector(self) -> Optional[YOLODetector]:
        return self._yolo
