"""
YOLO11-based image handling and screen detection for the Game Automation Bot.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import pyautogui
import pyscreeze
import PIL.Image
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

from .config import BotConfig


class YOLOImageHandler:
    """Handles image detection using custom YOLO11 model."""
    
    def __init__(self, config: BotConfig, logger: logging.Logger, model_path: str):
        self.config = config
        self.logger = logger
        self.model_path = Path(model_path)
        self.model = None
        self.class_names = {}
        
        # Initialize YOLO model
        self._load_model()
        
    def _load_model(self) -> None:
        """Load the YOLO11 model from the specified path."""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
                
            self.model = YOLO(str(self.model_path))
            self.logger.info(f"✅ YOLO11 model loaded successfully from: {self.model_path}")
            
            # Get class names from the model
            if hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
                self.logger.info(f"📋 Model classes: {list(self.class_names.values())}")
            else:
                self.logger.warning("⚠️ Could not retrieve class names from model")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load YOLO11 model: {e}")
            raise
    
    def find_objects_on_screen(self, target_classes: List[str] = None, 
                             confidence_threshold: float = None) -> List[Dict]:
        """
        Find objects on screen using YOLO11 model.
        
        Args:
            target_classes: List of class names to look for (e.g., ['close_ad', 'skip_ad'])
            confidence_threshold: Minimum confidence score (overrides config if provided)
            
        Returns:
            List of detected objects with their locations and metadata
        """
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Use config confidence or provided threshold
            conf_threshold = confidence_threshold or self.config.confidence
            
            # Run YOLO inference
            results = self.model.predict(
                screenshot_cv, 
                conf=conf_threshold,
                verbose=False
            )
            
            detected_objects = []
            
            if results and len(results) > 0:
                result = results[0]  # Get first result
                
                if result.boxes is not None and len(result.boxes) > 0:
                    # Convert to supervision format for easier handling
                    detections = sv.Detections.from_ultralytics(result)
                    
                    for i, (bbox, confidence, class_id) in enumerate(zip(
                        detections.xyxy, detections.confidence, detections.class_id
                    )):
                        class_name = self.class_names.get(int(class_id), f"class_{class_id}")
                        
                        # Filter by target classes if specified
                        if target_classes and class_name not in target_classes:
                            continue
                            
                        x1, y1, x2, y2 = bbox
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        obj_info = {
                            'class_name': class_name,
                            'confidence': float(confidence),
                            'center_point': pyscreeze.Point(center_x, center_y),
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'width': int(x2 - x1),
                            'height': int(y2 - y1)
                        }
                        
                        detected_objects.append(obj_info)
                        
                        self.logger.debug(
                            f"🎯 Found {class_name} at ({center_x}, {center_y}) "
                            f"with confidence {confidence:.2f}"
                        )
            
            self.logger.info(f"🔍 YOLO detection found {len(detected_objects)} objects")
            return detected_objects
            
        except Exception as e:
            self.logger.error(f"❌ Error during YOLO detection: {e}")
            return []
    
    def find_best_match(self, target_classes: List[str], 
                       confidence_threshold: float = None) -> Optional[Dict]:
        """
        Find the best matching object from target classes.
        
        Args:
            target_classes: List of class names to look for
            confidence_threshold: Minimum confidence score
            
        Returns:
            Best matching object info or None
        """
        detected_objects = self.find_objects_on_screen(target_classes, confidence_threshold)
        
        if not detected_objects:
            return None
            
        # Return the object with highest confidence
        best_match = max(detected_objects, key=lambda obj: obj['confidence'])
        
        self.logger.info(
            f"✅ Best match: {best_match['class_name']} "
            f"(confidence: {best_match['confidence']:.2f})"
        )
        
        return best_match
    
    def find_class_on_screen(self, class_name: str, 
                           confidence_threshold: float = None) -> Optional[pyscreeze.Point]:
        """
        Find a specific class on screen and return its center point.
        This method maintains compatibility with the existing image_handler interface.
        
        Args:
            class_name: Name of the class to find
            confidence_threshold: Minimum confidence score
            
        Returns:
            Center point of the detected object or None
        """
        best_match = self.find_best_match([class_name], confidence_threshold)
        
        if best_match:
            return best_match['center_point']
        return None
    
    def wait_for_class(self, class_name: str, timeout: int = 60, 
                      confidence_threshold: float = None) -> bool:
        """
        Wait for a specific class to appear on screen.
        
        Args:
            class_name: Name of the class to wait for
            timeout: Maximum time to wait in seconds
            confidence_threshold: Minimum confidence score
            
        Returns:
            True if class was found, False if timeout
        """
        self.logger.info(f"⏳ Waiting for {class_name} to appear...")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < timeout:
            check_count += 1
            self.logger.debug(f"🔍 Check #{check_count} for {class_name}")
            
            point = self.find_class_on_screen(class_name, confidence_threshold)
            if point:
                self.logger.info(f"✅ {class_name} found!")
                return True
            
            time.sleep(2)  # Check every 2 seconds
        
        self.logger.warning(f"⚠️ {class_name} not found after {timeout} seconds")
        return False
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            'model_path': str(self.model_path),
            'class_names': self.class_names,
            'num_classes': len(self.class_names) if self.class_names else 0
        }
    
    def save_annotated_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot and save it with YOLO detections annotated.
        Useful for debugging.
        
        Args:
            filename: Optional filename for the saved image
            
        Returns:
            Path to the saved annotated image
        """
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"yolo_detection_{timestamp}.png"
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Run YOLO inference
            results = self.model.predict(
                screenshot_cv, 
                conf=self.config.confidence,
                verbose=False
            )
            
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    # Convert to supervision format
                    detections = sv.Detections.from_ultralytics(result)
                    
                    # Create annotators
                    box_annotator = sv.BoxAnnotator()
                    label_annotator = sv.LabelAnnotator()
                    
                    # Create labels
                    labels = [
                        f"{self.class_names.get(int(class_id), f'class_{class_id}')} {confidence:.2f}"
                        for confidence, class_id in zip(detections.confidence, detections.class_id)
                    ]
                    
                    # Annotate image
                    annotated_image = box_annotator.annotate(
                        scene=screenshot_cv.copy(), 
                        detections=detections
                    )
                    annotated_image = label_annotator.annotate(
                        scene=annotated_image, 
                        detections=detections, 
                        labels=labels
                    )
                else:
                    annotated_image = screenshot_cv
            else:
                annotated_image = screenshot_cv
            
            # Save image
            save_path = Path(self.config.log_dir) / filename
            cv2.imwrite(str(save_path), annotated_image)
            
            self.logger.info(f"📸 Annotated screenshot saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save annotated screenshot: {e}")
            return """""
YOLO11-based image handling and screen detection for the Game Automation Bot.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import pyautogui
import pyscreeze
import PIL.Image
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

from .config import BotConfig


class YOLOImageHandler:
    """Handles image detection using custom YOLO11 model."""
    
    def __init__(self, config: BotConfig, logger: logging.Logger, model_path: str):
        self.config = config
        self.logger = logger
        self.model_path = Path(model_path)
        self.model = None
        self.class_names = {}
        
        # Initialize YOLO model
        self._load_model()
        
    def _load_model(self) -> None:
        """Load the YOLO11 model from the specified path."""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
                
            self.model = YOLO(str(self.model_path))
            self.logger.info(f"✅ YOLO11 model loaded successfully from: {self.model_path}")
            
            # Get class names from the model
            if hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
                self.logger.info(f"📋 Model classes: {list(self.class_names.values())}")
            else:
                self.logger.warning("⚠️ Could not retrieve class names from model")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load YOLO11 model: {e}")
            raise
    
    def find_objects_on_screen(self, target_classes: List[str] = None, 
                             confidence_threshold: float = None) -> List[Dict]:
        """
        Find objects on screen using YOLO11 model.
        
        Args:
            target_classes: List of class names to look for (e.g., ['close_ad', 'skip_ad'])
            confidence_threshold: Minimum confidence score (overrides config if provided)
            
        Returns:
            List of detected objects with their locations and metadata
        """
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Use config confidence or provided threshold
            conf_threshold = confidence_threshold or self.config.confidence
            
            # Run YOLO inference
            results = self.model.predict(
                screenshot_cv, 
                conf=conf_threshold,
                verbose=False
            )
            
            detected_objects = []
            
            if results and len(results) > 0:
                result = results[0]  # Get first result
                
                if result.boxes is not None and len(result.boxes) > 0:
                    # Convert to supervision format for easier handling
                    detections = sv.Detections.from_ultralytics(result)
                    
                    for i, (bbox, confidence, class_id) in enumerate(zip(
                        detections.xyxy, detections.confidence, detections.class_id
                    )):
                        class_name = self.class_names.get(int(class_id), f"class_{class_id}")
                        
                        # Filter by target classes if specified
                        if target_classes and class_name not in target_classes:
                            continue
                            
                        x1, y1, x2, y2 = bbox
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        obj_info = {
                            'class_name': class_name,
                            'confidence': float(confidence),
                            'center_point': pyscreeze.Point(center_x, center_y),
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'width': int(x2 - x1),
                            'height': int(y2 - y1)
                        }
                        
                        detected_objects.append(obj_info)
                        
                        self.logger.debug(
                            f"🎯 Found {class_name} at ({center_x}, {center_y}) "
                            f"with confidence {confidence:.2f}"
                        )
            
            self.logger.info(f"🔍 YOLO detection found {len(detected_objects)} objects")
            return detected_objects
            
        except Exception as e:
            self.logger.error(f"❌ Error during YOLO detection: {e}")
            return []
    
    def find_best_match(self, target_classes: List[str], 
                       confidence_threshold: float = None) -> Optional[Dict]:
        """
        Find the best matching object from target classes.
        
        Args:
            target_classes: List of class names to look for
            confidence_threshold: Minimum confidence score
            
        Returns:
            Best matching object info or None
        """
        detected_objects = self.find_objects_on_screen(target_classes, confidence_threshold)
        
        if not detected_objects:
            return None
            
        # Return the object with highest confidence
        best_match = max(detected_objects, key=lambda obj: obj['confidence'])
        
        self.logger.info(
            f"✅ Best match: {best_match['class_name']} "
            f"(confidence: {best_match['confidence']:.2f})"
        )
        
        return best_match
    
    def find_class_on_screen(self, class_name: str, 
                           confidence_threshold: float = None) -> Optional[pyscreeze.Point]:
        """
        Find a specific class on screen and return its center point.
        This method maintains compatibility with the existing image_handler interface.
        
        Args:
            class_name: Name of the class to find
            confidence_threshold: Minimum confidence score
            
        Returns:
            Center point of the detected object or None
        """
        best_match = self.find_best_match([class_name], confidence_threshold)
        
        if best_match:
            return best_match['center_point']
        return None
    
    def wait_for_class(self, class_name: str, timeout: int = 60, 
                      confidence_threshold: float = None) -> bool:
        """
        Wait for a specific class to appear on screen.
        
        Args:
            class_name: Name of the class to wait for
            timeout: Maximum time to wait in seconds
            confidence_threshold: Minimum confidence score
            
        Returns:
            True if class was found, False if timeout
        """
        self.logger.info(f"⏳ Waiting for {class_name} to appear...")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < timeout:
            check_count += 1
            self.logger.debug(f"🔍 Check #{check_count} for {class_name}")
            
            point = self.find_class_on_screen(class_name, confidence_threshold)
            if point:
                self.logger.info(f"✅ {class_name} found!")
                return True
            
            time.sleep(2)  # Check every 2 seconds
        
        self.logger.warning(f"⚠️ {class_name} not found after {timeout} seconds")
        return False
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            'model_path': str(self.model_path),
            'class_names': self.class_names,
            'num_classes': len(self.class_names) if self.class_names else 0
        }
    
    def save_annotated_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot and save it with YOLO detections annotated.
        Useful for debugging.
        
        Args:
            filename: Optional filename for the saved image
            
        Returns:
            Path to the saved annotated image
        """
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"yolo_detection_{timestamp}.png"
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Run YOLO inference
            results = self.model.predict(
                screenshot_cv, 
                conf=self.config.confidence,
                verbose=False
            )
            
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    # Convert to supervision format
                    detections = sv.Detections.from_ultralytics(result)
                    
                    # Create annotators
                    box_annotator = sv.BoxAnnotator()
                    label_annotator = sv.LabelAnnotator()
                    
                    # Create labels
                    labels = [
                        f"{self.class_names.get(int(class_id), f'class_{class_id}')} {confidence:.2f}"
                        for confidence, class_id in zip(detections.confidence, detections.class_id)
                    ]
                    
                    # Annotate image
                    annotated_image = box_annotator.annotate(
                        scene=screenshot_cv.copy(), 
                        detections=detections
                    )
                    annotated_image = label_annotator.annotate(
                        scene=annotated_image, 
                        detections=detections, 
                        labels=labels
                    )
                else:
                    annotated_image = screenshot_cv
            else:
                annotated_image = screenshot_cv
            
            # Save image
            save_path = Path(self.config.log_dir) / filename
            cv2.imwrite(str(save_path), annotated_image)
            
            self.logger.info(f"📸 Annotated screenshot saved: {save_path}")
            return str(save_path)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save annotated screenshot: {e}")
            return ""