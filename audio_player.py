import os

try:
    import pygame
    _PYGAME_OK = True
except Exception:
    _PYGAME_OK = False

import winsound  # fallback for wav if pygame not available

_pygame_inited = False
_sound_cache = {}      # file_path -> pygame Sound
_channel_by_btn = {}   # "BTN1" -> pygame Channel


def _init_pygame():
    global _pygame_inited
    if _PYGAME_OK and not _pygame_inited:
        pygame.mixer.init()
        _pygame_inited = True


def stop_all_audio() -> None:
    """Stops all currently playing audio (pygame only)."""
    if _PYGAME_OK and _pygame_inited:
        pygame.mixer.stop()
        _channel_by_btn.clear()


def play_audio(btn_id: str, file_path: str, stop_mode: str = "SAME") -> None:
    """
    stop_mode:
      - "ANY": stop ALL audio whenever any button plays
      - "SAME": stop only the previous audio from the same btn_id
    """
    try:
        if not file_path or not os.path.isfile(file_path):
            print(f"[AUDIO] File not found: {file_path}")
            return

        # pygame path (multi-format + overlap control)
        if _PYGAME_OK:
            _init_pygame()

            if file_path not in _sound_cache:
                _sound_cache[file_path] = pygame.mixer.Sound(file_path)

            sound = _sound_cache[file_path]

            if stop_mode == "ANY":
                stop_all_audio()
                ch = sound.play()
                if ch is not None:
                    _channel_by_btn[btn_id] = ch
                return

            # stop_mode == "SAME"
            old_ch = _channel_by_btn.get(btn_id)
            if old_ch is not None:
                old_ch.stop()

            ch = sound.play()  # allows overlap across different buttons
            if ch is not None:
                _channel_by_btn[btn_id] = ch
            return

        # winsound fallback (wav only)
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".wav":
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            print("[AUDIO] Non-wav file but pygame not available.")

    except Exception as e:
        print(f"[AUDIO ERROR] {e}")
