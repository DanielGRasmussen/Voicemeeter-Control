# Voicemeeter Control

Global hotkey control for Voicemeeter with visual notifications.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

- 🎮 **Global Hotkeys** - Control Voicemeeter from any application
- 🔊 **Volume Control** - Adjust volume levels with keyboard shortcuts
- 🔇 **Mute Toggle** - Quick mute/unmute for any channel
- 📊 **Visual Feedback** - On-screen notifications for all actions
- ⚙️ **Customizable** - Configure hotkeys and channels via YAML
- 🔄 **Auto-repeat** - Hold keys for continuous adjustment
- 💻 **System Tray** - Runs quietly in the background

## Requirements

- Windows 10/11 (64-bit)
- [Voicemeeter](https://vb-audio.com/Voicemeeter/) (Basic, Banana, or Potato)
- Python 3.8+ (if running from source)
- Git (if installing from source)

## Installation

### Method 1: Installer (Recommended)
1. Install Voicemeeter from https://vb-audio.com/Voicemeeter/
2. Download the latest installer from [Releases](https://github.com/danielrasmussen/voicemeeter-control/releases)
3. Run `VoicemeeterControl_Setup_vX.X.X.exe`
4. Follow the installation wizard

### Method 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/danielrasmussen/voicemeeter-control.git
cd voicemeeter-control

# Install dependencies
pip install -r requirements.txt

# Or install manually:
pip install pyqt5 pyyaml keyboard pillow
pip install git+https://github.com/chvolkmann/voicemeeter-remote-python.git

# Run the application
python voicemeeter_control.py
```

## Configuration

Edit `config.yaml` to customize your setup:

```yaml
settings:
  volume_step: 2.0    # Volume change per key press (dB)
  logging: False

channels:
  microphone: 0       # Voicemeeter strip index
  desktop: 5
  music: 6
  voicechat: 7

hotkeys:
  microphone:
    mute: 
      - "print screen"     # Primary hotkey
      - "ctrl+f13"         # Alternative hotkey
    up: "ctrl+f14"
    down: "ctrl+f15"
  
  voicechat:
    mute: "scroll lock"
    up: "home"
    down: "end"
```

### Channel Mapping

Find your Voicemeeter strip indices:
- Open Voicemeeter
- Strips are numbered left to right starting from 0
- Hardware inputs typically: 0-2
- Virtual inputs typically: 3-7

### Hotkey Format

- Single keys: `"print screen"`, `"f13"`, `"home"`
- With modifiers: `"ctrl+f14"`, `"alt+shift+m"`
- Multiple bindings: Use a list format

## Usage

1. **Start Voicemeeter** first
2. **Run Voicemeeter Control** - it minimizes to system tray
3. **Use your hotkeys** to control volume and muting
4. **Visual notifications** appear for each action

### System Tray Options
- **Pause** - Temporarily disable hotkeys
- **Restart** - Reload configuration
- **Quit** - Exit the application

## Troubleshooting

### Hotkeys not working
- Check if another application is using the same keys
- Try running as administrator
- Verify Voicemeeter is running

### Volume changes not applying
- Ensure channel indices match your Voicemeeter setup
- Check if Voicemeeter is responding to manual changes
- Try restarting both applications

### No visual notifications
- Check if notifications are blocked by Windows
- Ensure PyQt5 is properly installed
- Look for errors in the log file

## Building from Source

### Requirements
- Git (for installing the Voicemeeter library)
- Python 3.8+

```bash
# Install build dependencies
pip install pyinstaller

# Run the build script
python build_installer.py

# Or use the batch file
build_installer.bat
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Daniel Rasmussen**

## Acknowledgments

- VB-Audio for Voicemeeter
- [chvolkmann/voicemeeter-remote-python](https://github.com/chvolkmann/voicemeeter-remote-python) for the Python API
- Built with Python and PyQt5

---

**Note**: This software is not affiliated with VB-Audio or Voicemeeter.