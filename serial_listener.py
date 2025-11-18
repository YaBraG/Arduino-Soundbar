"""
Contains a SerialListener class that:
- Opens a COM port
- Listens for lines from the Arduino
- Calls a callback function whenever a full line (e.g. 'BTN1') is received
"""

import threading
import serial
import time


class SerialListener:
    """
    Manages a background thread that listens to serial messages.
    """

    def __init__(self, port, baud_rate, line_callback):
        """
        :param port: Serial port name (e.g. 'COM3')
        :param baud_rate: Baud rate (e.g. 9600)
        :param line_callback: Function that will receive the decoded line
        """
        self.port = port
        self.baud_rate = baud_rate
        self.line_callback = line_callback

        self._serial = None
        self._thread = None
        self._stop_flag = threading.Event()

    def start(self):
        """
        Opens the serial port and starts the listener thread.
        """
        try:
            self._serial = serial.Serial(self.port, self.baud_rate, timeout=0.2)
        except Exception as e:
            print(f"[ERROR] Could not open serial port {self.port}: {e}")
            self._serial = None
            return False

        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[INFO] Serial listener started on {self.port}")
        return True

    def _run(self):
        """
        Main loop of the listener thread.
        Reads lines from serial and calls the callback.
        """
        while not self._stop_flag.is_set():
            try:
                if self._serial is None:
                    break

                # Read one line (bytes)
                line_bytes = self._serial.readline()
                if line_bytes:
                    # Decode, strip whitespace/newlines
                    line = line_bytes.decode(errors="ignore").strip()
                    if line:
                        # Call the callback with the received line
                        self.line_callback(line)
            except Exception as e:
                print(f"[ERROR] Serial reading error: {e}")
                break

            # Small sleep to avoid tight loop
            time.sleep(0.01)

        print("[INFO] Serial listener thread stopped.")

    def stop(self):
        """
        Signals the thread to stop and closes the serial port.
        """
        self._stop_flag.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None
        print("[INFO] Serial listener fully stopped.")
