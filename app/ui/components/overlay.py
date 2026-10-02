"""Semi-transparent always-on-top overlay — edge-hugging HUD."""

import customtkinter as ctk
from app.ui import theme as T


class OverlayWindow(ctk.CTkToplevel):
    """A minimal, draggable, edge-snapping HUD for watching the bot work."""

    _W = 230
    _H_FULL = 190
    _H_COLLAPSED = 42

    def __init__(self, parent, controller, event_queue):
        super().__init__(parent)
        self._controller = controller
        self._eq = event_queue
        self._collapsed = False
        self._drag_x = 0
        self._drag_y = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.88)
        self.configure(bg="#1a1a2e")

        sw = self.winfo_screenwidth()
        self.geometry(f"{self._W}x{self._H_FULL}+{sw - self._W - 10}+20")

        self._build()
        self._bind_drag()

    # ── Build ─────────────────────────────────────────────────────────

    def _build(self) -> None:
        self._root_frame = ctk.CTkFrame(self, fg_color=T.BG_SIDEBAR, corner_radius=12)
        self._root_frame.pack(fill="both", expand=True, padx=2, pady=2)
        self._root_frame.grid_columnconfigure(0, weight=1)

        # Drag bar
        drag_bar = ctk.CTkFrame(self._root_frame, fg_color=T.BG_CARD, corner_radius=8, height=34)
        drag_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 0))
        drag_bar.grid_columnconfigure(0, weight=1)
        drag_bar.grid_propagate(False)

        ctk.CTkLabel(drag_bar, text="⚽ TopEleven Bot",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(row=0, column=0, padx=10, sticky="w")

        btn_frame = ctk.CTkFrame(drag_bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(0, 4), sticky="e")

        self._collapse_btn = ctk.CTkButton(
            btn_frame, text="−", width=22, height=22, corner_radius=4,
            fg_color=T.BG_SECONDARY, hover_color=T.NAV_HOVER,
            text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=13),
            command=self._toggle_collapse,
        )
        self._collapse_btn.pack(side="left", padx=1)

        ctk.CTkButton(
            btn_frame, text="✕", width=22, height=22, corner_radius=4,
            fg_color=T.BG_SECONDARY, hover_color=T.ACCENT_RED,
            text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=11),
            command=self.close,
        ).pack(side="left", padx=1)

        drag_bar.bind("<ButtonPress-1>", self._on_drag_start)
        drag_bar.bind("<B1-Motion>", self._on_drag_move)
        drag_bar.bind("<ButtonRelease-1>", self._on_drag_release)

        # Body (hidden when collapsed)
        self._body = ctk.CTkFrame(self._root_frame, fg_color="transparent")
        self._body.grid(row=1, column=0, sticky="ew", padx=6, pady=4)
        self._body.grid_columnconfigure(0, weight=1)

        # Status
        self._status_lbl = ctk.CTkLabel(
            self._body, text="● Idle",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=T.STATUS_IDLE,
        )
        self._status_lbl.grid(row=0, column=0, sticky="w", padx=6, pady=(4, 2))

        # Greens progress
        prog_row = ctk.CTkFrame(self._body, fg_color="transparent")
        prog_row.grid(row=1, column=0, sticky="ew", padx=6)
        prog_row.grid_columnconfigure(0, weight=1)

        self._prog_bar = ctk.CTkProgressBar(
            prog_row, height=8, corner_radius=4,
            fg_color=T.BG_SECONDARY, progress_color=T.ACCENT_GREEN,
        )
        self._prog_bar.set(0)
        self._prog_bar.grid(row=0, column=0, sticky="ew")

        self._prog_lbl = ctk.CTkLabel(
            prog_row, text="0/25", font=ctk.CTkFont(size=10),
            text_color=T.ACCENT_GREEN, width=36, anchor="e",
        )
        self._prog_lbl.grid(row=0, column=1, padx=(4, 0))

        # Step label
        self._step_lbl = ctk.CTkLabel(
            self._body, text="—",
            font=ctk.CTkFont(size=10), text_color=T.TEXT_SECONDARY,
        )
        self._step_lbl.grid(row=2, column=0, sticky="w", padx=6, pady=(2, 6))

        # Separator
        ctk.CTkFrame(self._body, height=1, fg_color=T.BORDER_COLOR).grid(
            row=3, column=0, sticky="ew", padx=4, pady=2)

        # Pause / Stop row
        btn_row = ctk.CTkFrame(self._body, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="ew", padx=4, pady=4)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self._pause_btn = ctk.CTkButton(
            btn_row, text="⏸", height=30, corner_radius=6,
            fg_color=T.ACCENT_ORANGE, hover_color="#c88000",
            text_color="#fff", font=ctk.CTkFont(size=12),
            command=self._handle_pause, state="disabled",
        )
        self._pause_btn.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        self._stop_btn = ctk.CTkButton(
            btn_row, text="■", height=30, corner_radius=6,
            fg_color=T.ACCENT_RED, hover_color="#c03030",
            text_color="#fff", font=ctk.CTkFont(size=12),
            command=self._handle_stop, state="disabled",
        )
        self._stop_btn.grid(row=0, column=1, padx=(2, 0), sticky="ew")

        # Opacity slider (at bottom)
        opacity_row = ctk.CTkFrame(self._body, fg_color="transparent")
        opacity_row.grid(row=5, column=0, sticky="ew", padx=4, pady=(2, 4))
        opacity_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(opacity_row, text="Opacity", font=ctk.CTkFont(size=9),
                     text_color=T.TEXT_MUTED).grid(row=0, column=0, padx=(2, 4))
        ctk.CTkSlider(
            opacity_row, from_=0.3, to=1.0,
            number_of_steps=14,
            command=lambda v: self.attributes("-alpha", float(v)),
        ).grid(row=0, column=1, sticky="ew")

    # ── Drag ─────────────────────────────────────────────────────────

    def _bind_drag(self) -> None:
        pass  # drag is bound to drag_bar only (above)

    def _on_drag_start(self, e) -> None:
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _on_drag_move(self, e) -> None:
        x = e.x_root - self._drag_x
        y = e.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _on_drag_release(self, e) -> None:
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        cx = self.winfo_x() + self._W // 2
        cy = self.winfo_y() + self._H_FULL // 2

        # Snap to nearest edge
        dists = {
            "left": cx,
            "right": sw - cx,
            "top": cy,
            "bottom": sh - cy,
        }
        edge = min(dists, key=dists.get)
        margin = 10
        h = self._H_COLLAPSED if self._collapsed else self._H_FULL
        if edge == "left":
            nx, ny = margin, self.winfo_y()
        elif edge == "right":
            nx, ny = sw - self._W - margin, self.winfo_y()
        elif edge == "top":
            nx, ny = self.winfo_x(), margin
        else:
            nx, ny = self.winfo_x(), sh - h - margin
        self.geometry(f"+{nx}+{ny}")

    # ── Collapse ─────────────────────────────────────────────────────

    def _toggle_collapse(self) -> None:
        self._collapsed = not self._collapsed
        if self._collapsed:
            self._body.grid_remove()
            self.geometry(f"{self._W}x{self._H_COLLAPSED}")
            self._collapse_btn.configure(text="+")
        else:
            self._body.grid()
            self.geometry(f"{self._W}x{self._H_FULL}")
            self._collapse_btn.configure(text="−")

    # ── Controller callbacks ─────────────────────────────────────────

    def _handle_pause(self) -> None:
        if self._controller.status == "paused":
            self._controller.resume()
        else:
            self._controller.pause()

    def _handle_stop(self) -> None:
        self._controller.stop()

    def close(self) -> None:
        self.withdraw()

    # ── Event-driven updates ─────────────────────────────────────────

    def update_status(self, status: str) -> None:
        label = T.STATUS_LABELS.get(status, status)
        color = T.STATUS_COLORS.get(status, T.TEXT_MUTED)
        self._status_lbl.configure(text=label, text_color=color)

        active = status in ("running", "paused")
        self._stop_btn.configure(state="normal" if active else "disabled")
        self._pause_btn.configure(
            state="normal" if active else "disabled",
            text="▶" if status == "paused" else "⏸",
        )

    def update_greens(self, current: int, maximum: int) -> None:
        frac = current / maximum if maximum > 0 else 0
        self._prog_bar.set(frac)
        self._prog_lbl.configure(text=f"{current}/{maximum}")

    def update_step(self, message: str) -> None:
        # Truncate to fit overlay width
        self._step_lbl.configure(text=message[:34] + "…" if len(message) > 34 else message)
