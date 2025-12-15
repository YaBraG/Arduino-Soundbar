"""
Contains the Tkinter GUI application:
- On startup: loads config and, if needed, asks user for an audio folder.
- Lets user pick COM port from a dropdown.
- Lets user set number of buttons.
- For each button, lets user choose an audio file from the selected folder.
- Start/Stop connection to Arduino.

The GUI does NOT talk directly to serial or audio; it calls callbacks supplied
by main.py so things stay modular.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config_manager import load_config, save_config
from version import APP_NAME, APP_VERSION


try:
    # Import only for listing ports in the GUI
    from serial.tools import list_ports
except ImportError:
    list_ports = None


class App(tk.Tk):
    """
    Main GUI application window.
    """

    def __init__(self, on_connect, on_disconnect, on_update_mappings):
        """
        :param on_connect: callback(port, mappings) when user clicks "Connect"
        :param on_disconnect: callback() when user clicks "Disconnect"
        :param on_update_mappings: callback(mappings) when button mappings change
        """
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")

        # Store callbacks
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_update_mappings = on_update_mappings

        # Load configuration from file
        self.config_data = load_config()

        # Internal variables
        self.audio_folder = self.config_data.get("audio_folder", "")
        self.num_buttons = tk.IntVar(value=self.config_data.get("num_buttons", 4))
        self.connected = False

        # Will hold Tkinter StringVars for each button's selected file
        self.button_file_vars = {}

        # GUI sections
        self._create_folder_section()
        self._create_port_section()
        self._create_buttons_section()
        self._create_control_section()

        # If no folder is set or folder doesn't exist, ask user to choose it
        if not self.audio_folder or not os.path.isdir(self.audio_folder):
            self._select_audio_folder()

        # Initially build the button rows
        self._rebuild_button_rows()

        # Apply stored button file mappings from config
        self._apply_stored_mappings()

        # Make sure GUI size adapts nicely
        self.minsize(600, 400)

    # -------------------------------------------------------------------------
    # Folder section
    # -------------------------------------------------------------------------
    def _create_folder_section(self):
        """
        Creates the section of the GUI related to choosing the audio folder.
        """
        frame = ttk.LabelFrame(self, text="Audio Folder")
        frame.pack(fill="x", padx=10, pady=5)

        self.folder_label_var = tk.StringVar(value=self.audio_folder or "No folder selected")

        label = ttk.Label(frame, textvariable=self.folder_label_var)
        label.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        btn = ttk.Button(frame, text="Change Folder", command=self._select_audio_folder)
        btn.pack(side="right", padx=5, pady=5)

    def _select_audio_folder(self):
        """
        Opens a folder selection dialog and updates the audio folder.
        """
        new_folder = filedialog.askdirectory(title="Select Folder Containing Audio Files")
        if not new_folder:
            # User cancelled the dialog
            return

        self.audio_folder = new_folder
        self.folder_label_var.set(self.audio_folder)

        # Save to config
        self.config_data["audio_folder"] = self.audio_folder
        save_config(self.config_data)

        # After changing folder, we may want to reset button selections
        # (optional, here we just notify mappings changed).
        self._notify_mappings_changed()

    # -------------------------------------------------------------------------
    # COM port section
    # -------------------------------------------------------------------------
    def _create_port_section(self):
        """
        Creates the COM port selection section.
        """
        frame = ttk.LabelFrame(self, text="Arduino Port")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Port:").pack(side="left", padx=5, pady=5)

        self.port_combo = ttk.Combobox(frame, state="readonly", width=30)
        self.port_combo.pack(side="left", padx=5, pady=5)

        refresh_btn = ttk.Button(frame, text="Refresh", command=self._refresh_ports)
        refresh_btn.pack(side="left", padx=5, pady=5)

        # Load last used port if available
        last_port = self.config_data.get("last_port", "")
        self._refresh_ports(select_port=last_port)

    def _refresh_ports(self, select_port=None):
        """
        Refreshes the list of available COM ports and optionally selects one.
        """
        ports_display = []
        ports_values = []

        if list_ports is None:
            # If pyserial.tools.list_ports is not available
            self.port_combo["values"] = []
        else:
            for p in list_ports.comports():
                # Example: "COM3 - Arduino Uno"
                display = f"{p.device} - {p.description}"
                ports_display.append(display)
                ports_values.append(p.device)

        self.port_display_to_value = dict(zip(ports_display, ports_values))
        self.port_combo["values"] = ports_display

        # Try to reselect the given port if it's still available
        if select_port:
            for display, value in self.port_display_to_value.items():
                if value == select_port:
                    self.port_combo.set(display)
                    break

    def get_selected_port(self):
        """
        Returns the selected port (e.g. 'COM3') or '' if none.
        """
        display = self.port_combo.get()
        if not display:
            return ""
        return self.port_display_to_value.get(display, "")

    # -------------------------------------------------------------------------
    # Button mapping section
    # -------------------------------------------------------------------------
    def _create_buttons_section(self):
        """
        Creates the section where the user chooses number of buttons and audio files.
        """
        outer_frame = ttk.LabelFrame(self, text="Buttons / Audio Mapping")
        outer_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Row for number of buttons
        top_row = ttk.Frame(outer_frame)
        top_row.pack(fill="x", pady=5)

        ttk.Label(top_row, text="Number of buttons:").pack(side="left", padx=5)
        spin = ttk.Spinbox(top_row, from_=1, to=32, width=5, textvariable=self.num_buttons, command=self._on_num_buttons_changed)
        spin.pack(side="left", padx=5)

        # Frame to contain the button rows
        self.buttons_frame = ttk.Frame(outer_frame)
        self.buttons_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _on_num_buttons_changed(self):
        """
        Called when the user changes the number of buttons.
        Rebuilds the button mapping rows.
        """
        self._rebuild_button_rows()
        # Update config
        self.config_data["num_buttons"] = int(self.num_buttons.get())
        save_config(self.config_data)
        self._notify_mappings_changed()

    def _rebuild_button_rows(self):
        """
        Clears and recreates the button mapping rows according to num_buttons.
        """
        # Clear existing rows
        for child in self.buttons_frame.winfo_children():
            child.destroy()

        self.button_file_vars.clear()

        # Create new rows
        for i in range(1, int(self.num_buttons.get()) + 1):
            row = ttk.Frame(self.buttons_frame)
            row.pack(fill="x", pady=2)

            btn_label_text = f"Btn {i}:"
            ttk.Label(row, text=btn_label_text, width=10).pack(side="left", padx=5)

            var = tk.StringVar(value="")
            self.button_file_vars[f"BTN{i}"] = var

            # The “slider” behavior is approximated by a readonly combo of files
            combo = ttk.Combobox(row, textvariable=var, width=40, state="readonly")
            combo.pack(side="left", padx=5, pady=2, expand=True, fill="x")

            select_btn = ttk.Button(row, text="Select audio", command=lambda btn_id=f"BTN{i}": self._select_audio_for_button(btn_id))
            select_btn.pack(side="left", padx=5, pady=2)

        # Populate combos with current folder's files
        self._populate_all_combos()

    def _populate_all_combos(self):
        """
        Updates each button's dropdown with the list of audio files in the folder.
        """
        files = self._list_audio_files_in_folder()
        for btn_id, var in self.button_file_vars.items():
            # Find the Combobox widget associated with this variable
            for row in self.buttons_frame.winfo_children():
                combo_boxes = [w for w in row.winfo_children() if isinstance(w, ttk.Combobox)]
                if combo_boxes and combo_boxes[0].cget("textvariable") == str(var):
                    combo_boxes[0]["values"] = files

    def _list_audio_files_in_folder(self):
        """
        Returns a list of audio file names in the current audio folder.
        Currently filters by extension (.wav only for simplicity).
        """
        if not self.audio_folder or not os.path.isdir(self.audio_folder):
            return []

        allowed_exts = {".wav"}  # You can expand this set if desired
        files = []
        for name in os.listdir(self.audio_folder):
            full_path = os.path.join(self.audio_folder, name)
            if os.path.isfile(full_path):
                _, ext = os.path.splitext(name)
                if ext.lower() in allowed_exts:
                    files.append(name)
        return files

    def _select_audio_for_button(self, btn_id):
        """
        Allows the user to pick a specific file for a single button
        by opening a file dialog starting in the audio folder.
        """
        if not self.audio_folder:
            messagebox.showwarning("No Folder", "Please select an audio folder first.")
            return

        # File dialog restricted to audio folder
        file_path = filedialog.askopenfilename(
            title=f"Select audio for {btn_id}",
            initialdir=self.audio_folder,
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # Only store the file name, not full path
        filename = os.path.basename(file_path)

        # Set the corresponding StringVar
        var = self.button_file_vars.get(btn_id)
        if var is not None:
            var.set(filename)
            self._notify_mappings_changed()

    def _apply_stored_mappings(self):
        """
        Loads button -> filename mappings from config and applies them to the GUI.
        """
        stored = self.config_data.get("button_files", {})
        for btn_id, filename in stored.items():
            var = self.button_file_vars.get(btn_id)
            if var is not None:
                var.set(filename)

        # Also repopulate combos in case we changed folder
        self._populate_all_combos()

    def _notify_mappings_changed(self):
        """
        Called whenever button mappings change.
        Updates config and notifies main via callback.
        """
        mappings = self.get_button_mappings()
        self.config_data["button_files"] = mappings
        save_config(self.config_data)

        if self._on_update_mappings:
            self._on_update_mappings(mappings)

    def get_button_mappings(self):
        """
        Returns a dictionary mapping 'BTN1' -> absolute file path, etc.
        """
        mappings = {}
        for btn_id, var in self.button_file_vars.items():
            filename = var.get().strip()
            if filename:
                full_path = os.path.join(self.audio_folder, filename)
                mappings[btn_id] = full_path
        return mappings

    # -------------------------------------------------------------------------
    # Connect / Disconnect section
    # -------------------------------------------------------------------------
    def _create_control_section(self):
        """
        Creates the bottom control section with Connect/Disconnect buttons.
        """
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.connect_btn = ttk.Button(frame, text="Connect", command=self._on_click_connect)
        self.connect_btn.pack(side="left", padx=5, pady=5)

        self.disconnect_btn = ttk.Button(frame, text="Disconnect", command=self._on_click_disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=5, pady=5)

    def _on_click_connect(self):
        """
        Handles the Connect button click.
        """
        port = self.get_selected_port()
        if not port:
            messagebox.showwarning("No Port Selected", "Please select an Arduino port first.")
            return

        mappings = self.get_button_mappings()
        if not mappings:
            if not messagebox.askyesno("No Mappings", "No buttons are mapped to audio files. Connect anyway?"):
                return

        # Save last port in config
        self.config_data["last_port"] = port
        save_config(self.config_data)

        # Call the external callback to actually start the serial listener
        if self._on_connect and self._on_connect(port, mappings):
            self.connected = True
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")

    def _on_click_disconnect(self):
        """
        Handles the Disconnect button click.
        """
        if self._on_disconnect:
            self._on_disconnect()

        self.connected = False
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")

    # -------------------------------------------------------------------------
    # Helper for processing serial messages safely in the GUI thread
    # -------------------------------------------------------------------------
    def handle_serial_message(self, msg):
        """
        Schedules processing of a serial message in the Tkinter main thread.
        This function can be called from any thread (e.g. serial listener).
        """
        self.after(0, self._process_serial_message, msg)

    def _process_serial_message(self, msg):
        """
        This runs in the Tkinter main thread.
        Right now it just logs; main.py will attach actual behavior.
        """
        print(f"[GUI] Received from Arduino: {msg}")
