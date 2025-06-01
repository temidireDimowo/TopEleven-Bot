"""
Configuration classes and enums for the Game Automation Bot.
"""

import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any


class ClickType(Enum):
    """Enumeration for different click types."""
    DEFAULT = "default"
    BLUESTACKS = "bluestacks"


@dataclass
class BotConfig:
    """Configuration class for bot settings."""
    delay: float = 0.1
    confidence: float = 0.65
    move_duration: float = 0.2
    images_dir: str = "images"
    log_dir: str = "logs"
    target_image: str = "ProductLogo.png"
    
    @classmethod
    def from_json(cls, config_path: str = "config.json") -> "BotConfig":
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            BotConfig instance with loaded settings
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            logging.warning(f"Config file {config_path} not found. Using default settings.")
            return cls()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Create instance with loaded data, falling back to defaults for missing keys
            return cls(
                delay=config_data.get('delay', 0.1),
                confidence=config_data.get('confidence', 0.65),
                move_duration=config_data.get('move_duration', 0.2),
                images_dir=config_data.get('images_dir', 'images'),
                log_dir=config_data.get('log_dir', 'logs'),
                target_image=config_data.get('target_image', 'ProductLogo.png')
            )
            
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file {config_path}: {e}")
            logging.info("Using default configuration.")
            return cls()
        except Exception as e:
            logging.error(f"Error loading config file {config_path}: {e}")
            logging.info("Using default configuration.")
            return cls()
    
    def to_json(self, config_path: str = "config.json") -> bool:
        """
        Save current configuration to JSON file.
        
        Args:
            config_path: Path where to save the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_data = asdict(self)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save config to {config_path}: {e}")
            return False
    
    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration values from a dictionary.
        
        Args:
            updates: Dictionary of configuration updates
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logging.info(f"Updated config: {key} = {value}")
            else:
                logging.warning(f"Unknown config key: {key}")
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        issues = []
        
        # Validate numeric ranges
        if not (0.01 <= self.delay <= 5.0):
            issues.append(f"delay ({self.delay}) should be between 0.01 and 5.0")
        
        if not (0.1 <= self.confidence <= 1.0):
            issues.append(f"confidence ({self.confidence}) should be between 0.1 and 1.0")
        
        if not (0.01 <= self.move_duration <= 2.0):
            issues.append(f"move_duration ({self.move_duration}) should be between 0.01 and 2.0")
        
        # Validate paths
        if not self.images_dir.strip():
            issues.append("images_dir cannot be empty")
        
        if not self.log_dir.strip():
            issues.append("log_dir cannot be empty")
        
        if not self.target_image.strip():
            issues.append("target_image cannot be empty")
        
        # Check if images directory exists
        images_path = Path(self.images_dir)
        if not images_path.exists():
            issues.append(f"images_dir '{self.images_dir}' does not exist")
        
        # Log issues
        for issue in issues:
            logging.error(f"Config validation error: {issue}")
        
        return len(issues) == 0
    
    def __str__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"BotConfig("
            f"delay={self.delay}, "
            f"confidence={self.confidence}, "
            f"move_duration={self.move_duration}, "
            f"images_dir='{self.images_dir}', "
            f"log_dir='{self.log_dir}', "
            f"target_image='{self.target_image}')"
        )