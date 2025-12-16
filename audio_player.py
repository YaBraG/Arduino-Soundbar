import os

# Try pygame for multi-format playback
try:
    import pygame
    _PYGAME_OK = True
except Exception:
    _PYGAME_OK = False

import winsound  # wav-only fallback

_pygame_inited = False

def _init_pygame():
    global _pygame_inited
    if _PYGAME_OK and not _pygame_inited:
        pygame.mixer.init()
        _pygame_inited = True

def play_audio(file_path: str) -> None:
    try:
        if not file_path:
            print("[AUDIO] No file path provided.")
            return

        if not os.path.isfile(file_path):
            print(f"[AUDIO] File does not exist: {file_path}")
            return

        ext = os.path.splitext(file_path)[1].lower()
        print(f"[AUDIO] Playing: {file_path}")

        # Use pygame when available (supports many formats)
        if _PYGAME_OK:
            _init_pygame()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            return

        # Fallback: winsound only for wav
        if ext == ".wav":
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            print("[AUDIO] Non-wav file but pygame not available. Install pygame to play this format.")

    except Exception as e:
        print(f"[AUDIO ERROR] Failed to play '{file_path}': {e}")
