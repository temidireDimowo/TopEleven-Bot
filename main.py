#!/usr/bin/env python3
"""
Simplified Game Automation Bot for Top Eleven BlueStacks.
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
    """Simplified controller for launch and farming functionalities only."""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.bluestacks_bot = None
        self.resource_farmer = None
        self.running = False
        
    def initialize(self) -> bool:
        """Initialize bot components."""
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
            
            # Initialize specialized bots
            self.bluestacks_bot = BlueStacksBot(self.config, self.logger)

            try:
                self.resource_farmer = ResourceFarmer(self.config, self.logger)
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
        """Print the simplified main menu options."""
        menu = """
╔══════════════════════════════════════════════════════════════╗
║                    Game Automation Bot                       ║
║                  Top Eleven BlueStacks                       ║
║                      Simple Version                          ║
╠══════════════════════════════════════════════════════════════╣
║  Available Commands:                                         ║
║                                                              ║
║  [1] Launch Top Eleven on BlueStacks                         ║
║  [2] Start Farming Greens                                    ║
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
        """Start automated resource farming."""
        self.logger.info("🌾 Starting resource farming automation...")
        
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
        """Run the bot in interactive mode with simplified menu."""
        self.logger.info("Starting simplified interactive mode...")
        
        while True:
            self.print_main_menu()
            
            try:
                choice = input("\nEnter your choice (0-2): ").strip()
                
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
                    print("🌾 Starting resource farming...")
                    print("Press F2 to toggle pause/resume, F3 to stop")
                    self.start_resource_farming()
                else:
                    print("❌ Invalid choice. Please enter 0, 1, or 2.")
                
                if choice in ['2']:
                    # After farming stops, show menu again
                    input("\n📱 Press Enter to return to main menu...")
                
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
    """Main entry point."""
    # Create main controller
    controller = SimpleBotController()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, controller.signal_handler)
    signal.signal(signal.SIGTERM, controller.signal_handler)
    
    # Initialize the bot
    if not controller.initialize():
        print("❌ Failed to initialize bot. Check logs for details.")
        sys.exit(1)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'launch':
            success = controller.launch_top_eleven()
            if not success:
                print("❌ Failed to launch Top Eleven")
                sys.exit(1)
        elif command == 'farm':
            controller.start_resource_farming()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: launch, farm")
            sys.exit(1)
    else:
        # Run in interactive mode
        controller.run_interactive_mode()


if __name__ == "__main__":
    main()