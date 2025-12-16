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
import sys

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

        # Set window icon (fixes Tk "feather" title icon)
        try:
            if getattr(sys, "frozen", False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.abspath(".")

            icon_path = os.path.join(base_dir, "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"[GUI] Could not set icon: {e}")

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

        # NEW: Stop mode + toggle button selection
        self.stop_mode_var = tk.StringVar(value=self.config_data.get("stop_mode", "SAME"))
        self.toggle_btn_var = tk.StringVar(value=self.config_data.get("toggle_button_id", ""))

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
        self._schedule_auto_refresh_files()

        # Apply stored button file mappings from config
        self._apply_stored_mappings()

        # Make sure GUI size adapts nicely
        self.minsize(600, 400)

    # -------------------------------------------------------------------------
    # Folder section
    # -------------------------------------------------------------------------
    def _create_folder_section(self):
        frame = ttk.LabelFrame(self, text="Audio Folder")
        frame.pack(fill="x", padx=10, pady=5)

        self.folder_label_var = tk.StringVar(value=self.audio_folder or "No folder selected")

        label = ttk.Label(frame, textvariable=self.folder_label_var)
        label.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        btn = ttk.Button(frame, text="Change Folder", command=self._select_audio_folder)
        btn.pack(side="right", padx=5, pady=5)

    def _select_audio_folder(self):
        new_folder = filedialog.askdirectory(title="Select Folder Containing Audio Files")
        if not new_folder:
            return

        self.audio_folder = new_folder
        self.folder_label_var.set(self.audio_folder)

        # Save to config
        self.config_data["audio_folder"] = self.audio_folder
        save_config(self.config_data)

        self._notify_mappings_changed()

    # -------------------------------------------------------------------------
    # COM port section (+ NEW toggle controls)
    # -------------------------------------------------------------------------
    def _create_port_section(self):
        frame = ttk.LabelFrame(self, text="Arduino Port")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Port:").pack(side="left", padx=5, pady=5)

        self.port_combo = ttk.Combobox(frame, state="readonly", width=30)
        self.port_combo.pack(side="left", padx=5, pady=5)

        refresh_btn = ttk.Button(frame, text="Refresh", command=self._refresh_ports)
        refresh_btn.pack(side="left", padx=5, pady=5)

        # NEW: Toggle button selection
        ttk.Label(frame, text="Toggle BTN:").pack(side="left", padx=(15, 2), pady=5)
        toggle_options = [""] + [f"BTN{i}" for i in range(1, 33)]
        self.toggle_combo = ttk.Combobox(frame, state="readonly", width=7,
                                         textvariable=self.toggle_btn_var,
                                         values=toggle_options)
        self.toggle_combo.pack(side="left", padx=5, pady=5)
        self.toggle_combo.bind("<<ComboboxSelected>>", lambda e: self._save_toggle_settings())

        # NEW: Stop mode display (read-only label)
        self.mode_label_var = tk.StringVar(value=self._mode_label_text(self.stop_mode_var.get()))
        mode_lbl = ttk.Label(frame, textvariable=self.mode_label_var)
        mode_lbl.pack(side="left", padx=(15, 5), pady=5)

        # Load last used port if available
        last_port = self.config_data.get("last_port", "")
        self._refresh_ports(select_port=last_port)

        # Ensure UI reflects loaded config
        self._save_toggle_settings(save_only=True)

    def _mode_label_text(self, mode: str) -> str:
        if mode == "ANY":
            return "Mode: ANY (stop all)"
        return "Mode: SAME (overlap)"

    def _save_toggle_settings(self, save_only: bool = False):
        """
        Save toggle button + stop mode to config.
        """
        self.config_data["toggle_button_id"] = self.toggle_btn_var.get().strip()
        self.config_data["stop_mode"] = self.stop_mode_var.get().strip() or "SAME"
        save_config(self.config_data)

        # Keep label updated
        self.mode_label_var.set(self._mode_label_text(self.stop_mode_var.get()))

        # Optionally notify main that settings changed
        if not save_only and self._on_update_mappings:
            self._on_update_mappings(self.get_button_mappings())

    def set_stop_mode(self, mode: str):
        """
        Called by main.py when the toggle button is pressed.
        Updates GUI + saves config.
        """
        if mode not in ("SAME", "ANY"):
            return
        self.stop_mode_var.set(mode)
        self._save_toggle_settings(save_only=True)

    def get_toggle_button_id(self) -> str:
        return self.toggle_btn_var.get().strip()

    def get_stop_mode(self) -> str:
        mode = self.stop_mode_var.get().strip()
        return mode if mode in ("SAME", "ANY") else "SAME"

    def _refresh_ports(self, select_port=None):
        ports_display = []
        ports_values = []

        if list_ports is None:
            self.port_combo["values"] = []
        else:
            for p in list_ports.comports():
                display = f"{p.device} - {p.description}"
                ports_display.append(display)
                ports_values.append(p.device)

        self.port_display_to_value = dict(zip(ports_display, ports_values))
        self.port_combo["values"] = ports_display

        if select_port:
            for display, value in self.port_display_to_value.items():
                if value == select_port:
                    self.port_combo.set(display)
                    break

    def get_selected_port(self):
        display = self.port_combo.get()
        if not display:
            return ""
        return self.port_display_to_value.get(display, "")

    # -------------------------------------------------------------------------
    # Button mapping section
    # -------------------------------------------------------------------------
    def _create_buttons_section(self):
        outer_frame = ttk.LabelFrame(self, text="Buttons / Audio Mapping")
        outer_frame.pack(fill="both", expand=True, padx=10, pady=5)

        top_row = ttk.Frame(outer_frame)
        top_row.pack(fill="x", pady=5)

        ttk.Label(top_row, text="Number of buttons:").pack(side="left", padx=5)
        spin = ttk.Spinbox(
            top_row, from_=1, to=32, width=5, textvariable=self.num_buttons,
            command=self._on_num_buttons_changed
        )
        spin.pack(side="left", padx=5)

        self.buttons_frame = ttk.Frame(outer_frame)
        self.buttons_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _on_num_buttons_changed(self):
        self._rebuild_button_rows()
        self.config_data["num_buttons"] = int(self.num_buttons.get())
        save_config(self.config_data)
        self._notify_mappings_changed()

    def _rebuild_button_rows(self):
        for child in self.buttons_frame.winfo_children():
            child.destroy()

        self.button_file_vars.clear()

        for i in range(1, int(self.num_buttons.get()) + 1):
            row = ttk.Frame(self.buttons_frame)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=f"Btn {i}:", width=10).pack(side="left", padx=5)

            var = tk.StringVar(value="")
            self.button_file_vars[f"BTN{i}"] = var

            combo = ttk.Combobox(row, textvariable=var, width=40, state="readonly")
            combo.pack(side="left", padx=5, pady=2, expand=True, fill="x")
            combo.bind("<Button-1>", lambda e: self._populate_all_combos())
            combo.bind("<<ComboboxSelected>>", self._on_dropdown_selected)

            select_btn = ttk.Button(row, text="Select audio",
                                    command=lambda btn_id=f"BTN{i}": self._select_audio_for_button(btn_id))
            select_btn.pack(side="left", padx=5, pady=2)

        self._populate_all_combos()

    def _populate_all_combos(self):
        files = self._list_audio_files_in_folder()
        for btn_id, var in self.button_file_vars.items():
            for row in self.buttons_frame.winfo_children():
                combo_boxes = [w for w in row.winfo_children() if isinstance(w, ttk.Combobox)]
                if combo_boxes and combo_boxes[0].cget("textvariable") == str(var):
                    combo_boxes[0]["values"] = files

    def _list_audio_files_in_folder(self):
        if not self.audio_folder or not os.path.isdir(self.audio_folder):
            return []

        allowed_exts = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".wma"}
        files = []
        for name in os.listdir(self.audio_folder):
            full_path = os.path.join(self.audio_folder, name)
            if os.path.isfile(full_path):
                _, ext = os.path.splitext(name)
                if ext.lower() in allowed_exts:
                    files.append(name)
        return files

    def _on_dropdown_selected(self, event=None):
        self._notify_mappings_changed()

    def _select_audio_for_button(self, btn_id):
        if not self.audio_folder:
            messagebox.showwarning("No Folder", "Please select an audio folder first.")
            return

        file_path = filedialog.askopenfilename(
            title=f"Select audio for {btn_id}",
            initialdir=self.audio_folder,
            filetypes=[
                ("Audio files", "*.wav;*.mp3;*.ogg;*.flac;*.m4a;*.aac;*.wma"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return

        filename = os.path.basename(file_path)

        var = self.button_file_vars.get(btn_id)
        if var is not None:
            var.set(filename)
            self._notify_mappings_changed()

    def _apply_stored_mappings(self):
        stored = self.config_data.get("button_files", {})
        for btn_id, value in stored.items():
            var = self.button_file_vars.get(btn_id)
            if var is not None and value:
                var.set(os.path.basename(value))

        self._populate_all_combos()

    def _notify_mappings_changed(self):
        mappings = self.get_button_mappings()
        self.config_data["button_files"] = mappings
        save_config(self.config_data)

        if self._on_update_mappings:
            self._on_update_mappings(mappings)

    def get_button_mappings(self):
        mappings = {}
        for btn_id, var in self.button_file_vars.items():
            value = var.get().strip()
            if value:
                mappings[btn_id] = os.path.basename(value)
        return mappings

    # -------------------------------------------------------------------------
    # Connect / Disconnect section
    # -------------------------------------------------------------------------
    def _create_control_section(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.connect_btn = ttk.Button(frame, text="Connect", command=self._on_click_connect)
        self.connect_btn.pack(side="left", padx=5, pady=5)

        self.disconnect_btn = ttk.Button(frame, text="Disconnect", command=self._on_click_disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=5, pady=5)

    def _on_click_connect(self):
        port = self.get_selected_port()
        if not port:
            messagebox.showwarning("No Port Selected", "Please select an Arduino port first.")
            return

        mappings = self.get_button_mappings()
        if not mappings:
            if not messagebox.askyesno("No Mappings", "No buttons are mapped to audio files. Connect anyway?"):
                return

        self.config_data["last_port"] = port
        save_config(self.config_data)

        if self._on_connect and self._on_connect(port, mappings):
            self.connected = True
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")

    def _on_click_disconnect(self):
        if self._on_disconnect:
            self._on_disconnect()

        self.connected = False
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")

    # -------------------------------------------------------------------------
    # Helper for processing serial messages safely in the GUI thread
    # -------------------------------------------------------------------------
    def handle_serial_message(self, msg):
        self.after(0, self._process_serial_message, msg)

    def _process_serial_message(self, msg):
        print(f"[GUI] Received from Arduino: {msg}")

    def _schedule_auto_refresh_files(self):
        self._populate_all_combos()
        self.after(2000, self._schedule_auto_refresh_files)
