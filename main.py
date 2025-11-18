"""
PC-side Python script.
Listens to Arduino over serial.
When codes like 'BTN1' are received, plays an associated audio file.

Make sure to:
- Change COM_PORT to your actual Arduino port (e.g. 'COM3' or '/dev/ttyUSB0').
- Change AUDIO_FOLDER if needed.
"""

import serial           # For serial communication with Arduino
import simpleaudio as sa  # For playing audio files
import os               # For working with file paths

# ------------------- USER SETTINGS -------------------

# Replace with your Arduino COM port
# On Windows: something like 'COM3'
# On Linux: something like '/dev/ttyACM0' or '/dev/ttyUSB0'
COM_PORT = "COM3"

# Baud rate must match Serial.begin() on Arduino
BAUD_RATE = 9600

# Folder where your audio files live
AUDIO_FOLDER = r"C:\soundboard"

# Map Arduino messages to audio file names
# e.g. if Arduino sends "BTN1", we play BTN1.wav
button_to_file = {
    "BTN1": "BTN1.wav",
    "BTN2": "BTN2.wav",
    "BTN3": "BTN3.wav",
    "BTN4": "BTN4.wav",
}

# ------------------- FUNCTIONS -------------------

def play_sound(filename):
    """
    Plays the given WAV file (blocking) using simpleaudio.
    """
    file_path = os.path.join(AUDIO_FOLDER, filename)

    if not os.path.isfile(file_path):
        print(f"[WARN] Audio file not found: {file_path}")
        return

    try:
        # Load WAV file into memory
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        # Start playback
        play_obj = wave_obj.play()
        # Optionally, wait for playback to finish
        # Comment out the next line if you want non-blocking behavior
        play_obj.wait_done()
    except Exception as e:
        print(f"[ERROR] Failed to play {file_path}: {e}")


def main():
    """
    Main loop:
    - Open serial port
    - Read text lines from Arduino
    - When a known button code is received, play the corresponding sound
    """
    print(f"[INFO] Opening serial port {COM_PORT} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"[ERROR] Could not open serial port {COM_PORT}: {e}")
        return

    print("[INFO] Serial port opened. Waiting for button presses...")
    print("[INFO] Press Ctrl+C to exit.\n")

    try:
        while True:
            # Read a line from Serial (as bytes)
            line_bytes = ser.readline()

            # If nothing was read (timeout), continue the loop
            if not line_bytes:
                continue

            # Convert from bytes to string and strip whitespace/newline
            line = line_bytes.decode(errors="ignore").strip()

            if not line:
                continue

            print(f"[DEBUG] Received from Arduino: '{line}'")

            # Check if the received message maps to an audio file
            if line in button_to_file:
                filename = button_to_file[line]
                print(f"[INFO] Playing sound for {line}: {filename}")
                play_sound(filename)
            else:
                print(f"[WARN] Unrecognized code: '{line}'")

    except KeyboardInterrupt:
        print("\n[INFO] Exiting by user request.")
    finally:
        ser.close()
        print("[INFO] Serial port closed.")


if __name__ == "__main__":
    main()
