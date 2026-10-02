"""Detection strategy abstract base class."""

import threading
import time
from abc import ABC, abstractmethod
from typing import List, Optional
import pyscreeze


class DetectionStrategy(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def find_element(
        self,
        class_name: str,
        confidence: float = 0.5,
    ) -> Optional[pyscreeze.Point]: ...

    @abstractmethod
    def find_elements(
        self,
        class_names: List[str],
        confidence: float = 0.5,
    ) -> List[dict]: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    def wait_for_element(
        self,
        class_name: str,
        timeout: int = 90,
        confidence: float = 0.5,
        stop_event: Optional[threading.Event] = None,
    ) -> Optional[pyscreeze.Point]:
        """Poll every 2s until class_name appears or timeout/stop fires."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if stop_event and stop_event.is_set():
                return None
            pt = self.find_element(class_name, confidence)
            if pt is not None:
                return pt
            time.sleep(2)
        return None
