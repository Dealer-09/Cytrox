import os
import json
from pathlib import Path
from pydantic import BaseModel, Field

class RepoShieldConfig(BaseModel):
    version: str = "1.0"
    ignored_severities: list[str] = Field(default_factory=list)
    ignored_categories: list[str] = Field(default_factory=list)
    strict_mode: bool = False

def get_config_path() -> Path:
    home = Path(os.path.expanduser("~"))
    reposhield_dir = home / ".reposhield"
    reposhield_dir.mkdir(exist_ok=True)
    return reposhield_dir / "config.json"

def load_config() -> dict:
    config_path = get_config_path()
    if not config_path.exists():
        default_cfg = RepoShieldConfig()
        save_config(default_cfg.model_dump())
        return default_cfg.model_dump()
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Validate with Pydantic
            valid_config = RepoShieldConfig(**data)
            return valid_config.model_dump()
    except Exception:
        # Fallback to default if corrupted or invalid
        default_cfg = RepoShieldConfig()
        return default_cfg.model_dump()

def save_config(config: dict):
    # Ensure it's valid before saving
    try:
        valid_config = RepoShieldConfig(**config)
    except Exception:
        valid_config = RepoShieldConfig()
        
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(valid_config.model_dump(), f, indent=4)