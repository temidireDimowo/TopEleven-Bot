import sys
import threading
import tkinter as tk
from pathlib import Path

from Modules.Bot.config import BotConfig, ClickType
from Modules.Bot.log import BotLogger
from Modules.bluestacks import BlueStacksBot
from Modules.farm_resources import ResourceFarmer
from Modules.Bot.input_handler import InputHandler

from main import SimpleBotController

class BotGUI(tk.Tk):
    def __init__(self, yolo_model_path=None):
        super().__init__()
        self.title("Top Eleven Automation Bot")
        self.geometry("600x400")

        # Buttons frame (pack first so text area resizes below)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=(10, 0))

        btn_names = [
            ("Launch App", self.launch),
            ("Farm Greens", self.farm),
            ("Rest Farm", self.rest_farm),
            ("Debug Screenshot", self.screenshot),
            ("Test YOLO", self.test_yolo),
            ("Exit", self.exit_app)
        ]
        for text, cmd in btn_names:
            tk.Button(btn_frame, text=text, command=lambda c=cmd: threading.Thread(target=c).start()).pack(side='left', padx=5)

        # Log text area fills remaining space
        self.log_text = tk.Text(self, state='disabled', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Initialize controller
        self.controller = SimpleBotController(yolo_model_path)
        if not self.controller.initialize():
            self.log("❌ Initialization failed. Check logs for details.")
        else:
            self.log("✅ Bot initialized successfully.")

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + "\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def launch(self):
        self.log("🚀 Launching Top Eleven...")
        success = self.controller.launch_top_eleven()
        self.log("✅ Launched." if success else "❌ Launch failed.")

    def farm(self):
        self.log("🌾 Starting farming...")
        self.controller.start_resource_farming()
        self.log("🛑 Farming stopped.")

    def rest_farm(self):
        self.log("🌾 Starting rest farming...")
        self.controller.start_rest_farming_player()
        self.log("🛑 Rest farming stopped.")

    def screenshot(self):
        self.log("📸 Taking debug screenshot...")
        try:
            path = self.controller.resource_farmer.take_screenshot("debug_manual")
            self.log(f"✅ Screenshot saved: {path}")
        except Exception as e:
            self.log(f"❌ Screenshot failed: {e}")

    def test_yolo(self):
        self.log("🧪 Testing YOLO detection...")
        try:
            self.controller.test_yolo_detection()
        except Exception as e:
            self.log(f"❌ YOLO test failed: {e}")

    def exit_app(self):
        self.log("👋 Exiting...")
        self.controller.cleanup()
        self.destroy()

if __name__ == '__main__':
    # Optional: pass YOLO model path as first arg
    yolo_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = BotGUI(yolo_path)
    app.mainloop()
