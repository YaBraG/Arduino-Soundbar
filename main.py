"""
main.py
Entry point of the application.

- Creates the GUI (App).
- Sets up the serial listener when user clicks Connect.
- When a message (e.g. 'BTN1') comes in from Arduino, plays the mapped audio file.
- Supports a user-selectable toggle button to switch stop mode:
    SAME = stop only same button (overlap across different buttons)
    ANY  = stop all audio when any button plays
"""

import os
from gui import App
from serial_listener import SerialListener
from audio_player import play_audio, stop_all_audio  # stop audio on toggle


class Controller:
    """
    High-level controller that connects GUI, serial listener, and audio playback.
    """

    def __init__(self):
        self.serial_listener = None
        self.button_mappings = {}

        # Playback behavior
        self.stop_mode = "SAME"        # "SAME" or "ANY"
        self.toggle_button_id = ""     # e.g. "BTN10" or "" for disabled

        self.app = App(
            on_connect=self.handle_connect,
            on_disconnect=self.handle_disconnect,
            on_update_mappings=self.handle_update_mappings
        )

        # Pull initial toggle settings from GUI/config
        self._sync_toggle_settings_from_gui()

    # -------------------------------------------------------------------------
    # GUI callbacks
    # -------------------------------------------------------------------------
    def handle_connect(self, port, mappings):
        print(f"[CTRL] Connecting to {port}...")
        self.button_mappings = mappings

        # Also sync toggle settings at connect time
        self._sync_toggle_settings_from_gui()

        def on_serial_line(line):
            self.app.handle_serial_message(line)
            self._handle_arduino_message(line)

        self.serial_listener = SerialListener(port=port, baud_rate=9600, line_callback=on_serial_line)
        ok = self.serial_listener.start()
        if not ok:
            self.serial_listener = None
        return ok

    def handle_disconnect(self):
        print("[CTRL] Disconnect requested.")
        if self.serial_listener:
            self.serial_listener.stop()
            self.serial_listener = None

    def handle_update_mappings(self, mappings):
        print("[CTRL] Updating mappings.")
        self.button_mappings = mappings

        # Also sync toggle settings whenever GUI changes stuff
        self._sync_toggle_settings_from_gui()

    def _sync_toggle_settings_from_gui(self):
        """
        Pull toggle button + stop mode from GUI (if those methods exist).
        """
        if hasattr(self.app, "get_toggle_button_id"):
            self.toggle_button_id = self.app.get_toggle_button_id()

        if hasattr(self.app, "get_stop_mode"):
            self.stop_mode = self.app.get_stop_mode()

    # -------------------------------------------------------------------------
    # Arduino messages
    # -------------------------------------------------------------------------
    def _handle_arduino_message(self, msg):
        try:
            msg = msg.strip()
            if not msg:
                return

            print(f"[CTRL] Arduino message: {msg}")

            # Toggle behavior (if enabled)
            if self.toggle_button_id and msg == self.toggle_button_id:
                self.stop_mode = "ANY" if self.stop_mode == "SAME" else "SAME"
                print(f"[CTRL] Toggled stop mode -> {self.stop_mode}")
                
                stop_all_audio()  # stop any ongoing audio when toggling modes


                # Update GUI label + persist config
                if hasattr(self.app, "set_stop_mode"):
                    self.app.set_stop_mode(self.stop_mode)
                return

            if msg in self.button_mappings:
                mapped = self.button_mappings[msg]

                if os.path.isabs(mapped):
                    file_path = mapped
                else:
                    file_path = os.path.join(self.app.audio_folder, mapped)

                print(f"[CTRL] Playing {msg}: {file_path} (mode={self.stop_mode})")
                play_audio(msg, file_path, self.stop_mode)
            else:
                print(f"[CTRL] No audio mapped for '{msg}'")

        except Exception as e:
            print(f"[CTRL ERROR] Exception while handling message '{msg}': {e}")

    # -------------------------------------------------------------------------
    # Run the app
    # -------------------------------------------------------------------------
    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    controller = Controller()
    controller.run()
