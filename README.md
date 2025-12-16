# 🎧 Arduino Audio Stream Deck (Arduino Soundbar)

A customizable **hardware soundboard** that uses an Arduino Uno/Nano and a Windows desktop application.
Press a physical button → Arduino sends a serial message → the PC instantly plays the assigned audio file.

This project is built to be simple, modular, and stable when compiled into a Windows `.exe`.

---

## 🚀 Features

### PC Application
- Tkinter-based GUI
- Select any folder containing **WAV** audio files
- Adjustable number of buttons (1–32)
- Each button can be assigned a different WAV file
- Drop-down selection of available COM ports (similar to Arduino IDE)
- Automatically remembers:
  - Last selected audio folder
  - Button → audio mappings
  - Number of buttons
  - Last used COM port
- Uses **winsound** for stable non-blocking audio playback inside `.exe`
- No crashes when audio finishes (fixed)

### Arduino
- Uses digital pins with `INPUT_PULLUP`
- Sends messages like `BTN1`, `BTN2`, `BTN3` over Serial
- Debounced and triggers only once per physical press

---

## ✅ Windows Install (Recommended)

### Install
1. Go to this repository’s **Releases** page.
2. Download **Install_ArduinoSoundbar.bat** (from the latest release assets).
3. Double-click it.
4. Press **ENTER** to install to the default location, or type a custom folder:
   - Default: `Documents\Arduino Soundbar`
5. A **Desktop shortcut** will be created automatically.

> Windows may show a “Protected your PC” warning because the app is not code-signed.
> Click **More info** → **Run anyway**.

### Update
To update to the latest version, simply run **Install_ArduinoSoundbar.bat** again.

---

## 🧩 System Architecture

```

[Buttons] → [Arduino] → USB Serial → [PC Stream Deck App] → [WAV Playback]

```

- Arduino handles hardware button presses.
- The PC app plays the corresponding audio.

---

## 📁 Project Structure

```

Arduino-Soundbar/
├─ main.py                     # Entry point: ties GUI, Serial Listener, Audio Player
├─ gui.py                      # Tkinter GUI (folder selection, mappings, COM ports)
├─ serial_listener.py          # Background thread that reads Arduino serial data
├─ audio_player.py             # Plays WAV files using winsound (non-blocking)
├─ config_manager.py           # Saves/loads config.json (next to the .exe)
├─ version.py                  # App name + version displayed in the title bar
├─ config.default.json         # Clean default config template (repo only)
├─ Install_ArduinoSoundbar.bat # One-click installer launcher (user downloads this)
├─ Install_ArduinoSoundbar.ps1 # Installer logic (downloads release zip, makes shortcut)
├─ requirements.txt            # Runtime deps (pyserial)
├─ README.md
└─ arduino_buttons.ino         # Arduino firmware for Uno/Nano

```

---

## 🔌 Arduino Hardware Setup

### Components
- Arduino Uno or Nano
- One momentary push button per audio trigger
- Jumper wires
- USB cable
- (Optional) custom enclosure

### Wiring
Each button goes between an Arduino pin and **GND**.

Example for 4 buttons:

```

Pin 2 ----[Button]---- GND
Pin 3 ----[Button]---- GND
Pin 4 ----[Button]---- GND
Pin 5 ----[Button]---- GND

````

Arduino code uses internal pull-ups:

```cpp
pinMode(pin, INPUT_PULLUP);
````

Logic:

* Not pressed → HIGH
* Pressed → LOW
* On press: Arduino sends `"BTN1"`, `"BTN2"`, …

The full code is in `arduino_buttons.ino`.

---

## 🎚️ Using the Application

### Step 1 — Select Audio Folder

Choose a folder containing your `.wav` sound files.
The app remembers this folder on the next launch.

### Step 2 — Select Arduino COM Port

Use the COM drop-down to select the connected board.

### Step 3 — Set Number of Buttons

Choose how many hardware buttons your Arduino has.

### Step 4 — Assign Audio Files

For each button:

* Pick a WAV file from the drop-down, or
* Use “Select audio” to browse for a WAV file

### Step 5 — Connect

The application starts listening for Arduino serial messages.

### Step 6 — Press Physical Buttons

The corresponding WAV file plays immediately (non-blocking, no crashes).

---

## 🛠️ Developer Setup (Optional)

> Users should install from **Releases** using the one-click installer.
> This section is only for developers who want to run from source or build locally.

### Run from source

```bash
pip install -r requirements.txt
python main.py
```

### Build the Windows Executable (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name Soundbar main.py
```

The executable appears in:

```
dist/Soundbar.exe
```

At runtime the application creates:

```
config.json
```

next to the `.exe` on first run.

---

## 📜 License

This project is released under the **MIT License**.
See `LICENSE` file for details.