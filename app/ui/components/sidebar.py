"""Sidebar navigation with status dot and quick Start/Stop."""

import customtkinter as ctk
from app.ui import theme as T


class Sidebar(ctk.CTkFrame):

    NAV_ITEMS = [
        ("Dashboard", "dashboard"),
        ("Farming",   "farming"),
        ("Settings",  "settings"),
        ("Debug",     "debug"),
    ]

    def __init__(self, parent, on_navigate, on_start, on_stop, on_pause, on_toggle_overlay):
        super().__init__(parent, width=190, fg_color=T.BG_SIDEBAR, corner_radius=0)
        self._on_navigate = on_navigate
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_pause = on_pause
        self._on_toggle_overlay = on_toggle_overlay
        self._active_page = "dashboard"
        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        self.grid_rowconfigure(5, weight=1)
        self._build()

    def _build(self) -> None:
        # Logo / header
        logo = ctk.CTkLabel(
            self, text="⚽ TopEleven Bot",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=T.TEXT_PRIMARY,
        )
        logo.grid(row=0, column=0, padx=16, pady=(20, 8), sticky="w")

        sep1 = ctk.CTkFrame(self, height=1, fg_color=T.BORDER_COLOR)
        sep1.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        # Nav buttons
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="ew", padx=8)
        nav_frame.grid_columnconfigure(0, weight=1)

        icons = {"dashboard": "📊", "farming": "🌿", "settings": "⚙️", "debug": "🔍"}
        for i, (label, key) in enumerate(self.NAV_ITEMS):
            btn = ctk.CTkButton(
                nav_frame,
                text=f" {icons.get(key, '')}  {label}",
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color=T.NAV_ACTIVE if key == self._active_page else T.NAV_INACTIVE,
                hover_color=T.NAV_HOVER,
                text_color=T.TEXT_PRIMARY,
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self._navigate(k),
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_buttons[key] = btn

        # Spacer
        ctk.CTkFrame(self, fg_color="transparent").grid(row=5, column=0, sticky="nsew")

        # Overlay toggle
        overlay_btn = ctk.CTkButton(
            self,
            text="  👁  Overlay",
            anchor="w",
            height=34,
            corner_radius=8,
            fg_color=T.NAV_INACTIVE,
            hover_color=T.NAV_HOVER,
            text_color=T.TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
            command=self._on_toggle_overlay,
        )
        overlay_btn.grid(row=6, column=0, sticky="ew", padx=8, pady=2)

        sep2 = ctk.CTkFrame(self, height=1, fg_color=T.BORDER_COLOR)
        sep2.grid(row=7, column=0, sticky="ew", padx=12, pady=8)

        # Status indicator
        self._status_label = ctk.CTkLabel(
            self, text="◌ Idle",
            font=ctk.CTkFont(size=12),
            text_color=T.STATUS_IDLE,
        )
        self._status_label.grid(row=8, column=0, padx=16, pady=(0, 6), sticky="w")

        # Start / Stop / Pause
        self._start_btn = ctk.CTkButton(
            self, text="▶  Start",
            height=40, corner_radius=8,
            fg_color=T.ACCENT_GREEN, hover_color="#3da890",
            text_color="#fff", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_start,
        )
        self._start_btn.grid(row=9, column=0, padx=8, pady=(0, 4), sticky="ew")

        self._pause_btn = ctk.CTkButton(
            self, text="⏸  Pause",
            height=34, corner_radius=8,
            fg_color=T.ACCENT_ORANGE, hover_color="#c88000",
            text_color="#fff", font=ctk.CTkFont(size=12),
            command=self._on_pause, state="disabled",
        )
        self._pause_btn.grid(row=10, column=0, padx=8, pady=(0, 4), sticky="ew")

        self._stop_btn = ctk.CTkButton(
            self, text="■  Stop",
            height=34, corner_radius=8,
            fg_color=T.ACCENT_RED, hover_color="#c03030",
            text_color="#fff", font=ctk.CTkFont(size=12),
            command=self._on_stop, state="disabled",
        )
        self._stop_btn.grid(row=11, column=0, padx=8, pady=(0, 20), sticky="ew")

        self.grid_columnconfigure(0, weight=1)

    def _navigate(self, key: str) -> None:
        if key == self._active_page:
            return
        old = self._nav_buttons.get(self._active_page)
        if old:
            old.configure(fg_color=T.NAV_INACTIVE)
        self._nav_buttons[key].configure(fg_color=T.NAV_ACTIVE)
        self._active_page = key
        self._on_navigate(key)

    def update_status(self, status: str) -> None:
        label = T.STATUS_LABELS.get(status, status)
        color = T.STATUS_COLORS.get(status, T.TEXT_MUTED)
        self._status_label.configure(text=label, text_color=color)

        running = status == "running"
        paused = status == "paused"
        active = running or paused

        self._start_btn.configure(state="disabled" if active else "normal")
        self._stop_btn.configure(state="normal" if active else "disabled")
        self._pause_btn.configure(
            state="normal" if active else "disabled",
            text="▶  Resume" if paused else "⏸  Pause",
        )
