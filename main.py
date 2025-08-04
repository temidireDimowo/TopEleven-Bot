#!/usr/bin/env python3
"""
Simplified Game Automation Bot for Top Eleven BlueStacks with YOLO11 support.
Only supports launching the game and resource farming.
"""

import sys
import time
import signal
from pathlib import Path
from typing import Optional

# Add the current directory to the path to import bot modules
sys.path.append(str(Path(__file__).parent))

from Modules.Bot.config import BotConfig, ClickType
from Modules.Bot.log import BotLogger
from Modules.bluestacks import BlueStacksBot
from Modules.farm_resources import ResourceFarmer


class SimpleBotController:
    """Simplified controller for launch and farming functionalities with YOLO support."""
    
    def __init__(self, yolo_model_path: str = None):
        self.config = None
        self.logger = None
        self.bluestacks_bot = None
        self.resource_farmer = None
        self.running = False
        self.yolo_model_path = yolo_model_path
        
    def initialize(self) -> bool:
        """Initialize bot components with optional YOLO model."""
        try:
            # Load configuration
            self.config = BotConfig.from_json("config.json")
            
            # Setup logging
            bot_logger = BotLogger(self.config)
            self.logger = bot_logger.setup_logging()
            
            # Validate configuration
            if not self.config.validate():
                self.logger.error("Configuration validation failed")
                return False
            
            self.logger.info("Configuration loaded and validated successfully")
            
            # Log YOLO model status
            if self.yolo_model_path and Path(self.yolo_model_path).exists():
                self.logger.info(f"🤖 YOLO11 model will be used: {self.yolo_model_path}")
            else:
                self.logger.warning("⚠️ YOLO11 model not found, using traditional image detection")
            
            # Initialize specialized bots
            self.bluestacks_bot = BlueStacksBot(self.config, self.logger)

            try:
                # Initialize ResourceFarmer with YOLO model path
                self.resource_farmer = ResourceFarmer(
                    self.config, 
                    self.logger, 
                    model_path=self.yolo_model_path
                )
                
                # Log detection method info
                detection_info = self.resource_farmer.get_detection_info()
                self.logger.info(f"🔍 Detection method: {detection_info['detection_method']}")
                if detection_info['model_info']:
                    model_info = detection_info['model_info']
                    self.logger.info(f"📋 Model classes: {list(model_info['class_names'].values())}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize Resource farmer: {e}")
                return False
            
            self.logger.info("Bot modules initialized successfully")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize bot: {e}")
            else:
                print(f"Failed to initialize bot: {e}")
            return False
    
    def print_main_menu(self) -> None:
        """Print the simplified main menu options with YOLO status."""
        yolo_status = "✅ YOLO11 Enabled" if (self.yolo_model_path and Path(self.yolo_model_path).exists()) else "⚠️ Traditional Detection"
        
        menu = f"""
╔══════════════════════════════════════════════════════════════╗
║                    Game Automation Bot                       ║
║                  Top Eleven BlueStacks                       ║
║                      Enhanced Version                        ║
║                                                              ║
║  Detection Mode: {yolo_status:<39} ║
╠══════════════════════════════════════════════════════════════╣
║  Available Commands:                                         ║
║                                                              ║
║  [1] Launch Top Eleven on BlueStacks                         ║
║  [2] Start Farming Greens (YOLO Enhanced)                    ║
║  [3] Take Debug Screenshot                                   ║
║  [4] Test YOLO Detection                                     ║
║  [0] Exit                                                    ║
║                                                              ║
║  During farming:                                             ║
║  • Press F2 to toggle pause/resume                           ║
║  • Press F3 to stop current operation                        ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(menu)
    
    def launch_top_eleven(self) -> bool:
        """Launch Top Eleven app on BlueStacks."""
        self.logger.info("🚀 Launching Top Eleven on BlueStacks...")
        
        try:
            # Apply BlueStacks optimizations
            self.bluestacks_bot.optimize_for_bluestacks()
            
            # Find and launch Top Eleven app
            result = self.bluestacks_bot.open_top_eleven_app()
            
            if result:
                self.logger.info("✅ Top Eleven launch sequence initiated")
                
                # Wait for BlueStacks to be ready
                if self.bluestacks_bot.wait_for_bluestacks_ready(timeout=120):
                    self.logger.info("🎮 BlueStacks is ready for automation")
                    time.sleep(5)  # Additional wait for app to fully load
                    return True
                else:
                    self.logger.warning("⚠️ BlueStacks not ready within timeout")
                    return False
            else:
                self.logger.error("❌ Failed to launch Top Eleven")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching Top Eleven: {e}")
            return False
    
    def start_resource_farming(self) -> None:
        """Start automated resource farming with YOLO enhancement."""
        self.logger.info("🌾 Starting YOLO-enhanced resource farming automation...")
        
        try:
            self.resource_farmer.start_farming()
            
            # Setup key handlers for control
            from Modules.Bot.input_handler import InputHandler
            input_handler = InputHandler(self.config, self.logger)
            input_handler.setup_key_handler(
                lambda: self.toggle_farming(),
                lambda: self.stop_resource_farming()
            )
            
            # Run continuous farming
            self.resource_farmer.continuous_farming(cycle_interval=5)  # 5 seconds
            
        except Exception as e:
            self.logger.error(f"Error in resource farming: {e}")

    def start_rest_farming_player(self) -> None:
        """Start automated player rest farming with YOLO enhancement."""
        self.logger.info("🌾 Starting automated player rest farming automation...")
        
        try:
            self.resource_farmer.farm_rest_player()
            
            # Setup key handlers for control
            from Modules.Bot.input_handler import InputHandler
            input_handler = InputHandler(self.config, self.logger)
            input_handler.setup_key_handler(
                lambda: self.toggle_farming(),
                lambda: self.stop_resource_farming()
            )
            
            # Run continuous farming
            self.resource_farmer.continuous_farming(cycle_interval=5)  # 5 seconds
            
        except Exception as e:
            self.logger.error(f"Error in resource farming: {e}")
       
    def take_debug_screenshot(self) -> None:
        """Take a debug screenshot with YOLO annotations if available."""
        self.logger.info("📸 Taking debug screenshot...")
        
        try:
            screenshot_path = self.resource_farmer.take_screenshot("debug_manual")
            print(f"✅ Debug screenshot saved: {screenshot_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to take debug screenshot: {e}")
            print("❌ Failed to take debug screenshot")
    
    def test_yolo_detection(self) -> None:
        """Test YOLO detection and display results."""
        if not self.yolo_model_path or not Path(self.yolo_model_path).exists():
            print("❌ YOLO model not available for testing")
            return
            
        self.logger.info("🧪 Testing YOLO detection...")
        
        try:
            # Get all detected objects
            detected_objects = self.resource_farmer.yolo_handler.find_objects_on_screen()
            
            if detected_objects:
                print(f"\n🎯 YOLO Detection Results ({len(detected_objects)} objects found):")
                print("=" * 60)
                
                for i, obj in enumerate(detected_objects, 1):
                    print(f"{i}. Class: {obj['class_name']}")
                    print(f"   Confidence: {obj['confidence']:.2f}")
                    print(f"   Center: ({obj['center_point'].x}, {obj['center_point'].y})")
                    print(f"   Size: {obj['width']}x{obj['height']}")
                    print()
            else:
                print("❌ No objects detected by YOLO")
            
            # Save annotated screenshot
            screenshot_path = self.resource_farmer.yolo_handler.save_annotated_screenshot("yolo_test.png")
            print(f"📸 Annotated screenshot saved: {screenshot_path}")
            
        except Exception as e:
            self.logger.error(f"Error during YOLO testing: {e}")
            print(f"❌ YOLO testing failed: {e}")
    
    def toggle_farming(self) -> None:
        """Toggle resource farming state."""
        if self.resource_farmer.farming_active:
            self.resource_farmer.stop_farming()
            self.logger.info("🔴 Resource farming paused")
        else:
            self.resource_farmer.start_farming()
            self.logger.info("🟢 Resource farming resumed")
    
    def stop_resource_farming(self) -> None:
        """Stop resource farming."""
        self.resource_farmer.stop_farming()
        self.logger.info("🛑 Resource farming stopped by user")
    
    def run_interactive_mode(self) -> None:
        """Run the bot in interactive mode with YOLO-enhanced menu."""
        self.logger.info("Starting YOLO-enhanced interactive mode...")
        
        while True:
            self.print_main_menu()
            
            try:
                choice = input("\nEnter your choice (0-5): ").strip()
                
                if choice == '0':
                    self.logger.info("👋 Exiting bot...")
                    self.cleanup()
                    break
                elif choice == '1':
                    success = self.launch_top_eleven()
                    if success:
                        print("✅ Top Eleven launched successfully!")
                    else:
                        print("❌ Failed to launch Top Eleven. Check logs for details.")
                elif choice == '2':
                    print("🌾 Starting YOLO-enhanced resource farming...")
                    print("Press F2 to toggle pause/resume, F3 to stop")
                    self.start_resource_farming()
                elif choice == '3':
                    self.take_debug_screenshot()
                elif choice == '4':
                    self.test_yolo_detection()
                elif choice == '5':
                    self.start_rest_farming_player()
                else:
                    print("❌ Invalid choice. Please enter 0-5.")
                
                if choice in ['2']:
                    # After farming stops, show menu again
                    input("\n📱 Press Enter to return to main menu...")
                elif choice in ['3', '4']:
                    input("\n📱 Press Enter to continue...")
                
            except KeyboardInterrupt:
                self.logger.info("👋 Keyboard interrupt received - exiting...")
                self.cleanup()
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}")
                input("Press Enter to continue...")
    
    def cleanup(self) -> None:
        """Cleanup resources before exit."""
        try:
            if self.resource_farmer:
                self.resource_farmer.stop_farming()
            
            self.logger.info("✅ Cleanup completed")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during cleanup: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"📡 Received signal {signum} - shutting down gracefully...")
        self.cleanup()
        sys.exit(0)


def main():
    """Main entry point with YOLO model path support."""
    # Default YOLO model path - update this to your model location
    default_yolo_path = "models/best.pt"
    
    # Parse command line arguments
    yolo_model_path = None
    
    # Check for YOLO model path argument
    if len(sys.argv) > 1:
        if sys.argv[1].endswith('.pt'):
            # First argument is a model path
            yolo_model_path = sys.argv[1]
            command_args = sys.argv[2:]
        else:
            # Check if default model exists
            if Path(default_yolo_path).exists():
                yolo_model_path = default_yolo_path
            command_args = sys.argv[1:]
    else:
        # Check if default model exists
        if Path(default_yolo_path).exists():
            yolo_model_path = default_yolo_path
        command_args = []
    
    # Create main controller with YOLO model
    controller = SimpleBotController(yolo_model_path=yolo_model_path)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, controller.signal_handler)
    signal.signal(signal.SIGTERM, controller.signal_handler)
    
    # Initialize the bot
    if not controller.initialize():
        print("❌ Failed to initialize bot. Check logs for details.")
        sys.exit(1)
    
    # Check for command line arguments
    if len(command_args) > 0:
        command = command_args[0].lower()
        
        if command == 'launch':
            success = controller.launch_top_eleven()
            if not success:
                print("❌ Failed to launch Top Eleven")
                sys.exit(1)
        elif command == 'farm':
            controller.start_resource_farming()
        elif command == 'test':
            controller.test_yolo_detection()
        elif command == 'screenshot':
            controller.take_debug_screenshot()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: launch, farm, test, screenshot")
            print("Or provide YOLO model path as first argument: python main.py path/to/best.pt farm")
            sys.exit(1)
    else:
        # Run in interactive mode
        controller.run_interactive_mode()


if __name__ == "__main__":
    main()