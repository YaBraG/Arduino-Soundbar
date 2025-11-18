# Arduino Audio Stream Deck

A customizable **hardware soundboard** using an Arduino Uno/Nano + a desktop GUI app.
Press a physical button → Arduino sends a message → Your PC instantly plays the assigned audio file.

This project is built to be clean, modular, and easy to extend. The PC app supports:

* Selecting any folder containing WAV audio files
* Mapping each button (BTN1, BTN2, …) to any sound
* Customizable number of buttons
* Automatic detection of connected Arduino COM ports
* Auto-remembering of last audio folder, button mappings, and port
* Exporting to a **Windows .exe** (PyInstaller)

---

##  Features

### ✔️ PC App (GUI)

* Modern Tkinter interface
* “Select Audio Folder” button
* Drop-down selection of COM ports
* Adjustable number of buttons (1–32)
* Each button has:

  * “Select audio” file picker
  * A drop-down list showing all audio files in the folder
* Automatic saving/loading of:

  * Last selected folder
  * Selected audio for each button
  * Last used COM port
  * Number of buttons

### ✔️ Arduino Side

* Simple and reliable
* Uses digital pins with `INPUT_PULLUP`
* Sends messages like `BTN1`, `BTN2`, `BTN3`, etc. over serial
* Zero latency, debounced, only triggers once per press

### ✔️ Audio Playback

* Uses the `simpleaudio` library for instant WAV playback
* Works even when compiled as `.exe`

---

## 🧩 System Architecture

```
[Physical Buttons] → [Arduino UNO/Nano] → USB Serial → [Windows GUI App] → [Audio Playback]
```

* Arduino just tells the PC *which* button was pressed.
* The PC app decides *which sound* to play.

---

## 📁 Project Structure

```
audio_stream_deck/
├─ main.py              # Entry point; ties together GUI + Serial Listener + Audio player
├─ gui.py               # All Tkinter GUI code
├─ serial_listener.py   # Background reading of Serial data (multi-threaded)
├─ audio_player.py      # Plays WAV files via simpleaudio
├─ config_manager.py    # Loads/saves last folder, port, mappings, etc.
├─ requirements.txt     # Python packages required
└─ arduino_buttons.ino  # Arduino sketch for UNO/Nano
```

Each file is intentionally separated for clean organization and easy readability.

---

## 🔌 Arduino Hardware Setup

### Components Needed

* Arduino Uno or Nano
* Momentary push buttons
* Wires
* Optional: enclosure or 3D-printed panel

### Wiring Diagram

Use **internal pull-up resistors** for simplicity:

```
Button → Pin 2
Button → Pin 3
Button → Pin 4
Button → Pin 5
... etc.
```

Each button should connect like this:

```
[Pin X] ----[Button]---- GND
```

And in code:

```cpp
pinMode(buttonPins[i], INPUT_PULLUP);
```

This means:

* **Not pressed** → HIGH
* **Pressed** → LOW

---

## 🎛️ Arduino Code

The board sends `"BTN1"`, `"BTN2"`, etc. whenever you press buttons:

```cpp
Serial.print("BTN");
Serial.println(i + 1);
```

The PC app listens for these exact strings.

Full Arduino code is provided in the repo:
`arduino_buttons.ino`

---

## 🖥️ Installing the PC App

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the app (Python version)

```
python main.py
```

### 3. Build a standalone `.exe`

```
pyinstaller --onefile --noconsole main.py
```

Your executable will be created in:

```
dist/main.exe
```

---

## 🎚️ How to Use the App

### 1. Launch `main.exe`

The UI appears.

### 2. Select your **Audio Folder**

The app remembers the last folder automatically.

### 3. Choose your **COM Port**

The drop-down lists all available ports, similar to the Arduino IDE.

### 4. Set **Number of Buttons**

Choose how many hardware buttons your build has.

### 5. Map Each Button to a Sound

Press **“Select Audio”** for each button to choose a WAV file.

### 6. Press **Connect**

The app starts listening to the Arduino.

### 7. Press your physical button

The chosen audio plays instantly.

---

## 🧠 How It Works Internally

### Arduino → PC (Serial)

* Each press generates `"BTN<number>"` over USB serial.

### PC → Audio

* The background serial thread receives the message
* `Controller` matches it to a file
* `audio_player.play_audio()` plays the WAV

### Persistent Settings

* Saved to `config.json` next to the `.exe`
* Restored automatically at each launch
