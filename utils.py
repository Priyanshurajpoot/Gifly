# utils.py
import json
import os
import shutil
import tempfile
import sys

APP_NAME = "Gifly"

def get_config_dir():
    """
    Return a sensible config dir for Gifly.
    - On Linux: ~/.config/Gifly
    - On macOS: ~/Library/Application Support/Gifly
    - On Windows: %APPDATA%\\Gifly
    """
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        appdata = os.getenv('APPDATA') or os.path.join(home, 'AppData', 'Roaming')
        cfg = os.path.join(appdata, APP_NAME)
    elif sys.platform == "darwin":
        cfg = os.path.join(home, "Library", "Application Support", APP_NAME)
    else:
        cfg = os.path.join(home, ".config", APP_NAME)
    os.makedirs(cfg, exist_ok=True)
    return cfg

SETTINGS_FILE = os.path.join(get_config_dir(), "settings.json")

def load_settings():
    """Load settings from JSON file with error handling"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Validate and provide defaults
                return validate_settings(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load settings: {e}")
            return get_default_settings()
    return get_default_settings()

def save_settings(data):
    """Save settings to JSON file atomically"""
    try:
        # Validate before saving
        validated_data = validate_settings(data)
        
        # Atomic write: write to temp file then move
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=get_config_dir())
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(validated_data, f, indent=4, ensure_ascii=False)
            # Atomic replace
            shutil.move(tmp_path, SETTINGS_FILE)
        except Exception as e:
            print(f"Warning: Atomic save failed: {e}")
            # Fallback non-atomic
            try:
                with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(validated_data, f, indent=4, ensure_ascii=False)
            except Exception as inner_e:
                print(f"Error: Could not save settings: {inner_e}")
        finally:
            # Ensure tmp doesn't remain
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
    except Exception as e:
        print(f"Error in save_settings: {e}")

def get_default_settings():
    """Return default settings structure"""
    return {
        "playlist": [],
        "last_index": -1,
        "last_position": 0,
        "volume": 70,
        "gifs": [],
        "song_gifs": {},
        "shuffle": False,
        "repeat_mode": "none",
        "dock_geometry": None,
        "window_geometry": None,
        "playlists": {},
        "theme": "dark"
    }

def validate_settings(data):
    """Validate and sanitize settings data"""
    defaults = get_default_settings()
    
    # Ensure all required keys exist
    for key, default_value in defaults.items():
        if key not in data:
            data[key] = default_value
    
    # Type validation
    if not isinstance(data.get("playlist"), list):
        data["playlist"] = []
    
    if not isinstance(data.get("last_index"), int):
        data["last_index"] = -1
    
    if not isinstance(data.get("last_position"), (int, float)):
        data["last_position"] = 0
    
    # Clamp volume to 0-100
    volume = data.get("volume", 70)
    if not isinstance(volume, (int, float)):
        volume = 70
    data["volume"] = max(0, min(100, int(volume)))
    
    if not isinstance(data.get("gifs"), list):
        data["gifs"] = []
    
    if not isinstance(data.get("song_gifs"), dict):
        data["song_gifs"] = {}
    
    if not isinstance(data.get("shuffle"), bool):
        data["shuffle"] = False
    
    if data.get("repeat_mode") not in ["none", "one", "all"]:
        data["repeat_mode"] = "none"
    
    # Validate dock geometry
    if data.get("dock_geometry") is not None:
        if not isinstance(data["dock_geometry"], list) or len(data["dock_geometry"]) != 4:
            data["dock_geometry"] = None
    
    # Validate window geometry
    if data.get("window_geometry") is not None:
        if not isinstance(data["window_geometry"], list) or len(data["window_geometry"]) != 4:
            data["window_geometry"] = None
    
    return data

def format_time(milliseconds):
    """Convert milliseconds to MM:SS format"""
    if milliseconds < 0:
        return "0:00"
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"