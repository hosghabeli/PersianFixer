import os
import json

SETTINGS_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "PersianFixer")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "auto_patch": True,
    "notify": True,
    "check_interval": 30
}

def load_settings() -> dict:
    """Loads settings from JSON file, falling back to defaults."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with defaults in case new keys were added
            settings = DEFAULT_SETTINGS.copy()
            settings.update(data)
            return settings
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict) -> bool:
    """Saves settings to JSON file in AppData."""
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_setting(key: str, default=None):
    """Retrieves a single setting value."""
    settings = load_settings()
    return settings.get(key, default)

def set_setting(key: str, value) -> bool:
    """Updates and saves a single setting."""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)
