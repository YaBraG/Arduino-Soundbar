"""
main.py
Entry point of the application.

- Creates the GUI (App).
- Sets up the serial listener when user clicks Connect.
- When a message (e.g. 'BTN1') comes in from Arduino, plays the mapped audio file.
"""

from gui import App
from serial_listener import SerialListener
from audio_player import play_audio


class Controller:
    """
    High-level controller that connects GUI, serial listener, and audio playback.
    """

    def __init__(self):
        # No serial listener until user clicks Connect
        self.serial_listener = None

        # Dictionary like: 'BTN1' -> 'C:\\path\\to\\sound1.wav'
        self.button_mappings = {}

        # Create GUI and pass callbacks
        self.app = App(
            on_connect=self.handle_connect,
            on_disconnect=self.handle_disconnect,
            on_update_mappings=self.handle_update_mappings
        )

    # -------------------------------------------------------------------------
    # GUI callbacks
    # -------------------------------------------------------------------------
    def handle_connect(self, port, mappings):
        """
        Called by the GUI when user clicks Connect.
        :param port: Selected COM port (e.g. 'COM3')
        :param mappings: Current button -> file path mapping
        :return: True on success, False otherwise
        """
        print(f"[CTRL] Connecting to {port}...")
        self.button_mappings = mappings

        # Define how to handle a line coming from the Arduino
        def on_serial_line(line):
            # Delegate message handling to the GUI-safe method
            self.app.handle_serial_message(line)
            self._handle_arduino_message(line)

        # Create and start serial listener
        self.serial_listener = SerialListener(port=port, baud_rate=9600, line_callback=on_serial_line)
        ok = self.serial_listener.start()
        if not ok:
            self.serial_listener = None
        return ok

    def handle_disconnect(self):
        """
        Called by the GUI when user clicks Disconnect.
        """
        print("[CTRL] Disconnect requested.")
        if self.serial_listener:
            self.serial_listener.stop()
            self.serial_listener = None

    def handle_update_mappings(self, mappings):
        """
        Called by the GUI whenever button -> file mappings change.
        """
        print("[CTRL] Updating mappings.")
        self.button_mappings = mappings

    # -------------------------------------------------------------------------
    # Arduino messages
    # -------------------------------------------------------------------------
    def _handle_arduino_message(self, msg):
        """
        Processes messages from Arduino.
        Expected format: 'BTN1', 'BTN2', etc.
        """
        try:
            msg = msg.strip()
            if not msg:
                return

            print(f"[CTRL] Arduino message: {msg}")

            if msg in self.button_mappings:
                file_path = self.button_mappings[msg]
                print(f"[CTRL] Playing mapped sound: {file_path}")
                # This is now non-blocking thanks to audio_player.py
                play_audio(file_path)
            else:
                print(f"[CTRL] No audio mapped for '{msg}'")
        except Exception as e:
            # This prevents unexpected exceptions from killing the program
            print(f"[CTRL ERROR] Exception while handling message '{msg}': {e}")

    # -------------------------------------------------------------------------
    # Run the app
    # -------------------------------------------------------------------------
    def run(self):
        """
        Starts the Tkinter main loop.
        """
        self.app.mainloop()


if __name__ == "__main__":
    controller = Controller()
    controller.run()
