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
    DEFAULT = "default"
    BLUESTACKS = "bluestacks"


@dataclass
class BotConfig:
    # Input timing
    delay: float = 0.1
    confidence: float = 0.65
    move_duration: float = 0.2

    # Paths
    images_dir: str = "Assets"
    log_dir: str = "logs/text"
    screenshot_dir: str = "logs/screenshots"
    target_image: str = "ProductLogo.png"
    top_eleven_dir: str = "Assets/TopEleven"
    close_dir: str = "Assets/TopEleven/Ads/close"
    skip_dir: str = "Assets/TopEleven/Ads/skip"

    # YOLO detection
    yolo_model_path: str = "models/best.pt"
    yolo_confidence: float = 0.5
    yolo_enabled: bool = True
    fallback_to_traditional: bool = True

    # Farming
    max_greens: int = 25
    ad_wait_timeout: int = 90
    cycle_interval: int = 5

    # Debug
    debug_mode: bool = False
    save_annotated_on_failure: bool = True
    detection_log_max_entries: int = 500
    screenshot_on_cycle_start: bool = False

    @classmethod
    def from_json(cls, config_path: str = "config.json") -> "BotConfig":
        config_file = Path(config_path)
        if not config_file.exists():
            logging.warning(f"Config file {config_path} not found. Using defaults.")
            return cls()
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                d = json.load(f)
            return cls(
                delay=d.get('delay', 0.1),
                confidence=d.get('confidence', 0.65),
                move_duration=d.get('move_duration', 0.2),
                images_dir=d.get('images_dir', 'Assets'),
                log_dir=d.get('log_dir', 'logs/text'),
                screenshot_dir=d.get('screenshot_dir', 'logs/screenshots'),
                target_image=d.get('target_image', 'ProductLogo.png'),
                top_eleven_dir=d.get('top_eleven_dir', 'Assets/TopEleven'),
                close_dir=d.get('close_dir', 'Assets/TopEleven/Ads/close'),
                skip_dir=d.get('skip_dir', 'Assets/TopEleven/Ads/skip'),
                yolo_model_path=d.get('yolo_model_path', 'models/best.pt'),
                yolo_confidence=d.get('yolo_confidence', 0.5),
                yolo_enabled=d.get('yolo_enabled', True),
                fallback_to_traditional=d.get('fallback_to_traditional', True),
                max_greens=d.get('max_greens', 25),
                ad_wait_timeout=d.get('ad_wait_timeout', 90),
                cycle_interval=d.get('cycle_interval', 5),
                debug_mode=d.get('debug_mode', False),
                save_annotated_on_failure=d.get('save_annotated_on_failure', True),
                detection_log_max_entries=d.get('detection_log_max_entries', 500),
                screenshot_on_cycle_start=d.get('screenshot_on_cycle_start', False),
            )
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {config_path}: {e}")
            return cls()
        except Exception as e:
            logging.error(f"Error loading {config_path}: {e}")
            return cls()

    def to_json(self, config_path: str = "config.json") -> bool:
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, indent=4, ensure_ascii=False)
            logging.info(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to save config to {config_path}: {e}")
            return False

    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logging.warning(f"Unknown config key: {key}")

    def validate(self) -> bool:
        issues = []

        if not (0.01 <= self.delay <= 5.0):
            issues.append(f"delay ({self.delay}) must be 0.01–5.0")
        if not (0.1 <= self.confidence <= 1.0):
            issues.append(f"confidence ({self.confidence}) must be 0.1–1.0")
        if not (0.01 <= self.move_duration <= 2.0):
            issues.append(f"move_duration ({self.move_duration}) must be 0.01–2.0")
        if not (0.1 <= self.yolo_confidence <= 1.0):
            issues.append(f"yolo_confidence ({self.yolo_confidence}) must be 0.1–1.0")
        if self.max_greens < 1:
            issues.append(f"max_greens must be >= 1")
        if self.ad_wait_timeout < 30:
            issues.append(f"ad_wait_timeout must be >= 30s")

        # Ensure required directories exist (create them if missing)
        for attr in ('log_dir', 'screenshot_dir'):
            Path(getattr(self, attr)).mkdir(parents=True, exist_ok=True)

        for issue in issues:
            logging.error(f"Config validation error: {issue}")

        return len(issues) == 0

    def __str__(self) -> str:
        return (
            f"BotConfig(delay={self.delay}, confidence={self.confidence}, "
            f"yolo_enabled={self.yolo_enabled}, yolo_confidence={self.yolo_confidence}, "
            f"max_greens={self.max_greens}, ad_wait_timeout={self.ad_wait_timeout}s)"
        )
