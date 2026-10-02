"""Dashboard panel — greens progress, stat tiles, session history."""

import customtkinter as ctk
from app.ui import theme as T


def _stat_tile(parent, label: str, initial: str) -> tuple:
    """Returns (frame, value_label)."""
    frame = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=12)
    val = ctk.CTkLabel(frame, text=initial, font=ctk.CTkFont(size=28, weight="bold"),
                       text_color=T.TEXT_PRIMARY)
    val.pack(pady=(18, 2))
    ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                 text_color=T.TEXT_SECONDARY).pack(pady=(0, 16))
    return frame, val


class DashboardPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=T.BG_PRIMARY, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self._session_rows: list = []
        self._build()

    def _build(self) -> None:
        # Title
        ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(
            row=0, column=0, padx=24, pady=(24, 4), sticky="w")

        ctk.CTkLabel(self, text="Today's farming summary",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY).grid(
            row=1, column=0, padx=24, pady=(0, 20), sticky="w")

        # Greens progress card
        progress_card = ctk.CTkFrame(self, fg_color=T.BG_CARD, corner_radius=12)
        progress_card.grid(row=2, column=0, padx=24, sticky="ew", pady=(0, 16))
        progress_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(progress_card, text="Greens Today",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")

        self._progress_bar = ctk.CTkProgressBar(
            progress_card, height=14, corner_radius=7,
            fg_color=T.BG_SECONDARY, progress_color=T.ACCENT_GREEN,
        )
        self._progress_bar.set(0)
        self._progress_bar.grid(row=1, column=0, padx=16, sticky="ew", pady=(0, 6))

        self._progress_label = ctk.CTkLabel(
            progress_card, text="0 / 25 today",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=T.ACCENT_GREEN,
        )
        self._progress_label.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="e")

        # Stat tiles
        tiles_frame = ctk.CTkFrame(self, fg_color="transparent")
        tiles_frame.grid(row=3, column=0, padx=24, sticky="ew", pady=(0, 16))
        tiles_frame.grid_columnconfigure((0, 1, 2), weight=1)

        tile1, self._cycles_val = _stat_tile(tiles_frame, "Total Cycles", "0")
        tile1.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        tile2, self._time_val = _stat_tile(tiles_frame, "Session Time", "0:00")
        tile2.grid(row=0, column=1, padx=4, sticky="ew")

        tile3, self._detect_val = _stat_tile(tiles_frame, "Detection Mode", "Composite")
        tile3.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # History header
        ctk.CTkLabel(self, text="Recent Sessions",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(
            row=4, column=0, padx=24, pady=(4, 8), sticky="w")

        # History table container
        self._table_frame = ctk.CTkScrollableFrame(
            self, fg_color=T.BG_CARD, corner_radius=12, height=160,
        )
        self._table_frame.grid(row=5, column=0, padx=24, sticky="ew", pady=(0, 24))
        self._table_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._build_table_header()

    def _build_table_header(self) -> None:
        headers = ["Date", "Mode", "Greens", "Cycles", "Duration"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(
                self._table_frame, text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=T.TEXT_SECONDARY,
            ).grid(row=0, column=col, padx=8, pady=(8, 4), sticky="w")

    # ── Update helpers ────────────────────────────────────────────────

    def update_greens(self, current: int, maximum: int) -> None:
        frac = current / maximum if maximum > 0 else 0
        self._progress_bar.set(frac)
        self._progress_label.configure(text=f"{current} / {maximum} today")

    def update_cycles(self, cycles: int) -> None:
        self._cycles_val.configure(text=str(cycles))

    def update_session_time(self, elapsed_secs: float) -> None:
        mins = int(elapsed_secs) // 60
        secs = int(elapsed_secs) % 60
        self._time_val.configure(text=f"{mins}:{secs:02d}")

    def update_detection_mode(self, mode: str) -> None:
        self._detect_val.configure(text=mode)

    def refresh_sessions(self, sessions) -> None:
        for w in self._table_frame.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        for row_idx, sess in enumerate(sessions, start=1):
            started = sess.started_at[:10] if sess.started_at else "-"
            duration = "-"
            if sess.started_at and sess.ended_at:
                try:
                    from datetime import datetime
                    s = datetime.fromisoformat(sess.started_at)
                    e = datetime.fromisoformat(sess.ended_at)
                    d = int((e - s).total_seconds())
                    duration = f"{d//60}m {d%60}s"
                except Exception:
                    pass
            cols = [started, sess.mode, str(sess.greens_earned), str(sess.cycles_completed), duration]
            fg = T.TEXT_PRIMARY if row_idx % 2 == 1 else T.TEXT_SECONDARY
            for col, val in enumerate(cols):
                ctk.CTkLabel(
                    self._table_frame, text=val,
                    font=ctk.CTkFont(size=11), text_color=fg,
                ).grid(row=row_idx, column=col, padx=8, pady=2, sticky="w")
