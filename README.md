# Arduino Soundbar

Arduino Soundbar is a desktop application that turns an Arduino into a configurable soundboard controller.  
Physical buttons connected to an Arduino trigger audio files on a Windows PC with **low latency**, **fast retrigger**, and **reliable overlap behavior**.

The project is designed to be simple, fast, and robust under rapid button presses.

---

## 🧩 Project Overview

**System flow:**

Arduino → Serial (USB) → PC App → Audio Playback

- Arduino sends button events (`BTN1`, `BTN2`, etc.)
- PC app listens over serial
- Each button triggers a mapped audio file
- Playback behavior depends on the selected stop mode

---

## ✨ Features

- 🎛️ Map Arduino buttons to audio files
- 🔊 True audio overlap across different buttons
- ⚡ Instant retrigger on the same button
- 🔁 Toggle between stop modes using an Arduino button
- 🖥️ Simple GUI for configuration
- 📦 Standalone Windows `.exe` for end users

---

## 🔌 Arduino Setup

### Hardware
- Any Arduino board with USB serial support (Uno, Nano, Mega, etc.)
- Momentary push buttons wired to digital input pins
- Internal pullups recommended

Example wiring:
- Button → Digital Pin
- Other side → GND

---

### Arduino Firmware (Concept)

The Arduino **only sends text messages over serial** when buttons are pressed.

Example messages:
```

BTN1
BTN2
BTN3
TOGGLE

```

> The PC application does **not** control the Arduino — it only listens.

Basic logic:
- Detect button press
- Send a single line over `Serial.println()`

Debouncing can be done either:
- In Arduino code (recommended), or
- On the hardware side

---

## 🔄 Serial Protocol

- Baud rate: **9600** (default)
- Line-based messages (`\n`)
- Messages are case-sensitive by convention

### Button Messages
```

BTN1
BTN2
BTN3
...

```

### Toggle Message
```

TOGGLE

````

The toggle message switches playback modes on the PC.

---

## 🎚️ Stop Modes

The app supports two playback modes:

### SAME (Overlap Mode)
- Pressing the **same button** restarts its sound
- Pressing **different buttons** allows sounds to overlap
- Ideal for soundboards and layered effects

### ANY (Exclusive Mode)
- Any button press stops all currently playing audio
- Only one sound plays at a time

### Toggle Button Behavior
- A dedicated Arduino button can toggle between `SAME` and `ANY`
- **Pressing the toggle button immediately stops all audio** (v1.0.5)

---

## 🔊 Audio Engine Details

- Uses `pygame.mixer`
- Each Arduino button is assigned a **dedicated audio channel**
- Prevents random cutoffs caused by pygame channel stealing
- Audio files are cached in memory for instant replay
- Mixer pre-allocates channels for stability under rapid presses

Supported formats depend on pygame (commonly `.wav`, `.mp3`, `.ogg`).

---

## 🧪 Tested Scenarios

- Rapidly spamming the same button
- Alternating between two or more buttons
- Holding one button while pressing others
- Toggling modes while audio is playing

All scenarios behave deterministically as of **v1.0.5**.

---

## 🖥️ Running from Source (Developers)

### Requirements
- Windows
- Python 3.10+
- USB-connected Arduino

Install dependencies:
```powershell
pip install -r requirements.txt
````

Run:

```powershell
python main.py
```

---

## 📦 Building the EXE (Windows)

Clean build with icon:

```powershell
pyinstaller --noconfirm --clean --onefile --noconsole `
  --name "Soundbar" `
  --icon "icon.ico" `
  main.py
```

After building:

```powershell
Copy-Item ".\icon.ico" ".\dist\icon.ico" -Force
```

Final output:

```
dist/
 ├─ Soundbar.exe
 └─ icon.ico
```

---

## 🧾 Version History

### v1.0.5

* Stop any ongoing audio when the toggle button is pressed

### v1.0.4

* Fix overlap mode where some sounds failed to overlap under rapid presses
* Assign dedicated pygame audio channels per button (BTN1, BTN2, etc.)
* Preserve fast retrigger behavior while allowing true cross-button overlap
* Improve mixer stability by pre-allocating channels

### v1.0.3

* Fix dropdown mappings and path resolution
* Auto-refresh audio dropdowns
* Multi-format audio playback
* Updated Windows icon support

---

## 📌 Notes

* `dist/` and `build/` folders are **not committed** to GitHub
* `.exe` files are distributed via **GitHub Releases**
* Arduino firmware is intentionally minimal and customizable

---

## 📬 Feedback & Testing

When reporting issues, include:

* Button pressed (`BTN#`)
* Stop mode (`SAME` / `ANY`)
* Audio format
* Whether the toggle button was used
* Whether running from source or `.exe`

This helps isolate edge cases quickly.
