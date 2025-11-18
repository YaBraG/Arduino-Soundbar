"""
Plays WAV audio files on Windows using the built-in winsound module.
Playback is asynchronous so it does not block the GUI or serial listener.
"""

import os
import winsound  # Windows-only standard library module


def play_audio(file_path: str) -> None:
    """
    Play the given WAV file asynchronously.

    :param file_path: Absolute path to a .wav file.
    """
    try:
        # Ensure we got a valid path
        if not file_path:
            print("[AUDIO] No file path provided.")
            return

        if not os.path.isfile(file_path):
            print(f"[AUDIO] File does not exist: {file_path}")
            return

        print(f"[AUDIO] Playing: {file_path}")

        # winsound.PlaySound:
        # - SND_FILENAME: treat the string as a filename
        # - SND_ASYNC: return immediately, play in the background
        winsound.PlaySound(
            file_path,
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )

    except Exception as e:
        # Any exception here will be printed but NOT kill the program
        print(f"[AUDIO ERROR] Failed to play '{file_path}': {e}")
