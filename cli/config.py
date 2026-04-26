import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "ignored_severities": [],
    "ignored_categories": [],
    "strict_mode": False
}

def get_config_path() -> Path:
    home = Path(os.path.expanduser("~"))
    reposhield_dir = home / ".reposhield"
    reposhield_dir.mkdir(exist_ok=True)
    return reposhield_dir / "config.json"

def load_config() -> dict:
    config_path = get_config_path()
    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback to default if corrupted
        return DEFAULT_CONFIG

def save_config(config: dict):
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
