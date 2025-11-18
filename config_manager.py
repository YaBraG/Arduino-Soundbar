"""
Handles saving/loading configuration such as:
- last audio folder
- number of buttons
- which audio file is mapped to each button
- last used COM port
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

    if not os.path.isfile(path):
        # Default configuration
        return {
            "audio_folder": "",
            "num_buttons": 4,
            "button_files": {},  # key: "BTN1", value: "filename.wav"
            "last_port": ""
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # If something goes wrong reading JSON, fallback to defaults
        return {
            "audio_folder": "",
            "num_buttons": 4,
            "button_files": {},
            "last_port": ""
        }

    # Make sure important keys exist
    if "audio_folder" not in data:
        data["audio_folder"] = ""
    if "num_buttons" not in data:
        data["num_buttons"] = 4
    if "button_files" not in data:
        data["button_files"] = {}
    if "last_port" not in data:
        data["last_port"] = ""

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
