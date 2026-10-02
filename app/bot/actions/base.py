"""BotAction abstract base class — shared helpers for all farming actions."""

import logging
import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import List, Optional
import pyscreeze

from Modules.Bot.config import BotConfig
from Modules.Bot.input_handler import InputHandler
from app.bot.detection.base import DetectionStrategy
from app.bot.platform.base import PlatformAdapter


class ActionResult:
    __slots__ = ('success', 'message', 'data')

    def __init__(self, success: bool, message: str = '', data: dict = None):
        self.success = success
        self.message = message
        self.data = data or {}


class BotAction(ABC):

    def __init__(
        self,
        config: BotConfig,
        logger: logging.Logger,
        detector: DetectionStrategy,
        input_handler: InputHandler,
        platform: PlatformAdapter,
        event_queue: queue.Queue,
        stop_event: threading.Event,
        pause_event: threading.Event,
    ):
        self.config = config
        self.logger = logger
        self.detector = detector
        self.input_handler = input_handler
        self.platform = platform
        self._eq = event_queue
        self._stop = stop_event
        self._pause = pause_event

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def execute(self) -> bool:
        """Run one complete cycle. Returns True on success."""
        ...

    # ── Shared helpers ───────────────────────────────────────────────

    def _emit(self, event_type: str, **data) -> None:
        try:
            self._eq.put_nowait({'type': event_type, **data})
        except queue.Full:
            pass

    def _should_stop(self) -> bool:
        return self._stop.is_set()

    def _wait_if_paused(self) -> bool:
        """Block while paused. Returns False if stopped while waiting."""
        while self._pause.is_set():
            if self._stop.is_set():
                return False
            time.sleep(0.3)
        return True

    def _adaptive_wait(
        self,
        target_classes: List[str],
        timeout: Optional[int] = None,
    ) -> Optional[pyscreeze.Point]:
        """
        Poll every 2s for any class in target_classes.
        Respects stop and pause events. Returns point or None on timeout.
        """
        timeout = timeout or self.config.ad_wait_timeout
        deadline = time.time() + timeout
        conf = self.config.yolo_confidence

        while time.time() < deadline:
            if not self._wait_if_paused():
                return None
            if self._should_stop():
                return None

            results = self.detector.find_elements(target_classes, conf)
            if results:
                best = max(results, key=lambda r: r.get('confidence', 0))
                return best['center_point']

            time.sleep(2)

        return None

    def _click(self, point: pyscreeze.Point) -> bool:
        return self.input_handler.click_at_point(point)

    def _find(self, class_name: str) -> Optional[pyscreeze.Point]:
        return self.detector.find_element(class_name, self.config.yolo_confidence)

    def _interruptible_sleep(self, seconds: float) -> bool:
        """Sleep in 0.5s chunks, respecting stop/pause. Returns False if interrupted."""
        end = time.time() + seconds
        while time.time() < end:
            if not self._wait_if_paused():
                return False
            if self._should_stop():
                return False
            time.sleep(0.5)
        return True
