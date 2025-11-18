"""
Provides a simple function to play an audio file (WAV) using simpleaudio.
"""

import os
import simpleaudio as sa


def play_audio(file_path):
    """
    Plays the given WAV file.
    This function is blocking by default (waits until playback finishes).
    """
    if not file_path:
        print("[WARN] No file path provided for playback.")
        return

    if not os.path.isfile(file_path):
        print(f"[WARN] Audio file does not exist: {file_path}")
        return

    try:
        # Load the WAV file into memory
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        # Start playing
        play_obj = wave_obj.play()
        # Wait until it finishes playing
        play_obj.wait_done()
    except Exception as e:
        print(f"[ERROR] Failed to play '{file_path}': {e}")
