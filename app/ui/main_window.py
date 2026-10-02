"""MainWindow — CustomTkinter root with sidebar + content frame + event pump."""

import queue
import time
import customtkinter as ctk

from app.ui import theme as T
from app.ui.components.sidebar import Sidebar
from app.ui.components.dashboard import DashboardPanel
from app.ui.components.farming_panel import FarmingPanel
from app.ui.components.settings_panel import SettingsPanel
from app.ui.components.debug_panel import DebugPanel
from app.ui.components.overlay import OverlayWindow
from app.bot.controller import BotController
from app.data.session_store import SessionStore
from app.data.debug_store import DebugStore


class MainWindow(ctk.CTk):

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()

        self.title("TopEleven Bot")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=T.BG_PRIMARY)

        self._eq: queue.Queue = queue.Queue(maxsize=500)
        self._controller = BotController(self._eq)
        self._session_store = SessionStore()
        self._debug_store = DebugStore()
        self._overlay: OverlayWindow | None = None
        self._session_start: float | None = None
        self._cycle_count = 0

        self._controller.initialize()

        self._build()
        self._bind_hotkeys()
        self._refresh_dashboard()
        self.after(100, self._poll_events)

    # ── Layout ────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._sidebar = Sidebar(
            self,
            on_navigate=self._navigate,
            on_start=self._start_bot,
            on_stop=self._stop_bot,
            on_pause=self._pause_bot,
            on_toggle_overlay=self._toggle_overlay,
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        content = ctk.CTkFrame(self, fg_color=T.BG_PRIMARY, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        config = self._controller.config

        self._panels: dict[str, ctk.CTkFrame] = {
            "dashboard": DashboardPanel(content),
            "farming":   FarmingPanel(content,
                                      on_start=self._start_bot,
                                      on_stop=self._stop_bot,
                                      on_pause=self._pause_bot),
            "settings":  SettingsPanel(content, config=config, on_save=self._on_settings_saved),
            "debug":     DebugPanel(content, debug_store=self._debug_store, config=config),
        }

        for panel in self._panels.values():
            panel.grid(row=0, column=0, sticky="nsew")

        self._navigate("dashboard")

    def _bind_hotkeys(self) -> None:
        self.bind("<Control-Shift-O>", lambda e: self._toggle_overlay())
        self.bind("<Control-s>", lambda e: self._stop_bot())

    # ── Navigation ───────────────────────────────────────────────────

    def _navigate(self, page: str) -> None:
        for key, panel in self._panels.items():
            if key == page:
                panel.tkraise()
            else:
                panel.lower()
        if page == "debug":
            self._panels["debug"].refresh_detection_log()
            self._panels["debug"].refresh_gallery()
            self._panels["debug"].refresh_perf()

    # ── Bot control ──────────────────────────────────────────────────

    def _start_bot(self, mode: str = "farm_greens") -> None:
        self._session_start = time.time()
        self._cycle_count = 0
        self._controller.start(mode)

    def _stop_bot(self) -> None:
        self._controller.stop()
        self._session_start = None
        self._refresh_dashboard()

    def _pause_bot(self) -> None:
        if self._controller.status == "paused":
            self._controller.resume()
        else:
            self._controller.pause()

    def _on_settings_saved(self) -> None:
        pass  # config already written to disk by SettingsPanel

    # ── Overlay ──────────────────────────────────────────────────────

    def _toggle_overlay(self) -> None:
        if self._overlay is None or not self._overlay.winfo_exists():
            self._overlay = OverlayWindow(self, self._controller, self._eq)
        elif self._overlay.winfo_viewable():
            self._overlay.withdraw()
        else:
            self._overlay.deiconify()

    # ── Event pump (main-thread safe) ────────────────────────────────

    def _poll_events(self) -> None:
        try:
            while True:
                event = self._eq.get_nowait()
                self._dispatch(event)
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def _dispatch(self, event: dict) -> None:
        etype = event.get("type")

        if etype == "log":
            msg = event.get("message", "")
            level = event.get("level", "info")
            farming: FarmingPanel = self._panels["farming"]
            farming.append_log(msg, level)
            if level == "error":
                self._panels["debug"].append_error(msg)
            if self._overlay and self._overlay.winfo_exists():
                self._overlay.update_step(msg)

        elif etype == "status_change":
            status = event.get("status", "idle")
            self._sidebar.update_status(status)
            self._panels["farming"].update_bot_state(status)
            if self._overlay and self._overlay.winfo_exists():
                self._overlay.update_status(status)

        elif etype == "green_count":
            current = event.get("current", 0)
            maximum = event.get("maximum", 25)
            self._panels["dashboard"].update_greens(current, maximum)
            if self._overlay and self._overlay.winfo_exists():
                self._overlay.update_greens(current, maximum)

        elif etype == "cycle_complete":
            self._cycle_count = event.get("cycle", self._cycle_count)
            self._panels["dashboard"].update_cycles(self._cycle_count)

        elif etype == "next_cycle_in":
            secs = event.get("seconds", 0)
            self._panels["farming"].update_cycle_status(self._cycle_count, secs)
            if self._session_start:
                elapsed = time.time() - self._session_start
                self._panels["dashboard"].update_session_time(elapsed)

        elif etype == "error":
            msg = event.get("message", "Unknown error")
            self._panels["farming"].append_log(f"ERROR: {msg}", "error")
            self._panels["debug"].append_error(msg)

        elif etype == "detection":
            if self._debug_store and self._controller.config.debug_mode:
                self._debug_store.record(
                    class_name=event.get("class_name", ""),
                    confidence=event.get("confidence", 0.0),
                    found=event.get("found", False),
                    point=event.get("point"),
                    detection_method=event.get("method", "unknown"),
                    duration_ms=event.get("duration_ms", 0.0),
                    screenshot_path=event.get("screenshot_path"),
                )

    # ── Dashboard refresh ─────────────────────────────────────────────

    def _refresh_dashboard(self) -> None:
        try:
            today_greens = self._session_store.get_today_greens()
            max_greens = (self._controller.config.max_greens
                          if self._controller.config else 25)
            self._panels["dashboard"].update_greens(today_greens, max_greens)
            sessions = self._session_store.get_recent_sessions()
            self._panels["dashboard"].refresh_sessions(sessions)
        except Exception:
            pass
