"""Farming panel — mode selector, big start button, live log."""

import customtkinter as ctk
from app.ui import theme as T

_MODES = ["Farm Greens", "Farm Rest", "Claim Daily"]
_MODE_KEYS = {"Farm Greens": "farm_greens", "Farm Rest": "farm_rest", "Claim Daily": "claim_daily"}


class FarmingPanel(ctk.CTkFrame):

    def __init__(self, parent, on_start, on_stop, on_pause):
        super().__init__(parent, fg_color=T.BG_PRIMARY, corner_radius=0)
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_pause = on_pause
        self._selected_mode = "farm_greens"
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self._build()

    def _build(self) -> None:
        # Title
        ctk.CTkLabel(self, text="Farming", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(
            row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        ctk.CTkLabel(self, text="Configure and launch your farming session",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY).grid(
            row=1, column=0, padx=24, pady=(0, 20), sticky="w")

        # Mode selector
        mode_frame = ctk.CTkFrame(self, fg_color=T.BG_CARD, corner_radius=12)
        mode_frame.grid(row=2, column=0, padx=24, sticky="ew", pady=(0, 16))
        mode_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(mode_frame, text="Mode", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")

        self._seg = ctk.CTkSegmentedButton(
            mode_frame, values=_MODES,
            font=ctk.CTkFont(size=12),
            command=self._on_mode_change,
        )
        self._seg.set(_MODES[0])
        self._seg.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")

        # Controls row
        ctrl_frame = ctk.CTkFrame(self, fg_color=T.BG_CARD, corner_radius=12)
        ctrl_frame.grid(row=3, column=0, padx=24, sticky="ew", pady=(0, 16))
        ctrl_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._start_btn = ctk.CTkButton(
            ctrl_frame, text="▶  Start Farming",
            height=52, corner_radius=10,
            fg_color=T.ACCENT_GREEN, hover_color="#3da890",
            text_color="#fff", font=ctk.CTkFont(size=15, weight="bold"),
            command=self._handle_start,
        )
        self._start_btn.grid(row=0, column=0, padx=16, pady=16, sticky="ew")

        self._pause_btn = ctk.CTkButton(
            ctrl_frame, text="⏸  Pause",
            height=52, corner_radius=10,
            fg_color=T.ACCENT_ORANGE, hover_color="#c88000",
            text_color="#fff", font=ctk.CTkFont(size=14),
            command=self._on_pause, state="disabled",
        )
        self._pause_btn.grid(row=0, column=1, padx=4, pady=16, sticky="ew")

        self._stop_btn = ctk.CTkButton(
            ctrl_frame, text="■  Stop",
            height=52, corner_radius=10,
            fg_color=T.ACCENT_RED, hover_color="#c03030",
            text_color="#fff", font=ctk.CTkFont(size=14),
            command=self._on_stop, state="disabled",
        )
        self._stop_btn.grid(row=0, column=2, padx=(4, 16), pady=16, sticky="ew")

        # Status row
        status_frame = ctk.CTkFrame(self, fg_color=T.BG_CARD, corner_radius=12)
        status_frame.grid(row=4, column=0, padx=24, sticky="ew", pady=(0, 16))
        status_frame.grid_columnconfigure(0, weight=1)

        self._cycle_label = ctk.CTkLabel(
            status_frame, text="Ready to start",
            font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY,
        )
        self._cycle_label.grid(row=0, column=0, padx=16, pady=10, sticky="w")

        # Live log
        log_frame = ctk.CTkFrame(self, fg_color=T.BG_CARD, corner_radius=12)
        log_frame.grid(row=5, column=0, padx=24, pady=(0, 24), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="ew")
        log_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_header, text="Live Log", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            log_header, text="Clear", width=56, height=24,
            fg_color=T.BG_SECONDARY, hover_color=T.NAV_HOVER,
            text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=11),
            command=self._clear_log,
        ).grid(row=0, column=1, sticky="e")

        self._log_box = ctk.CTkTextbox(
            log_frame, font=ctk.CTkFont(family="Consolas" if __import__("sys").platform=="win32" else "Monaco", size=11),
            fg_color=T.BG_SECONDARY, text_color=T.TEXT_PRIMARY, state="disabled",
        )
        self._log_box.grid(row=1, column=0, padx=8, pady=(0, 12), sticky="nsew")
        # Tag colours
        self._log_box._textbox.tag_config("info",    foreground=T.LOG_INFO)
        self._log_box._textbox.tag_config("warning", foreground=T.LOG_WARNING)
        self._log_box._textbox.tag_config("error",   foreground=T.LOG_ERROR)
        self._log_box._textbox.tag_config("success", foreground=T.LOG_SUCCESS)
        self._log_box._textbox.tag_config("debug",   foreground=T.LOG_DEBUG)

    # ── Handlers ─────────────────────────────────────────────────────

    def _on_mode_change(self, value: str) -> None:
        self._selected_mode = _MODE_KEYS.get(value, "farm_greens")

    def _handle_start(self) -> None:
        self._on_start(self._selected_mode)

    def _clear_log(self) -> None:
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    # ── Public update methods ─────────────────────────────────────────

    def append_log(self, message: str, level: str = "info") -> None:
        self._log_box.configure(state="normal")
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        tag = level if level in ("info", "warning", "error", "success", "debug") else "info"
        self._log_box._textbox.insert("end", f"[{ts}] {message}\n", tag)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def update_cycle_status(self, cycle: int, next_in: int) -> None:
        self._cycle_label.configure(text=f"Cycle {cycle} · Next in {next_in}s")

    def update_bot_state(self, status: str) -> None:
        running = status == "running"
        paused = status == "paused"
        active = running or paused

        self._start_btn.configure(state="disabled" if active else "normal")
        self._stop_btn.configure(state="normal" if active else "disabled")
        self._pause_btn.configure(
            state="normal" if active else "disabled",
            text="▶  Resume" if paused else "⏸  Pause",
        )
        if not active:
            self._cycle_label.configure(text="Ready to start")
