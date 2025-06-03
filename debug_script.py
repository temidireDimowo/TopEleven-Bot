#!/usr/bin/env python3
"""
Debug script to help troubleshoot Top Eleven app detection issues.
"""

import sys
import time
from pathlib import Path
import pyautogui
import PIL.Image
from typing import Optional

# Add the current directory to the path to import bot modules
sys.path.append(str(Path(__file__).parent))

from Modules.Bot.config import BotConfig
from Modules.Bot.image_handler import ImageHandler
from Modules.Bot.log import BotLogger


def take_debug_screenshot(filename: str = "debug_screenshot.png") -> str:
    """Take a screenshot for debugging purposes."""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"📸 Screenshot saved as: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to take screenshot: {e}")
        return ""


def test_image_loading(image_path: str) -> Optional[PIL.Image.Image]:
    """Test if an image can be loaded properly."""
    try:
        print(f"🔍 Testing image loading for: {image_path}")
        
        # Check if file exists
        if not Path(image_path).exists():
            print(f"❌ Image file does not exist: {image_path}")
            return None
        
        # Try to load the image
        image = PIL.Image.open(image_path)
        print(f"✅ Image loaded successfully!")
        print(f"   - Size: {image.size}")
        print(f"   - Mode: {image.mode}")
        print(f"   - Format: {image.format}")
        
        return image
        
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return None


def test_image_detection(image: PIL.Image.Image, confidence: float = 0.75) -> bool:
    """Test image detection on current screen."""
    try:
        print(f"🔍 Searching for image on screen with confidence {confidence}...")
        
        result = pyautogui.locateOnScreen(
            image, 
            grayscale=True, 
            confidence=confidence
        )
        
        if result is None:
            print("❌ Image not found on screen")
            return False
        
        center_point = pyautogui.center(result)
        print(f"✅ Image found at coordinates: ({center_point.x}, {center_point.y})")
        print(f"   - Bounding box: {result}")
        
        return True
        
    except pyautogui.ImageNotFoundException:
        print("❌ Image not found on screen (ImageNotFoundException)")
        return False
    except Exception as e:
        print(f"❌ Error during image detection: {e}")
        return False


def debug_top_eleven_detection(test_image_path ="TopEleven\Ads\close\close_15.png"):
    """Main debug function for Top Eleven app detection."""
    print("🐛 Starting Top Eleven Detection Debug")
    print("=" * 50)
    
    # Load configuration
    config = BotConfig.from_json("config.json")
    print(f"📁 Images directory: {config.images_dir}")
    print(f"📁 Top Eleven directory: {config.top_eleven_dir}")
    
    # Construct the expected image path
    top_eleven_image_path = Path(config.images_dir) / test_image_path
    print(f"🎯 Looking for Top Eleven image at: {top_eleven_image_path}")
    
    # Test 1: Check if image file exists and can be loaded
    print("\n📋 Test 1: Image File Loading")
    print("-" * 30)
    image = test_image_loading(str(top_eleven_image_path))
    
    if image is None:
        print("\n🛑 Cannot proceed with detection tests - image loading failed")
        print("\n💡 Suggestions:")
        print("   1. Check if the image file exists at the expected location")
        print("   2. Verify the file isn't corrupted")
        print("   3. Make sure the file has the correct name and extension")
        return
    
    # Test 2: Take a screenshot for manual comparison
    print("\n📋 Test 2: Current Screen Capture")
    print("-" * 30)
    screenshot_path = take_debug_screenshot("bluestacks_current_screen.png")
    
    # Test 3: Try detection with different confidence levels
    print("\n📋 Test 3: Image Detection Tests")
    print("-" * 30)
    
    confidence_levels = [0.9, 0.8, 0.75, 0.7, 0.6, 0.5]
    
    for confidence in confidence_levels:
        print(f"\n🎯 Testing with confidence: {confidence}")
        if test_image_detection(image, confidence):
            print(f"✅ SUCCESS: Image detected with confidence {confidence}")
            break
        else:
            print(f"❌ FAILED: Image not detected with confidence {confidence}")
    
    # Test 4: Try detection without grayscale
    print("\n📋 Test 4: Color Detection Test")
    print("-" * 30)
    try:
        print("🔍 Searching for image on screen (color mode)...")
        result = pyautogui.locateOnScreen(image, confidence=0.75)
        
        if result is not None:
            center_point = pyautogui.center(result)
            print(f"✅ Image found in color mode at: ({center_point.x}, {center_point.y})")
        else:
            print("❌ Image not found in color mode")
            
    except Exception as e:
        print(f"❌ Error in color detection: {e}")
    
    # Test 5: Show all files in the BlueStacks directory
    print("\n📋 Test 5: Available BlueStacks Images")
    print("-" * 30)
    
    bluestacks_dir = Path(config.images_dir) / "TopEleven"
    if bluestacks_dir.exists():
        print(f"📁 Contents of {bluestacks_dir}:")
        for file in bluestacks_dir.iterdir():
            if file.is_file() and file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                print(f"   📄 {file.name}")
    else:
        print(f"❌ BlueStacks directory not found: {bluestacks_dir}")
    
    print("\n" + "=" * 50)
    print("🐛 Debug completed!")
    print("\n💡 Next Steps:")
    print("   1. Compare the screenshot with your Top Eleven app icon")
    print("   2. If the icon looks different, update the image file")
    print("   3. If the icon isn't visible, navigate to BlueStacks home screen manually")
    print("   4. Try running the detection with a lower confidence level")


def interactive_debug(test_image_path ="TopEleven\Ads\close\close_15.png"):
    """Interactive debug mode with menu options."""
    while True:
        print("\n" + "=" * 50)
        print("🐛 Top Eleven Detection Debug Menu")
        print("=" * 50)
        print("1. Run full debug analysis")
        print("2. Take screenshot only")
        print("3. Test image loading only")
        print("4. Test detection with custom confidence")
        print("5. List available images")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == '0':
            print("👋 Exiting debug mode...")
            break
        elif choice == '1':
            debug_top_eleven_detection()
        elif choice == '2':
            take_debug_screenshot("manual_screenshot.png")
        elif choice == '3':
            config = BotConfig.from_json("config.json")
            top_eleven_image_path = Path(config.images_dir) / test_image_path
            test_image_loading(str(top_eleven_image_path))
        elif choice == '4':
            try:
                confidence = float(input("Enter confidence level (0.1-1.0): "))
                config = BotConfig.from_json("config.json")
                top_eleven_image_path = Path(config.images_dir) / test_image_path
                image = test_image_loading(str(top_eleven_image_path))
                if image:
                    test_image_detection(image, confidence)
            except ValueError:
                print("❌ Invalid confidence value")
        elif choice == '5':
            config = BotConfig.from_json("config.json")
            bluestacks_dir = Path(config.images_dir) / "TopEleven"
            if bluestacks_dir.exists():
                print(f"\n📁 Images in {bluestacks_dir}:")
                for file in bluestacks_dir.iterdir():
                    if file.is_file():
                        print(f"   📄 {file.name}")
            else:
                print(f"❌ Directory not found: {bluestacks_dir}")
        else:
            print("❌ Invalid choice. Please enter 0-5.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'auto':
        debug_top_eleven_detection()
    else:
        interactive_debug()