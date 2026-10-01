# Talking Clock Python Library

A cross-platform Python library and test suite for a **Talking Clock** that evaluates time as integer hours, minutes, and seconds, builds the corresponding MP3 playback sequence, and auto-detects system commands to play audio on **macOS**, **Linux**, and **Windows**.

---

## 🎵 How It Works

1. Evaluates hour, minute, and second as integers (e.g. `09:05:07` -> `hour = 9`, `minute = 5`, `second = 7`).
2. Generates the exact MP3 playback sequence using the pattern:
   $$\text{begintime.mp3} \rightarrow \text{\{hour\}.mp3} \rightarrow \text{hour.mp3} \rightarrow \text{\{minute\}.mp3} \rightarrow \text{minute.mp3} \rightarrow \text{\{second\}.mp3} \rightarrow \text{second.mp3} \rightarrow \text{endtime.mp3}$$

   **Example for `09:05:07`:**
   `begintime.mp3` $\rightarrow$ `9.mp3` $\rightarrow$ `hour.mp3` $\rightarrow$ `5.mp3` $\rightarrow$ `minute.mp3` $\rightarrow$ `7.mp3` $\rightarrow$ `second.mp3` $\rightarrow$ `endtime.mp3`

3. Auto-detects available system audio players across OS platforms using `shutil.which`.

---

## 💻 Supported OS Audio Players

| Operating System | Supported System Commands (in auto-detection priority) |
| :--- | :--- |
| **macOS (`darwin`)** | `afplay` (native), `ffplay`, `mpv`, `vlc`, `cvlc` |
| **Linux** | `play` (SoX), `paplay` (PulseAudio), `mpg123`, `mpg321`, `ffplay`, `mpv`, `cvlc`, `vlc`, `aplay` |
| **Windows (`win32` / `nt`)** | `powershell` (WMPlayer COM / SoundPlayer), `cmd` (`cmd /c start /wait`), `wmplayer`, `ffplay`, `mpv`, `vlc` |

---

## 📁 Repository Structure

```
talking-clock/
├── mp3-thai-clock/      # 65 MP3 files (0.mp3 - 59.mp3, begintime.mp3, endtime.mp3, hour.mp3, minute.mp3, second.mp3)
├── talking_clock/       # Core Python Library Package
│   ├── __init__.py      # Package export and convenience function
│   ├── clock.py         # TalkingClock class (time sequence builder & audio trigger)
│   ├── player.py        # SystemAudioPlayer class (cross-platform OS player detector)
│   └── exceptions.py    # Custom exception classes
├── tests/               # Automated unit tests
│   ├── test_clock.py    # Unit tests for clock sequence & pattern verification
│   └── test_player.py   # Unit tests for OS player detection & mock execution
├── test_talking_clock.py# Main CLI test runner & interactive test tool
├── example.py           # Simple code example
└── pyproject.toml       # Python packaging definition
```

---

## 🚀 Quick Usage

### Python Code Usage

```python
from talking_clock import TalkingClock, announce_current_time

# 1. Announce current system time immediately
announce_current_time()

# 2. Or instantiate TalkingClock for custom time announcements
clock = TalkingClock(mp3_dir="mp3-thai-clock")

# Get audio file sequence for 09:05:07
seq = clock.get_sequence_for_time(hour=9, minute=5, second=7)
print(seq)

# Play audio for 09:05:07
clock.announce_time(hour=9, minute=5, second=7)
```

---

## 🧪 Running Tests & Command-Line Options

Run the test suite and CLI runner using `test_talking_clock.py`:

```bash
# 1. Run all unit tests and test example 09:05:07 time announcement:
python3 test_talking_clock.py

# 2. Run unit tests only:
python3 test_talking_clock.py --unit

# 3. Dry-run test for specific time (09:05:07):
python3 test_talking_clock.py --time 09:05:07 --dry-run

# 4. List detected system audio player & OS candidates:
python3 test_talking_clock.py --list-players

# 5. Verify all 65 required MP3 files exist in mp3-thai-clock:
python3 test_talking_clock.py --verify

# 6. Announce current system time:
python3 test_talking_clock.py --now
```

---

## 📜 Audio Licensing & Commercial Use

> [!NOTE]
> The MP3 voice audio files located in the `mp3-thai-clock/` directory were generated using **Microsoft Azure Text-to-Speech (Azure Cognitive Services Speech)** using a free subscription token from an Azure subscription.
> 
> - **Licensing & Commercial Use**: Audio assets synthesized via Azure Text-to-Speech are subject to the [Microsoft Azure Legal Terms](https://azure.microsoft.com/en-us/support/legal/) and [Azure Cognitive Services Terms](https://azure.microsoft.com/en-us/support/legal/cognitive-services-terms/).
> - If you plan to use this library or the provided audio files for commercial purposes, please ensure your usage aligns with Microsoft Azure's licensing guidelines or replace the MP3 files with your own custom or commercially licensed voice samples.

