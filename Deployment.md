# 🚀 Deployment Document for “Run 3”
**Author:** Nayan Patel  
**Last Updated:** April 2025  
**Project Type:** Python (Pygame) 2D Side-Scrolling Game  

---

## 📦 Project Overview  
**Run 3** is a 2D arcade-style runner featuring dynamic movement mechanics, shooting enemies, collectible powerups, environmental hazards (spikes, meteorites), glowing animations, and reactive UI elements.

---

## 🖥️ System Requirements

### Minimum:
- OS: Windows 10, macOS 10.15+, Linux Ubuntu 20.04+
- Python 3.8+
- Pygame 2.0+
- RAM: 4 GB
- Graphics: Integrated (supports SDL)

### Recommended:
- Python 3.11+
- Sound card for music playback
- 60Hz monitor for optimal frame sync

---

## 📁 Directory Structure
```
Run3/
├── run3.py               # Main game file
├── space_synth.mp3       # Background music
├── assets/               # (Optional) folder for sprites or future expansion
├── README.md             # Project overview
├── requirements.txt      # Python dependencies
└── deployment_doc.md     # This deployment document
```

---

## 🧰 Dependencies

Create a `requirements.txt` file with:
```
pygame==2.5.2
```

Install dependencies via:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup Instructions

1. **Clone or Download the Repository:**
   ```bash
   git clone https://github.com/FuriousNayan/run3.py.git
   cd run3.py
   ```

2. **Install Python (if not installed):**  
   Download from: https://www.python.org/downloads/

3. **Install Dependencies:**
   ```bash
   pip install pygame
   ```

4. **Ensure Music File Exists:**
   - The game depends on `space_synth.mp3`.
   - Place this file in the same directory as the script or adjust the path in `start_music()`:
     ```python
     pygame.mixer.music.load("space_synth.mp3")
     ```

5. **Run the Game:**
   ```bash
   python run3.py
   ```

---

## 🧪 Testing

- Run in a terminal or IDE (VS Code / PyCharm).
- Test controls:
  - Arrow Keys: Move
  - Spacebar: Jump / Interact
  - Left Shift: Dash
  - `P`: Pause / Resume
  - `R`: Restart (after death)

---

## 🎵 Media Assets

**Background Music**:  
- File: `space_synth.mp3`  
- Must be loopable  
- Recommended: Royalty-free synthwave track (~1–2 min loop)

---

## 🛠️ Deployment Tips

- To **package into an executable** (Windows):
  ```bash
  pip install pyinstaller
  pyinstaller --onefile --windowed run3.py
  ```
  Output will be in `dist/`.

- For **web deployment**, consider converting with [Pygbag](https://pygame-web.github.io/pygame-web/) (experimental).

---

## 🧯 Troubleshooting

| Issue                        | Solution                                             |
|-----------------------------|------------------------------------------------------|
| Music not playing           | Verify `space_synth.mp3` is present and supported    |
| No sound                    | Ensure `pygame.mixer.init()` runs without error      |
| Game lags or crashes        | Try reducing FPS or object spawn rates               |
| `pygame.error: No available video device` | Use a GUI-enabled environment (not WSL) |

---

## 📌 Future Improvements (Optional)

- Add level selection or save system
- Optimize particle effects for lower-end hardware
- Add mobile control support
- Integrate settings menu with volume sliders
- Replace placeholders with sprite artwork
