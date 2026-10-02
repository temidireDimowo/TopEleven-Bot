"""Settings panel — editable config backed by BotConfig."""

import tkinter.filedialog as fd
import customtkinter as ctk
from app.ui import theme as T


class SettingsPanel(ctk.CTkFrame):

    def __init__(self, parent, config, on_save):
        super().__init__(parent, fg_color=T.BG_PRIMARY, corner_radius=0)
        self._config = config
        self._on_save = on_save
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._vars: dict = {}
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=T.TEXT_PRIMARY).grid(
            row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        ctk.CTkLabel(self, text="Bot configuration — changes apply on next session start",
                     font=ctk.CTkFont(size=12), text_color=T.TEXT_SECONDARY).grid(
            row=1, column=0, padx=24, pady=(0, 16), sticky="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.grid(row=2, column=0, padx=24, sticky="nsew", pady=(0, 0))
        scroll.grid_columnconfigure(0, weight=1)

        row = 0

        # ── Detection ─────────────────────────────────────────────
        row = self._section(scroll, "Detection", row)

        row = self._switch(scroll, "yolo_enabled", "Use YOLO detection", row)
        row = self._switch(scroll, "fallback_to_traditional", "Fallback to template matching", row)
        row = self._slider(scroll, "yolo_confidence", "Confidence threshold", 0.1, 1.0, row)
        row = self._file_entry(scroll, "yolo_model_path", "YOLO model path (.pt)", row)

        # ── Timing ────────────────────────────────────────────────
        row = self._section(scroll, "Timing", row)

        row = self._entry(scroll, "ad_wait_timeout", "Ad wait timeout (s)", row)
        row = self._entry(scroll, "cycle_interval", "Cycle interval (s)", row)
        row = self._entry(scroll, "max_greens", "Max greens per session", row)
        row = self._slider(scroll, "move_duration", "Mouse move duration (s)", 0.05, 1.0, row)

        # ── Input ─────────────────────────────────────────────────
        row = self._section(scroll, "Input & Paths", row)

        row = self._entry(scroll, "images_dir", "Assets directory", row)
        row = self._entry(scroll, "log_dir", "Log directory", row)
        row = self._entry(scroll, "screenshot_dir", "Screenshot directory", row)

        # ── Debug ─────────────────────────────────────────────────
        row = self._section(scroll, "Debug", row)

        row = self._switch(scroll, "debug_mode", "Debug mode", row)
        row = self._switch(scroll, "save_annotated_on_failure", "Save annotated screenshots on failure", row)
        row = self._switch(scroll, "screenshot_on_cycle_start", "Screenshot on each cycle start", row)
        row = self._entry(scroll, "detection_log_max_entries", "Max detection log entries", row)

        # Save button
        save_btn = ctk.CTkButton(
            scroll, text="💾  Save Settings",
            height=42, corner_radius=10,
            fg_color=T.ACCENT_BLUE, hover_color="#2a7fd0",
            text_color="#fff", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save,
        )
        save_btn.grid(row=row, column=0, padx=0, pady=(16, 24), sticky="ew")

    # ── Widget helpers ────────────────────────────────────────────────

    def _section(self, parent, title: str, row: int) -> int:
        ctk.CTkLabel(parent, text=title,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=T.ACCENT_BLUE).grid(
            row=row, column=0, pady=(16, 4), sticky="w")
        sep = ctk.CTkFrame(parent, height=1, fg_color=T.BORDER_COLOR)
        sep.grid(row=row + 1, column=0, sticky="ew", pady=(0, 8))
        return row + 2

    def _switch(self, parent, key: str, label: str, row: int) -> int:
        val = getattr(self._config, key, False)
        var = ctk.BooleanVar(value=bool(val))
        self._vars[key] = var
        frame = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=8)
        frame.grid(row=row, column=0, sticky="ew", pady=3)
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12),
                     text_color=T.TEXT_PRIMARY).grid(row=0, column=0, padx=14, pady=10, sticky="w")
        ctk.CTkSwitch(frame, text="", variable=var, onvalue=True, offvalue=False,
                      progress_color=T.ACCENT_GREEN).grid(row=0, column=1, padx=14, sticky="e")
        return row + 1

    def _slider(self, parent, key: str, label: str, from_: float, to: float, row: int) -> int:
        val = float(getattr(self._config, key, from_))
        var = ctk.DoubleVar(value=val)
        self._vars[key] = var
        frame = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=8)
        frame.grid(row=row, column=0, sticky="ew", pady=3)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12),
                     text_color=T.TEXT_PRIMARY).grid(row=0, column=0, padx=14, pady=10, sticky="w")
        val_lbl = ctk.CTkLabel(frame, text=f"{val:.2f}", font=ctk.CTkFont(size=11),
                               text_color=T.TEXT_SECONDARY, width=40)
        val_lbl.grid(row=0, column=2, padx=(4, 14))

        def on_slide(v):
            val_lbl.configure(text=f"{float(v):.2f}")

        ctk.CTkSlider(frame, from_=from_, to=to, variable=var, command=on_slide,
                      progress_color=T.ACCENT_BLUE).grid(row=0, column=1, padx=4, sticky="ew")
        return row + 1

    def _entry(self, parent, key: str, label: str, row: int) -> int:
        val = str(getattr(self._config, key, ""))
        var = ctk.StringVar(value=val)
        self._vars[key] = var
        frame = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=8)
        frame.grid(row=row, column=0, sticky="ew", pady=3)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12),
                     text_color=T.TEXT_PRIMARY, width=210, anchor="w").grid(
            row=0, column=0, padx=14, pady=10)
        ctk.CTkEntry(frame, textvariable=var, font=ctk.CTkFont(size=11),
                     fg_color=T.BG_SECONDARY, border_color=T.BORDER_COLOR).grid(
            row=0, column=1, padx=(4, 14), sticky="ew")
        return row + 1

    def _file_entry(self, parent, key: str, label: str, row: int) -> int:
        val = str(getattr(self._config, key, ""))
        var = ctk.StringVar(value=val)
        self._vars[key] = var
        frame = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=8)
        frame.grid(row=row, column=0, sticky="ew", pady=3)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12),
                     text_color=T.TEXT_PRIMARY, width=180, anchor="w").grid(
            row=0, column=0, padx=14, pady=10)
        ctk.CTkEntry(frame, textvariable=var, font=ctk.CTkFont(size=11),
                     fg_color=T.BG_SECONDARY, border_color=T.BORDER_COLOR).grid(
            row=0, column=1, padx=4, sticky="ew")
        ctk.CTkButton(
            frame, text="Browse…", width=70, height=28,
            fg_color=T.BG_SECONDARY, hover_color=T.NAV_HOVER,
            text_color=T.TEXT_SECONDARY, font=ctk.CTkFont(size=11),
            command=lambda v=var: self._browse(v),
        ).grid(row=0, column=2, padx=(0, 14))
        return row + 1

    def _browse(self, var: ctk.StringVar) -> None:
        path = fd.askopenfilename(filetypes=[("Model files", "*.pt"), ("All files", "*.*")])
        if path:
            var.set(path)

    # ── Save ─────────────────────────────────────────────────────────

    def _save(self) -> None:
        for key, var in self._vars.items():
            raw = var.get()
            field_type = type(getattr(self._config, key, ""))
            try:
                if field_type == bool:
                    setattr(self._config, key, bool(raw))
                elif field_type == int:
                    setattr(self._config, key, int(float(raw)))
                elif field_type == float:
                    setattr(self._config, key, float(raw))
                else:
                    setattr(self._config, key, str(raw))
            except (ValueError, TypeError):
                pass
        self._config.to_json("config.json")
        self._on_save()
