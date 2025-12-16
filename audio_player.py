import os

try:
    import pygame
    _PYGAME_OK = True
except Exception:
    _PYGAME_OK = False

import winsound  # fallback for wav if pygame unavailable

_pygame_inited = False
_sound_cache = {}  # cache Sound objects for fast replay


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

        print(f"[AUDIO] Playing: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()

        # --- Preferred path: pygame Sound (fast retrigger) ---
        if _PYGAME_OK:
            _init_pygame()

            # Cache sounds so repeat presses are instant
            if file_path not in _sound_cache:
                _sound_cache[file_path] = pygame.mixer.Sound(file_path)

            sound = _sound_cache[file_path]

            # Stop + play guarantees restart-on-demand
            sound.stop()
            sound.play()
            return

        # --- Fallback: winsound (wav only) ---
        if ext == ".wav":
            winsound.PlaySound(
                file_path,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        else:
            print("[AUDIO] Non-wav file but pygame not available.")

    except Exception as e:
        print(f"[AUDIO ERROR] Failed to play '{file_path}': {e}")
