"""
Handles saving/loading configuration such as:
- last audio folder
- number of buttons
- which audio file is mapped to each button
- last used COM port
- toggle button id (optional)
- stop mode (SAME vs ANY)
"""

import json
import os
import sys

# Name of the config file that will live next to the .exe / script
CONFIG_FILENAME = "config.json"


def get_app_dir():
    """
    Returns the directory where the script or .exe is located.
    This works both for Python and PyInstaller builds.
    """
    if getattr(sys, "frozen", False):
        # Running from PyInstaller .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as a normal Python script
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    """
    Returns the full path to the config.json file.
    """
    return os.path.join(get_app_dir(), CONFIG_FILENAME)


def load_config():
    """
    Loads the configuration from disk.
    If it doesn't exist, returns a default config dictionary.
    """
    path = get_config_path()

    default_config = {
        "audio_folder": "",
        "num_buttons": 4,
        "button_files": {},          # key: "BTN1", value: "filename.wav"
        "last_port": "",
        "toggle_button_id": "",      # e.g. "BTN10" or "" (disabled)
        "stop_mode": "SAME"          # "SAME" or "ANY"
    }

    if not os.path.isfile(path):
        return default_config

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return default_config

    # Ensure required keys exist (migrate older configs)
    for k, v in default_config.items():
        if k not in data:
            data[k] = v

    # Validate stop_mode
    if data.get("stop_mode") not in ("SAME", "ANY"):
        data["stop_mode"] = "SAME"

    # Validate toggle_button_id format (allow "" or "BTN<number>")
    t = str(data.get("toggle_button_id", "")).strip()
    data["toggle_button_id"] = t

    return data


def save_config(config):
    """
    Saves the configuration dictionary to disk.
    """
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")
