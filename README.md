# Arduino Soundbar

Arduino Soundbar is a desktop application that turns an Arduino into a customizable soundboard.  
Each Arduino button triggers an audio file on the PC with ultra-fast response, reliable overlap behavior, and flexible stop modes.

Designed for **low latency**, **rapid retriggering**, and **stable multi-button playback**.

---

## ✨ Features

- 🎛️ Map Arduino buttons (BTN1, BTN2, etc.) to audio files
- 🔊 True audio overlap across different buttons
- ⚡ Fast retrigger on the same button (instant restart)
- 🔁 Toggle between stop modes using a dedicated Arduino button
- 🖥️ Simple GUI for configuration
- 📦 Standalone `.exe` build (no Python required for users)

---

## 🎚️ Stop Modes

The app supports two playback modes:

### SAME (Overlap Mode)
- Pressing the **same button** restarts its sound
- Pressing **different buttons** allows sounds to overlap
- Best for soundboards and layered effects

### ANY (Exclusive Mode)
- Any button press stops all currently playing audio
- Only one sound plays at a time

### Toggle Button
- A dedicated Arduino button can toggle between `SAME` and `ANY`
- **Pressing the toggle button immediately stops all audio** (v1.0.5)

---

## 🔊 Audio Engine (Important)

- Uses `pygame.mixer`
- Each button is assigned a **dedicated audio channel**
- Prevents channel stealing and random cutoffs under rapid presses
- Audio files are cached for instant replay

Supported formats depend on pygame (commonly `.wav`, `.mp3`, `.ogg`).

---

## 🧪 Tested Scenarios

- Rapidly spamming the same button
- Rapidly alternating between two buttons
- Holding one button while spamming another
- Toggling modes during playback

All tested scenarios behave deterministically as of **v1.0.5**.

---

## 🖥️ Running from Source (Developers)

### Requirements
- Python 3.10+
- Windows (pygame + winsound fallback)

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

Clean build + icon:

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

Output:

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
* Arduino firmware only needs to send `BTN#` messages over serial

---

## 📬 Feedback & Testing

If something breaks:

* Note which button(s)
* Stop mode (`SAME` / `ANY`)
* Audio format
* Whether the toggle button was involved

This helps isolate timing or hardware edge cases quickly.
