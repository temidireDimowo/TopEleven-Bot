"""Debug panel — detection log, screenshot gallery, performance metrics, error console."""

import os
import tkinter as tk
import customtkinter as ctk
from pathlib import Path
from app.ui import theme as T


class DebugPanel(ctk.CTkFrame):

    def __init__(self, parent, debug_store, config):
        super().__init__(parent, fg_color=T.BG_PRIMARY, corner_radius=0)
        self._store = debug_store
        self._config = config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Debug", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(
            row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        ctk.CTkLabel(self, text="Detection events, screenshots, performance metrics",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY).grid(
            row=1, column=0, padx=24, pady=(0, 12), sticky="w")

        tabs = ctk.CTkTabview(self, fg_color=T.BG_CARD, corner_radius=12)
        tabs.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")

        t_log = tabs.add("Detection Log")
        t_gallery = tabs.add("Screenshots")
        t_perf = tabs.add("Performance")
        t_errors = tabs.add("Errors")

        self._build_detection_log(t_log)
        self._build_gallery(t_gallery)
        self._build_perf(t_perf)
        self._build_errors(t_errors)

    # ── Detection Log ─────────────────────────────────────────────────

    def _build_detection_log(self, parent) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(8, 4))
        toolbar.grid_columnconfigure(0, weight=1)

        self._det_stats_lbl = ctk.CTkLabel(
            toolbar, text="Loaded 0 events",
            font=ctk.CTkFont(size=11), text_color=T.TEXT_SECONDARY,
        )
        self._det_stats_lbl.grid(row=0, column=0, padx=8, sticky="w")

        ctk.CTkButton(
            toolbar, text="Refresh", width=80, height=28,
            fg_color=T.ACCENT_BLUE, hover_color="#2a7fd0",
            text_color="#fff", font=ctk.CTkFont(size=11),
            command=self.refresh_detection_log,
        ).grid(row=0, column=1, padx=(4, 0))

        ctk.CTkButton(
            toolbar, text="Clear", width=64, height=28,
            fg_color=T.BG_SECONDARY, hover_color=T.NAV_HOVER,
            text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=11),
            command=self._clear_detection_log,
        ).grid(row=0, column=2, padx=(4, 8))

        self._log_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=T.BG_SECONDARY, corner_radius=8,
        )
        self._log_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 8))
        self._log_scroll.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Time", "Class", "Conf", "Found", "Method"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self._log_scroll, text=h, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=T.TEXT_SECONDARY).grid(row=0, column=col, padx=6, pady=4, sticky="w")

    def refresh_detection_log(self) -> None:
        if self._store is None:
            return
        for w in self._log_scroll.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()

        events = self._store.get_recent(limit=self._config.detection_log_max_entries)
        stats = self._store.get_stats()
        self._det_stats_lbl.configure(
            text=f"{stats['total']} events · {stats['success_rate']}% found · avg {stats['avg_latency_ms']}ms"
        )

        for i, ev in enumerate(events, start=1):
            color = T.LOG_SUCCESS if ev.found else T.LOG_ERROR
            ts = ev.timestamp[11:19] if len(ev.timestamp) > 10 else ev.timestamp
            vals = [ts, ev.class_name, f"{ev.confidence:.2f}", "✓" if ev.found else "✗", ev.detection_method]
            for col, val in enumerate(vals):
                ctk.CTkLabel(self._log_scroll, text=val, font=ctk.CTkFont(size=10),
                             text_color=color).grid(row=i, column=col, padx=6, pady=1, sticky="w")

    def _clear_detection_log(self) -> None:
        if self._store:
            self._store.clear()
        self.refresh_detection_log()

    # ── Screenshot Gallery ────────────────────────────────────────────

    def _build_gallery(self, parent) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(8, 4))
        toolbar.grid_columnconfigure(0, weight=1)

        self._gallery_count_lbl = ctk.CTkLabel(
            toolbar, text="0 screenshots",
            font=ctk.CTkFont(size=11), text_color=T.TEXT_SECONDARY,
        )
        self._gallery_count_lbl.grid(row=0, column=0, padx=8, sticky="w")

        ctk.CTkButton(
            toolbar, text="Refresh", width=80, height=28,
            fg_color=T.ACCENT_BLUE, hover_color="#2a7fd0",
            text_color="#fff", font=ctk.CTkFont(size=11),
            command=self.refresh_gallery,
        ).grid(row=0, column=1, padx=(4, 0))

        ctk.CTkButton(
            toolbar, text="Delete All", width=80, height=28,
            fg_color=T.ACCENT_RED, hover_color="#c03030",
            text_color="#fff", font=ctk.CTkFont(size=11),
            command=self._delete_all_screenshots,
        ).grid(row=0, column=2, padx=(4, 8))

        self._gallery_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=T.BG_SECONDARY, corner_radius=8,
        )
        self._gallery_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 8))
        self._gallery_scroll.grid_columnconfigure(0, weight=1)

    def refresh_gallery(self) -> None:
        for w in self._gallery_scroll.winfo_children():
            w.destroy()

        screenshots_dir = Path(self._config.screenshot_dir)
        if not screenshots_dir.exists():
            return

        files = sorted(screenshots_dir.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
        self._gallery_count_lbl.configure(text=f"{len(files)} screenshots")

        for i, f in enumerate(files):
            row_frame = ctk.CTkFrame(self._gallery_scroll, fg_color=T.BG_CARD, corner_radius=6)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            row_frame.grid_columnconfigure(0, weight=1)

            size_kb = f.stat().st_size // 1024
            ctk.CTkLabel(row_frame, text=f.name, font=ctk.CTkFont(size=10),
                         text_color=T.TEXT_PRIMARY, anchor="w").grid(
                row=0, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(row_frame, text=f"{size_kb} KB", font=ctk.CTkFont(size=10),
                         text_color=T.TEXT_MUTED).grid(row=0, column=1, padx=10, sticky="e")

    def _delete_all_screenshots(self) -> None:
        screenshots_dir = Path(self._config.screenshot_dir)
        if screenshots_dir.exists():
            for f in screenshots_dir.glob("*.png"):
                try:
                    f.unlink()
                except Exception:
                    pass
        self.refresh_gallery()

    # ── Performance ───────────────────────────────────────────────────

    def _build_perf(self, parent) -> None:
        parent.grid_columnconfigure((0, 1), weight=1)
        parent.grid_rowconfigure(1, weight=1)

        self._perf_stats: dict[str, ctk.CTkLabel] = {}
        perf_items = [
            ("avg_latency_ms", "Avg Detection Latency", "—"),
            ("success_rate",   "Detection Success Rate", "—"),
            ("total",          "Total Detections",       "0"),
            ("found",          "Elements Found",         "0"),
        ]
        for i, (key, label, default) in enumerate(perf_items):
            col = i % 2
            row = i // 2
            tile = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=10)
            tile.grid(row=row, column=col, padx=(0 if col else 0, 4 if col == 0 else 0),
                      pady=4, sticky="ew", padx=(0 if col else 4, 4 if col == 0 else 0))
            val_lbl = ctk.CTkLabel(tile, text=default,
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color=T.TEXT_PRIMARY)
            val_lbl.pack(pady=(16, 2))
            ctk.CTkLabel(tile, text=label, font=ctk.CTkFont(size=11),
                         text_color=T.TEXT_SECONDARY).pack(pady=(0, 14))
            self._perf_stats[key] = val_lbl

        ctk.CTkButton(
            parent, text="Refresh Stats",
            height=36, corner_radius=8,
            fg_color=T.ACCENT_BLUE, hover_color="#2a7fd0",
            text_color="#fff", font=ctk.CTkFont(size=12),
            command=self.refresh_perf,
        ).grid(row=2, column=0, columnspan=2, pady=12, sticky="ew")

    def refresh_perf(self) -> None:
        if self._store is None:
            return
        stats = self._store.get_stats()
        self._perf_stats["avg_latency_ms"].configure(text=f"{stats['avg_latency_ms']}ms")
        self._perf_stats["success_rate"].configure(text=f"{stats['success_rate']}%")
        self._perf_stats["total"].configure(text=str(stats["total"]))
        self._perf_stats["found"].configure(text=str(stats["found"]))

    # ── Errors ───────────────────────────────────────────────────────

    def _build_errors(self, parent) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self._error_box = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Consolas" if os.name == "nt" else "Monaco", size=10),
            fg_color=T.BG_SECONDARY, text_color=T.LOG_ERROR, state="disabled",
        )
        self._error_box.grid(row=0, column=0, sticky="nsew", pady=(8, 4))

        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        toolbar.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            toolbar, text="Export Errors", width=120, height=30,
            fg_color=T.ACCENT_ORANGE, hover_color="#c88000",
            text_color="#fff", font=ctk.CTkFont(size=11),
            command=self._export_errors,
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            toolbar, text="Export Bundle", width=120, height=30,
            fg_color=T.ACCENT_BLUE, hover_color="#2a7fd0",
            text_color="#fff", font=ctk.CTkFont(size=11),
            command=self._export_bundle,
        ).grid(row=0, column=2)

    def append_error(self, message: str) -> None:
        self._error_box.configure(state="normal")
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._error_box._textbox.insert("end", f"[{ts}] {message}\n")
        self._error_box.see("end")
        self._error_box.configure(state="disabled")

    def _export_errors(self) -> None:
        import datetime
        today = datetime.date.today().isoformat()
        content = self._error_box._textbox.get("1.0", "end")
        path = f"logs/errors_{today}.txt"
        Path("logs").mkdir(exist_ok=True)
        with open(path, "w") as fh:
            fh.write(content)

    def _export_bundle(self) -> None:
        if self._store:
            bundle = self._store.export_bundle()
            self.append_error(f"[info] Bundle exported: {bundle}")
