# 🎧 Arduino Audio Stream Deck

A customizable **hardware soundboard** that uses an Arduino Uno/Nano and a Windows desktop application.
Press a physical button → Arduino sends a serial message → the PC instantly plays the assigned audio file.

This project is built to be simple, modular, and stable when compiled into a Windows `.exe`.

---

## 🚀 Features

### PC Application

* Tkinter-based GUI
* Select any folder containing **WAV** audio files
* Adjustable number of buttons (1–32)
* Each button can be assigned a different WAV file
* Drop-down selection of available COM ports (similar to Arduino IDE)
* Automatically remembers:

  * Last selected audio folder
  * Button → audio mappings
  * Number of buttons
  * Last used COM port
* Uses **winsound** for 100% stable non-blocking audio playback inside `.exe`
* No crashes when audio finishes (fixed)

### Arduino

* Uses digital pins with `INPUT_PULLUP`
* Sends messages like `BTN1`, `BTN2`, `BTN3` over Serial
* Debounced and triggers only once per physical press

---

## 🧩 System Architecture

```
[Buttons] → [Arduino] → USB Serial → [PC Stream Deck App] → [WAV Playback]
```

* Arduino handles hardware button presses.
* The PC app plays the corresponding audio.

---

## 📁 Project Structure

```
Arduino-Soundbar/
├─ main.py              # Entry point: ties GUI, Serial Listener, Audio Player
├─ gui.py               # Tkinter GUI (folder selection, mappings, COM ports)
├─ serial_listener.py   # Background thread that reads Arduino serial data
├─ audio_player.py      # Plays WAV files using winsound (non-blocking)
├─ config_manager.py    # Saves/loads config.json (folder, mappings, port)
├─ requirements.txt     # Only pyserial needed for build
└─ arduino_buttons.ino  # Arduino firmware for Uno/Nano
```

### ✔️ Updated differences from the previous version

* `simpleaudio` removed
* `winsound` added (built-in, stable, no blocking)
* `audio_player.py` rewritten to be asynchronous
* No external audio dependencies in `.exe`
* Program no longer closes after audio completion

---

## 🔌 Arduino Hardware Setup

### Components

* Arduino Uno or Nano
* One momentary push button per audio trigger
* Jumper wires
* USB cable
* (Optional) custom enclosure

### Wiring

Each button goes between an Arduino pin and **GND**.

Example for 4 buttons:

```
Pin 2 ----[Button]---- GND
Pin 3 ----[Button]---- GND
Pin 4 ----[Button]---- GND
Pin 5 ----[Button]---- GND
```

Arduino code uses internal pull-ups:

```cpp
pinMode(pin, INPUT_PULLUP);
```

Logic:

* Not pressed → HIGH
* Pressed → LOW
* On press: Arduino sends `"BTN1"`, `"BTN2"`, …

The full code is in `arduino_buttons.ino`.

---

## 🖥️ Installing and Running the PC Application

### 1. Install Requirements

```
pip install pyserial
```

(Only pyserial is needed — audio uses built-in winsound.)

### 2. Run Using Python

```
python main.py
```

### 3. Build the Windows Executable

You can build either a console or no-console version:

**Console version** (recommended for your first test):

```
python -m PyInstaller --onefile main.py
```

**Final production version** (no console window):

```
python -m PyInstaller --onefile --noconsole main.py
```

The executable appears in:

```
dist/main.exe
```

The application automatically creates:

```
config.json
```

next to the `.exe` on first run.

---

## 🎚️ Using the Application

### **Step 1 — Select Audio Folder**

Choose a folder containing your `.wav` sound files.
The app remembers this folder on the next launch.

### **Step 2 — Select Arduino COM Port**

Use the COM drop-down to select the connected board.

### **Step 3 — Set Number of Buttons**

Choose how many hardware buttons your Arduino has.

### **Step 4 — Assign Audio Files**

For each button:

* Use the drop-down or
* Use the “Select audio” button
  to choose a WAV file.

### **Step 5 — Connect**

The application starts listening for Arduino serial messages.

### **Step 6 — Press Your Physical Buttons**

The corresponding WAV file plays immediately (non-blocking, no crashes).

---

## 📜 License

This project is released under the **MIT License**.
See `LICENSE` file for details.

---