import os

try:
    import pygame
    _PYGAME_OK = True
except Exception:
    _PYGAME_OK = False

import winsound  # fallback for wav if pygame not available

_pygame_inited = False
_sound_cache = {}      # file_path -> pygame Sound
_channel_by_btn = {}   # "BTN1" -> pygame Channel (fixed channel per button)

# Give ourselves plenty of mixer channels so overlap is reliable even when
# buttons are spammed rapidly (fast retrigger) or many buttons exist.
_DEFAULT_NUM_CHANNELS = 64


def _init_pygame():
    """
    Initialize pygame mixer exactly once.
    Also pre-allocate a healthy channel pool so pygame doesn't steal channels
    during rapid re-triggers / overlap scenarios.
    """
    global _pygame_inited
    if _PYGAME_OK and not _pygame_inited:
        pygame.mixer.init()

        # IMPORTANT:
        # If we let pygame auto-pick channels via Sound.play(), it can "steal"
        # channels under load (rapid presses), which makes some sounds cut off
        # instead of overlapping. We fix this by pre-allocating a lot of
        # channels and assigning a dedicated Channel per button.
        pygame.mixer.set_num_channels(_DEFAULT_NUM_CHANNELS)
        _pygame_inited = True


def _ensure_min_channels(min_channels: int) -> None:
    """Ensure the mixer has at least `min_channels` channels available."""
    if not (_PYGAME_OK and _pygame_inited):
        return

    try:
        current = pygame.mixer.get_num_channels()
        if current < min_channels:
            pygame.mixer.set_num_channels(max(min_channels, _DEFAULT_NUM_CHANNELS))
    except Exception:
        # Fail soft if something is odd in a specific environment.
        pass


def _get_fixed_channel_for_button(btn_id: str):
    """
    Return a dedicated pygame Channel for the given button id.

    Deterministic mapping:
      BTN1 -> channel 0
      BTN2 -> channel 1
      ...
    """
    if btn_id in _channel_by_btn:
        return _channel_by_btn[btn_id]

    idx = None

    # Try to parse "BTN<number>"
    try:
        if btn_id.upper().startswith("BTN"):
            idx = int(btn_id[3:]) - 1
            if idx < 0:
                idx = None
    except Exception:
        idx = None

    # Fallback for unexpected ids: allocate next available slot.
    if idx is None:
        idx = len(_channel_by_btn)

    _ensure_min_channels(idx + 1)

    ch = pygame.mixer.Channel(idx)
    _channel_by_btn[btn_id] = ch
    return ch


def stop_all_audio() -> None:
    """Stops all currently playing audio (pygame only)."""
    if _PYGAME_OK and _pygame_inited:
        pygame.mixer.stop()
        # Keep the channel mapping; we reuse fixed channels per button.


def play_audio(btn_id: str, file_path: str, stop_mode: str = "SAME") -> None:
    """
    stop_mode:
      - "ANY": stop ALL audio whenever any button plays
      - "SAME": stop only the previous audio from the same btn_id
               (overlap across different buttons stays intact)
    """
    try:
        if not file_path or not os.path.isfile(file_path):
            print(f"[AUDIO] File not found: {file_path}")
            return

        # pygame path (multi-format + overlap control)
        if _PYGAME_OK:
            _init_pygame()

            # Cache decoded audio so repeat triggers are instant.
            if file_path not in _sound_cache:
                _sound_cache[file_path] = pygame.mixer.Sound(file_path)

            sound = _sound_cache[file_path]

            # Dedicated channel per button = no channel stealing across buttons.
            ch = _get_fixed_channel_for_button(btn_id)

            if stop_mode == "ANY":
                # Stop everything, then play on this button's fixed channel.
                stop_all_audio()
                ch.play(sound)
                return

            # stop_mode == "SAME"
            # Fast retrigger behavior: stop only THIS button's channel, then replay.
            ch.stop()
            ch.play(sound)
            return

        # winsound fallback (wav only)
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".wav":
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            print("[AUDIO] Non-wav file but pygame not available.")

    except Exception as e:
        print(f"[AUDIO ERROR] {e}")
