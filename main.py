#!/usr/bin/env python3
"""
GUI-Only Game Automation Bot for Top Eleven BlueStacks with YOLO support.
Combined application with modern GUI interface.
"""

import sys
import time
import signal
import threading
import tkinter as tk
from tkinter import font, ttk
from tkinter.scrolledtext import ScrolledText
import datetime
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent))

from Modules.Bot.config import BotConfig, ClickType
from Modules.Bot.log import BotLogger
from Modules.bluestacks import BlueStacksBot
from Modules.farm_resources import ResourceFarmer


class SimpleBotController:
    """Controller for launch and farming functionalities with YOLO support."""

    def __init__(self, yolo_model_path: str = None):
        self.config = None
        self.logger = None
        self.bluestacks_bot = None
        self.resource_farmer = None
        self.running = False
        self.yolo_model_path = yolo_model_path

    def resolve_yolo_model_path(self):
        import os

        if self.yolo_model_path and Path(self.yolo_model_path).exists():
            return self.yolo_model_path

        if self.config:
            yolo_enabled = getattr(self.config, 'yolo_enabled', True)
            if not yolo_enabled:
                self.logger.info("YOLO disabled in config")
                return None

            config_path = getattr(self.config, 'yolo_model_path', None)
            if config_path and Path(config_path).exists():
                self.yolo_model_path = config_path
                return config_path
            elif config_path:
                self.logger.warning(f"Config path not found: {config_path}")

        env_path = os.getenv('YOLO_MODEL_PATH')
        if env_path and Path(env_path).exists():
            self.yolo_model_path = env_path
            return env_path

        for path in ["models/best.pt"]:
            if Path(path).exists():
                self.yolo_model_path = path
                self.logger.info("Yolo best.pt file validation found")
                return path

        self.yolo_model_path = None
        self.logger.error("Yolo best.pt file validation failed")
        return None

    def initialize(self) -> bool:
        try:
            self.config = BotConfig.from_json("config.json")
            bot_logger = BotLogger(self.config)
            self.logger = bot_logger.setup_logging()

            if not self.config.validate():
                self.logger.error("Configuration validation failed")
                return False

            self.logger.info("Configuration loaded")

            resolved_path = self.resolve_yolo_model_path()
            if resolved_path:
                self.logger.info(f"YOLO model: {resolved_path}")
            else:
                self.logger.warning("YOLO model not found, using fallback method")

            self.bluestacks_bot = BlueStacksBot(self.config, self.logger)

            try:
                self.resource_farmer = ResourceFarmer(self.config, self.logger, model_path=self.yolo_model_path)
                detection_info = self.resource_farmer.get_detection_info()
                self.logger.info(f"Detection method: {detection_info['detection_method']}")
                if detection_info.get('model_info'):
                    classes = detection_info['model_info']['class_names']
                    self.logger.info(f"Model classes: {list(classes.values())}")
            except Exception as e:
                self.logger.error(f"ResourceFarmer init error: {e}")
                return False

            self.logger.info("Modules initialized")
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Initialization error: {e}")
            else:
                print(f"Initialization error: {e}")
            return False

    def launch_top_eleven(self) -> bool:
        self.logger.info("Launching Top Eleven on BlueStacks...")
        try:
            self.bluestacks_bot.optimize_for_bluestacks()
            result = self.bluestacks_bot.open_top_eleven_app()
            if result and self.bluestacks_bot.wait_for_bluestacks_ready(timeout=120):
                time.sleep(5)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Launch error: {e}")
            return False

    def start_resource_farming(self) -> None:
        self.logger.info("Starting resource farming...")
        try:
            # self.resource_farmer.start_farming()
            from Modules.Bot.input_handler import InputHandler
            input_handler = InputHandler(self.config, self.logger)
            input_handler.setup_key_handler(self.toggle_farming, self.stop_resource_farming)
            for x in range(0,5):
                self.resource_farmer.continuous_farming(cycle_interval=5)
                self.logger.info(f"Farming cycle {x} of 5 ended")
        except Exception as e:
            self.logger.error(f"Farming error: {e}")

    def start_rest_farming_player(self) -> None:
        self.logger.info("Starting rest farming...")
        try:
            self.resource_farmer.farm_rest_player()
            from Modules.Bot.input_handler import InputHandler
            input_handler = InputHandler(self.config, self.logger)
            input_handler.setup_key_handler(self.toggle_farming, self.stop_resource_farming)
            self.resource_farmer.continuous_farming(cycle_interval=5)
        except Exception as e:
            self.logger.error(f"Rest farming error: {e}")

    def take_debug_screenshot(self) -> None:
        self.logger.info("Taking debug screenshot...")
        try:
            path = self.resource_farmer.take_screenshot("debug_manual")
            self.logger.info(f"Screenshot saved: {path}")
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")

    def test_yolo_detection(self) -> None:
        if not self.yolo_model_path or not Path(self.yolo_model_path).exists():
            self.logger.error("YOLO model unavailable")
            return
        self.logger.info("Testing YOLO detection...")
        try:
            detected = self.resource_farmer.yolo_handler.find_objects_on_screen()
            if detected:
                for i, obj in enumerate(detected, 1):
                    self.logger.info(f"{i}. {obj['class_name']} ({obj['confidence']:.2f})")
            else:
                self.logger.warning("No objects detected")
            annotated = self.resource_farmer.yolo_handler.save_annotated_screenshot("yolo_test.png")
            self.logger.info(f"Annotated image: {annotated}")
        except Exception as e:
            self.logger.error(f"YOLO test error: {e}")

    def toggle_farming(self) -> None:
        if self.resource_farmer.farming_active:
            self.resource_farmer.stop_farming()
            self.logger.info("Farming paused")
        else:
            self.resource_farmer.start_farming()
            self.logger.info("Farming resumed")

    def stop_resource_farming(self) -> None:
        self.resource_farmer.stop_farming()
        self.logger.info("Farming stopped")

    def cleanup(self) -> None:
        try:
            if self.resource_farmer:
                self.resource_farmer.stop_farming()
            self.logger.info("Cleanup done")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def signal_handler(self, signum, frame):
        self.logger.info(f"Signal {signum} received, shutting down")
        self.cleanup()
        sys.exit(0)


class ModernBotGUI(ttk.Frame):
    def __init__(self, parent, yolo_model_path=None):
        super().__init__(parent)
        self.parent = parent
        self.yolo_model_path = yolo_model_path

        self.setup_theme()

        parent.title("Top Eleven Automation Bot")
        parent.geometry("900x650")
        parent.configure(bg='#1e1e1e')
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.grid(sticky="nsew")

        self.controller = SimpleBotController(yolo_model_path)

        self.create_header()
        self.create_main_content()
        self.create_status_bar()

        if not self.controller.initialize():
            self.log("Initialization failed", 'error')
        else:
            self.log("Bot initialized", 'info')

        signal.signal(signal.SIGINT, self.controller.signal_handler)
        signal.signal(signal.SIGTERM, self.controller.signal_handler)

    def setup_theme(self):
        style = ttk.Style()
        colors = {
            'bg': '#1e1e1e', 'fg': '#ffffff',
            'select_bg': '#404040', 'select_fg': '#ffffff',
            'accent': '#0078d4', 'accent_hover': '#106ebe',
            'success': '#107c10', 'warning': '#ff8c00', 'error': '#d13438'
        }
        style.configure('TFrame', background=colors['bg'])
        style.configure('Card.TFrame', background='#2d2d2d')
        style.configure('Header.TFrame', background='#2d2d2d')
        style.configure('TButton', background=colors['accent'], foreground='#000000', font=('Segoe UI', 10))
        style.map('TButton', background=[('active', colors['accent_hover']), ('pressed', '#005a9e')])
        style.configure('Success.TButton', background=colors['success'])
        style.map('Success.TButton', background=[('active', '#0e6e0e')])
        style.configure('Warning.TButton', background=colors['warning'])
        style.map('Warning.TButton', background=[('active', '#e67c00')])
        style.configure('Error.TButton', background=colors['error'])
        style.map('Error.TButton', background=[('active', '#b52d30')])
        style.configure('Header.TLabel', background='#2d2d2d', foreground=colors['fg'], font=('Segoe UI', 16, 'bold'))
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'], font=('Segoe UI', 10))
        style.configure('Status.TLabel', background='#2d2d2d', foreground='#888888', font=('Segoe UI', 9))

    def create_header(self):
        header = ttk.Frame(self, style='Header.TFrame', padding=(20, 15))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title = ttk.Label(header, text="Top Eleven Bot", style='Header.TLabel')
        title.grid(row=0, column=0, sticky="w")
        status = "YOLO Enabled" if (self.yolo_model_path and Path(self.yolo_model_path).exists()) else "Fallback Detection"
        ttk.Label(header, text=status, style='Status.TLabel').grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(header, textvariable=self.status_var, style='Status.TLabel').grid(row=0, column=1, sticky="e")
        header.grid_columnconfigure(1, weight=1)

    def create_main_content(self):
        main = ttk.Frame(self, style='TFrame')
        main.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        self.create_controls(main)
        self.create_log(main)

    def create_controls(self, parent):
        controls = ttk.Frame(parent, style='Card.TFrame', padding=20)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        controls.grid_columnconfigure((0,1,2), weight=1)
        groups = [
            {'title': 'Launch & Setup', 'buttons': [('Launch', self.launch), ('Screenshot', self.screenshot)]},
            {'title': 'Farming', 'buttons': [('Farm Greens', self.farm), ('Farm Rest', self.rest_farm)]},
            {'title': 'Tools', 'buttons': [('Test YOLO', self.test_yolo), ('Exit', self.exit_app)]}
        ]
        for i, g in enumerate(groups):
            gf = ttk.Frame(controls, style='TFrame', padding=10)
            gf.grid(row=0, column=i, sticky="nsew", padx=10)
            ttk.Label(gf, text=g['title']).grid(row=0, column=0, sticky="w", pady=(0,10))
            for j, (t, cmd) in enumerate(g['buttons']):
                btn = ttk.Button(gf, text=t, command=lambda c=cmd: self.execute_threaded(c))
                btn.grid(row=j+1, column=0, sticky="ew", pady=2)
                gf.grid_columnconfigure(0, weight=1)

    def create_log(self, parent):
        logf = ttk.Frame(parent, style='Card.TFrame', padding=15)
        logf.grid(row=1, column=0, sticky="nsew")
        logf.grid_rowconfigure(1, weight=1)
        logf.grid_columnconfigure(0, weight=1)
        ttk.Label(logf, text="Activity Log").grid(row=0, column=0, sticky="w", pady=(0,10))
        ttk.Button(logf, text="Clear", command=self.clear_log).grid(row=0, column=1, sticky="e")
        self.log_widget = ScrolledText(
            logf, wrap="word", state="disabled", font=('Consolas', 10),
            bg='#1a1a1a', fg='#ffffff', insertbackground='#ffffff',
            selectbackground='#404040', selectforeground='#ffffff',
            relief='flat', borderwidth=0
        )
        self.log_widget.grid(row=1, column=0, columnspan=2, sticky="nsew")
        for tag, color in [('success','#4ec9b0'), ('warning','#ffd700'), ('error','#f14c4c'), ('info','#9cdcfe')]:
            self.log_widget.tag_configure(tag, foreground=color)

    def create_status_bar(self):
        sf = ttk.Frame(self, style='Header.TFrame', padding=(20, 10))
        sf.grid(row=2, column=0, sticky="ew")
        self.time_var = tk.StringVar()
        ttk.Label(sf, textvariable=self.time_var, style='Status.TLabel').grid(row=0, column=0, sticky="w")
        self.update_time()
        sf.grid_columnconfigure(1, weight=1)

    def update_time(self):
        self.time_var.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self.update_time)

    def log(self, message, level='info'):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        msg = f"[{ts}] {message}\n"
        self.log_widget.configure(state="normal")
        tag = 'info'
        if level in ('success','warning','error'):
            tag = level
        self.log_widget.insert("end", msg, tag)
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    def clear_log(self):
        self.log_widget.configure(state="normal")
        self.log_widget.delete(1.0, "end")
        self.log_widget.configure(state="disabled")
        self.log("Log cleared")

    def execute_threaded(self, command):
        self.status_var.set("Working...")
        threading.Thread(target=lambda: self._execute_with_status(command), daemon=True).start()

    def _execute_with_status(self, command):
        try:
            command()
        finally:
            self.parent.after(0, lambda: self.status_var.set("Ready"))

    def launch(self):
        self.log("Launching...", 'info')
        ok = self.controller.launch_top_eleven()
        self.log("Launch succeeded" if ok else "Launch failed", 'success' if ok else 'error')

    def farm(self):
        self.log("Starting farming...", 'info')
        self.log("Use F2 to pause/resume, F3 to stop", 'info')
        try:
            self.controller.start_resource_farming()
            self.log("Farming stopped", 'info')
        except Exception as e:
            self.log(f"Farming error: {e}", 'error')

    def rest_farm(self):
        self.log("Starting rest farming...", 'info')
        self.log("Use F2 to pause/resume, F3 to stop", 'info')
        try:
            self.controller.start_rest_farming_player()
            self.log("Rest farming stopped", 'info')
        except Exception as e:
            self.log(f"Rest error: {e}", 'error')

    def screenshot(self):
        self.log("Taking screenshot...", 'info')
        try:
            self.controller.take_debug_screenshot()
            self.log("Screenshot done", 'success')
        except Exception as e:
            self.log(f"Screenshot error: {e}", 'error')

    def test_yolo(self):
        self.log("Testing YOLO...", 'info')
        try:
            self.controller.test_yolo_detection()
            self.log("YOLO test done", 'success')
        except Exception as e:
            self.log(f"YOLO error: {e}", 'error')

    def exit_app(self):
        self.log("Shutting down...", 'info')
        self.controller.cleanup()
        self.log("Shutdown complete", 'success')
        self.parent.after(500, self.parent.destroy)


def main():
    yolo_model_path = None
    if len(sys.argv) > 1 and sys.argv[1].endswith('.pt'):
        yolo_model_path = sys.argv[1]
        print(f"Model specified: {yolo_model_path}")

    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.configure(bg='#1e1e1e')
    app = ModernBotGUI(root, yolo_model_path)

    def on_closing():
        app.controller.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
