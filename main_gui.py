import sys
import threading
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import datetime
from pathlib import Path
from Modules.Bot.config import BotConfig
from main import SimpleBotController

class ModernBotGUI(ttk.Frame):
    def __init__(self, parent, yolo_model_path=None):
        super().__init__(parent)
        self.parent = parent
        
        # Store yolo_model_path for later use
        self.yolo_model_path = yolo_model_path
        
        # Configure modern theme and styling
        self.setup_modern_theme()
        
        # Layout setup
        parent.title("Top Eleven Automation Bot")
        parent.geometry("900x650")
        parent.configure(bg='#1e1e1e')  # Dark background
        parent.grid_rowconfigure(0, weight=1)  # Make the main frame fill vertically
        parent.grid_columnconfigure(0, weight=1)  # Make the main frame fill horizontally
        self.grid(sticky="nsew")
        
        # Configure this frame's grid weights
        self.grid_rowconfigure(1, weight=1)  # Make main content area expandable
        self.grid_columnconfigure(0, weight=1)  # Make content fill horizontally
        
        # Initialize controller first
        self.controller = SimpleBotController(yolo_model_path)
        
        # Create header (now controller exists)
        self.create_header()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Initialize controller
        if not self.controller.initialize():
            self.log("❌ Initialization failed. Check logs for details.", 'error')
        else:
            self.log("✅ Bot initialized successfully.", 'success')
        
    def setup_modern_theme(self):
        """Configure a modern dark theme"""
        style = ttk.Style()
        
        # Configure colors
        colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'select_bg': '#404040',
            'select_fg': '#ffffff',
            'accent': '#0078d4',
            'accent_hover': '#106ebe',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438'
        }
        
        # Configure frame styles
        style.configure('Modern.TFrame', background=colors['bg'])
        style.configure('Card.TFrame', background='#2d2d2d', relief='flat', borderwidth=1)
        style.configure('Header.TFrame', background='#2d2d2d', relief='flat', borderwidth=0)
        
        # Configure button styles
        style.configure('Modern.TButton',
                       background=colors['accent'],
                       foreground='#000000',  # Black text
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10))
        
        style.map('Modern.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', '#005a9e')])
        
        # Configure success/warning/error button variants
        style.configure('Success.TButton', background=colors['success'])
        style.map('Success.TButton', background=[('active', '#0e6e0e')])
        
        style.configure('Warning.TButton', background=colors['warning'])
        style.map('Warning.TButton', background=[('active', '#e67c00')])
        
        style.configure('Error.TButton', background=colors['error'])
        style.map('Error.TButton', background=[('active', '#b52d30')])
        
        # Configure label styles
        style.configure('Header.TLabel',
                       background='#2d2d2d',
                       foreground=colors['fg'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Modern.TLabel',
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10))
        
        style.configure('Status.TLabel',
                       background='#2d2d2d',
                       foreground='#888888',
                       font=('Segoe UI', 9))
    
    def create_header(self):
        """Create a modern header with title and status indicator"""
        header_frame = ttk.Frame(self, style='Header.TFrame', padding=(20, 15))
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Title and YOLO status
        title_label = ttk.Label(header_frame, text="⚡ Top Eleven Bot", style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # YOLO status indicator
        yolo_status = "✅ YOLO11 Enabled" if (self.yolo_model_path and Path(self.yolo_model_path).exists()) else "⚠️ Traditional Detection"
        yolo_label = ttk.Label(header_frame, text=yolo_status, style='Status.TLabel')
        yolo_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Current status indicator
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(header_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.grid(row=0, column=1, sticky="e")
        
        header_frame.grid_columnconfigure(1, weight=1)
    
    def create_main_content(self):
        """Create the main content area with controls and log"""
        main_frame = ttk.Frame(self, style='Modern.TFrame')
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_rowconfigure(1, weight=1)  # Make log section expandable
        main_frame.grid_columnconfigure(0, weight=1)  # Fill horizontally
        
        # Controls section
        self.create_controls_section(main_frame)
        
        # Log section
        self.create_log_section(main_frame)
    
    def create_controls_section(self, parent):
        """Create modern control buttons organized in cards"""
        controls_frame = ttk.Frame(parent, style='Card.TFrame', padding=20)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Configure grid to expand properly
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_columnconfigure(2, weight=1)
        
        # Group buttons by functionality
        button_groups = [
            {
                'title': '🚀 Launch & Setup',
                'buttons': [
                    ('Launch Game', self.launch, 'Modern.TButton'),
                    ('Take Screenshot', self.screenshot, 'Modern.TButton')
                ]
            },
            {
                'title': '🌾 Farming Operations',
                'buttons': [
                    ('Farm Greens', self.farm, 'Success.TButton'),
                    ('Farm Player Rest', self.rest_farm, 'Success.TButton')
                ]
            },
            {
                'title': '🔧 Tools & Debug',
                'buttons': [
                    ('Test YOLO', self.test_yolo, 'Warning.TButton'),
                    ('Exit App', self.exit_app, 'Error.TButton')
                ]
            }
        ]
        
        for col, group in enumerate(button_groups):
            group_frame = ttk.Frame(controls_frame, style='Modern.TFrame', padding=10)
            group_frame.grid(row=0, column=col, sticky="nsew", padx=10)
            
            # Group title
            title_label = ttk.Label(group_frame, text=group['title'], style='Modern.TLabel')
            title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
            
            # Buttons
            for i, (text, command, style_name) in enumerate(group['buttons']):
                btn = ttk.Button(group_frame, text=text, style=style_name,
                               command=lambda c=command: self.execute_threaded(c))
                btn.grid(row=i+1, column=0, sticky="ew", pady=2)
                group_frame.grid_columnconfigure(0, weight=1)
    
    def create_log_section(self, parent):
        """Create a modern log display area"""
        log_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)  # Make text area expandable
        log_frame.grid_columnconfigure(0, weight=1)  # Fill horizontally
        
        # Log header
        log_header = ttk.Label(log_frame, text="📋 Activity Log", style='Modern.TLabel')
        log_header.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Clear log button
        clear_btn = ttk.Button(log_frame, text="Clear", style='Modern.TButton',
                              command=self.clear_log)
        clear_btn.grid(row=0, column=1, sticky="e", pady=(0, 10))
        
        # Ensure header row doesn't expand
        log_frame.grid_columnconfigure(1, weight=0)
        
        # Log text area with modern styling
        self.log_widget = ScrolledText(
            log_frame,
            wrap="word",
            state="disabled",
            font=('Consolas', 10),
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#404040',
            selectforeground='#ffffff',
            relief='flat',
            borderwidth=0
        )
        self.log_widget.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        # Configure log text colors for different message types
        self.log_widget.tag_configure('success', foreground='#4ec9b0')
        self.log_widget.tag_configure('warning', foreground='#ffd700')
        self.log_widget.tag_configure('error', foreground='#f14c4c')
        self.log_widget.tag_configure('info', foreground='#9cdcfe')
    
    def create_status_bar(self):
        """Create a modern status bar"""
        status_frame = ttk.Frame(self, style='Header.TFrame', padding=(20, 10))
        status_frame.grid(row=2, column=0, sticky="ew")
        
        # Current time
        self.time_var = tk.StringVar()
        time_label = ttk.Label(status_frame, textvariable=self.time_var, style='Status.TLabel')
        time_label.grid(row=0, column=0, sticky="w")
        
        # Update time periodically
        self.update_time()
        
        status_frame.grid_columnconfigure(1, weight=1)
    
    def update_time(self):
        """Update the status bar time"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.after(1000, self.update_time)
    
    def log(self, message, level='info'):
        """Enhanced logging with color coding"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_widget.configure(state="normal")
        
        # Determine message type and apply appropriate color
        if '✅' in message or 'success' in message.lower():
            tag = 'success'
        elif '⚠️' in message or 'warning' in message.lower():
            tag = 'warning'
        elif '❌' in message or 'error' in message.lower() or 'failed' in message.lower():
            tag = 'error'
        else:
            tag = 'info'
        
        self.log_widget.insert("end", formatted_message, tag)
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_widget.configure(state="normal")
        self.log_widget.delete(1.0, "end")
        self.log_widget.configure(state="disabled")
        self.log("📋 Log cleared")
    
    def execute_threaded(self, command):
        """Execute command in a separate thread to prevent UI freezing"""
        self.status_var.set("Working...")
        threading.Thread(target=lambda: self._execute_with_status(command)).start()
    
    def _execute_with_status(self, command):
        """Execute command and update status"""
        try:
            command()
        finally:
            self.status_var.set("Ready")
    
    # Button command methods using your actual controller
    def launch(self):
        self.log("🚀 Launching Top Eleven...", 'info')
        success = self.controller.launch_top_eleven()
        if success:
            self.log("✅ Top Eleven launched successfully", 'success')
        else:
            self.log("❌ Launch failed", 'error')
    
    def farm(self):
        self.log("🌾 Starting YOLO-enhanced resource farming...", 'info')
        self.log("Press F2 to toggle pause/resume, F3 to stop", 'info')
        try:
            self.controller.start_resource_farming()
            self.log("🛑 Resource farming stopped", 'info')
        except Exception as e:
            self.log(f"❌ Resource farming error: {e}", 'error')
    
    def rest_farm(self):
        self.log("😴 Starting automated player rest farming...", 'info')
        self.log("Press F2 to toggle pause/resume, F3 to stop", 'info')
        try:
            self.controller.start_rest_farming_player()
            self.log("🛑 Player rest farming stopped", 'info')
        except Exception as e:
            self.log(f"❌ Player rest farming error: {e}", 'error')
    
    def screenshot(self):
        self.log("📸 Taking debug screenshot with YOLO annotations...", 'info')
        try:
            # Use the same method name as in your main.py
            self.controller.take_debug_screenshot()
            self.log("✅ Debug screenshot completed", 'success')
        except Exception as e:
            self.log(f"❌ Screenshot failed: {e}", 'error')
    
    def test_yolo(self):
        self.log("🧪 Testing YOLO detection...", 'info')
        try:
            self.controller.test_yolo_detection()
            self.log("✅ YOLO test completed", 'success')
        except Exception as e:
            self.log(f"❌ YOLO test failed: {e}", 'error')
    
    def exit_app(self):
        self.log("👋 Shutting down bot...", 'info')
        self.controller.cleanup()
        self.log("✅ Bot shutdown complete", 'success')
        self.parent.after(500, self.parent.destroy)

if __name__ == "__main__":
    yolo_path = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    
    # Configure root window
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    
    # Apply dark theme to root
    root.configure(bg='#1e1e1e')
    
    app = ModernBotGUI(root, yolo_path)
    root.mainloop()