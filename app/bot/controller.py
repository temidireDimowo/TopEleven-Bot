"""BotController — orchestrates the worker thread and surfaces events to the UI."""

import logging
import queue
import threading
import time
from typing import Optional

from Modules.Bot.config import BotConfig
from Modules.Bot.log import BotLogger, UILogHandler
from Modules.Bot.input_handler import InputHandler
from app.bot.detection.composite_detector import CompositeDetector
from app.bot.platform.base import PlatformAdapter
from app.data.session_store import SessionStore


class BotController:
    """Owns the worker thread; drives actions; surfaces events via queue."""

    STATUS_IDLE = "idle"
    STATUS_RUNNING = "running"
    STATUS_PAUSED = "paused"
    STATUS_ERROR = "error"

    def __init__(self, event_queue: queue.Queue):
        self._eq = event_queue
        self.config: Optional[BotConfig] = None
        self.logger: Optional[logging.Logger] = None
        self._detector: Optional[CompositeDetector] = None
        self._platform: Optional[PlatformAdapter] = None
        self._session_store: Optional[SessionStore] = None
        self._input: Optional[InputHandler] = None

        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._worker: Optional[threading.Thread] = None

        self._status = self.STATUS_IDLE
        self._green_count = 0
        self._cycle_count = 0
        self._error_count = 0
        self._session_id: Optional[int] = None
        self._session_start: Optional[float] = None

    # ── Lifecycle ────────────────────────────────────────────────────

    def initialize(self) -> bool:
        try:
            self.config = BotConfig.from_json("config.json")
            bot_logger = BotLogger("TopElevenBot")
            bot_logger.add_ui_handler(self._eq)
            self.logger = bot_logger.logger

            self._detector = CompositeDetector(self.config, self.logger)
            self._platform = PlatformAdapter.for_current_platform(self.config, self.logger)
            self._session_store = SessionStore()
            self._input = InputHandler(self.config, self.logger)
            self._emit('status_change', status=self.STATUS_IDLE)
            return True
        except Exception as exc:
            self._emit('error', message=f"Initialization failed: {exc}")
            return False

    def start(self, mode: str = "farm_greens") -> bool:
        if self._worker and self._worker.is_alive():
            return False
        if self.config is None:
            self.initialize()

        self._stop_event.clear()
        self._pause_event.clear()
        self._green_count = 0
        self._cycle_count = 0
        self._error_count = 0
        self._session_start = time.time()
        self._session_id = self._session_store.start_session(mode)

        self._worker = threading.Thread(
            target=self._run_loop,
            args=(mode,),
            daemon=True,
            name="BotWorker",
        )
        self._set_status(self.STATUS_RUNNING)
        self._worker.start()
        return True

    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.clear()
        if self._worker:
            self._worker.join(timeout=10)
        self._finalize_session()
        self._set_status(self.STATUS_IDLE)

    def pause(self) -> None:
        if self._status == self.STATUS_RUNNING:
            self._pause_event.set()
            self._set_status(self.STATUS_PAUSED)

    def resume(self) -> None:
        if self._status == self.STATUS_PAUSED:
            self._pause_event.clear()
            self._set_status(self.STATUS_RUNNING)

    # ── Worker loop ──────────────────────────────────────────────────

    def _run_loop(self, mode: str) -> None:
        action = self._build_action(mode)
        if action is None:
            self._emit('error', message=f"Unknown mode: {mode}")
            self._set_status(self.STATUS_IDLE)
            return

        try:
            while not self._stop_event.is_set():
                if self._green_count >= self.config.max_greens:
                    self._emit('log', level='success',
                               message=f"Target reached: {self._green_count} greens farmed!")
                    break

                # Respect pause
                while self._pause_event.is_set():
                    if self._stop_event.is_set():
                        return
                    time.sleep(0.3)

                success = action.execute()
                self._cycle_count += 1

                if success:
                    self._green_count += 1
                    self._emit('green_count',
                               current=self._green_count,
                               maximum=self.config.max_greens)
                else:
                    self._error_count += 1

                self._emit('cycle_complete',
                           cycle=self._cycle_count,
                           green_count=self._green_count,
                           success=success)

                # Wait between cycles (interruptible)
                interval = self.config.cycle_interval
                deadline = time.time() + interval
                while time.time() < deadline:
                    if self._stop_event.is_set():
                        return
                    remaining = max(0, deadline - time.time())
                    self._emit('next_cycle_in', seconds=int(remaining))
                    time.sleep(min(1, remaining))

        except Exception as exc:
            self.logger.exception("Unhandled error in bot loop")
            self._emit('error', message=str(exc))
            self._set_status(self.STATUS_ERROR)
        finally:
            self._finalize_session()
            if self._status not in (self.STATUS_ERROR, self.STATUS_IDLE):
                self._set_status(self.STATUS_IDLE)

    # ── Helpers ──────────────────────────────────────────────────────

    def _build_action(self, mode: str):
        common = dict(
            config=self.config,
            logger=self.logger,
            detector=self._detector,
            input_handler=self._input,
            platform=self._platform,
            event_queue=self._eq,
            stop_event=self._stop_event,
            pause_event=self._pause_event,
        )
        if mode == "farm_greens":
            from app.bot.actions.farm_greens import FarmGreensAction
            return FarmGreensAction(**common)
        if mode == "farm_rest":
            from app.bot.actions.farm_rest import FarmRestAction
            return FarmRestAction(**common)
        if mode == "claim_daily":
            from app.bot.actions.claim_daily import ClaimDailyAction
            return ClaimDailyAction(**common)
        return None

    def _finalize_session(self) -> None:
        if self._session_id is not None and self._session_store is not None:
            try:
                self._session_store.end_session(
                    self._session_id,
                    self._green_count,
                    self._cycle_count,
                    self._error_count,
                )
            except Exception:
                pass
            self._session_id = None

    def _set_status(self, status: str) -> None:
        self._status = status
        self._emit('status_change', status=status)

    def _emit(self, event_type: str, **data) -> None:
        try:
            self._eq.put_nowait({'type': event_type, **data})
        except queue.Full:
            pass

    @property
    def status(self) -> str:
        return self._status

    @property
    def green_count(self) -> int:
        return self._green_count

    @property
    def session_elapsed(self) -> float:
        if self._session_start is None:
            return 0.0
        return time.time() - self._session_start
