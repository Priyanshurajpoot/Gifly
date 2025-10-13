# 🎵 Gifly — Music Player with GIF Dock

![Gifly Logo](gifly.ico)

**Gifly** is a lightweight, modern music player built with **Python (PyQt5)**.  
It combines smooth audio playback with a floating, resizable **GIF dock** that stays on top of all windows — making your music listening experience more fun and interactive.

---

## 👨‍💻 About the Developer

**Priyanshu Rajpoot**  
*MCA Post Graduate | Python Developer | Prompt Engineer | AI Enthusiast*

- 🔗 **LinkedIn**: [priyanshux5](https://linkedin.com/in/priyanshux5)
- 💻 **GitHub**: [Priyanshurajpoot](https://github.com/Priyanshurajpoot)
- 📧 **Email**: priyanshux5xraj@gmail.com

**Core Interests**: Prompt Engineering, Artificial Intelligence, Machine Learning, NLP, Generative AI  
**Primary Skills**: Python, PyQt5, PyTorch, Transformers, OpenCV, Chrome Extension API, OAuth 2.0, Data Analysis, GUI Development

---

## ✨ Features

- 🎶 **Music Playback**
  - Supports multiple audio formats: MP3, WAV, OGG, FLAC, AAC, WMA, M4A
  - Shuffle / Repeat (One / All / None) modes
  - Volume controls 

- 📂 **Library Management**
  - Add multiple songs at once
  - Search songs
  - Remove single or all songs
    
- 🖼 **GIF Dock**
  - Floating, always-on-top transparent dock
  - Add your favorite GIFs and sync them with songs
  - Hover to reveal controls (Next/Prev GIF, Resize, Close)
  - Resizable and draggable

- 🎨 **Beautiful UI**
  - Modern dark theme with accent highlights
  - Clean tab-based interface
  - Minimalist playback controls

- 💾 **Smart State Management**
  - Automatic save/restore of playback position
  - Remember window and dock positions
  - Persistent settings across sessions

---

## 🎯 Quick Start

### Option 1: Portable EXE
1. Download the latest **Gifly.exe** from [Releases](https://github.com/Priyanshurajpoot/Gifly/releases).
2. Run `Gifly.exe` — no install required.

### Option 2: Full Installer
1. Download **GiflySetup.exe** from [Releases](https://github.com/Priyanshurajpoot/Gifly/releases).
2. Run the installer and follow instructions.
3. Launch Gifly from Start Menu or Desktop.

---

## 🛠 Build from Source

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**:
```bash
git clone https://github.com/Priyanshurajpoot/Gifly.git
cd Gifly
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python main.py
```

### Requirements
Create a `requirements.txt` file with the following content:

```txt
PyQt5>=5.15.0
PyQt5-Qt5>=5.15.2
PyQt5-sip>=12.11.0
```

---

## 🎮 How to Use

### Adding Music
1. Go to the **Songs** tab
2. Click **"+ Add Songs"**
3. Select your audio files (MP3, WAV, OGG, FLAC, etc.)
4. Double-click any song to play

### Adding GIFs
1. Go to the **GIFs** tab  
2. Click **"+ Add GIFs"**
3. Select your GIF files
4. GIFs will appear in the floating dock

### Using the GIF Dock
1. Go to the **Dock** tab
2. Click **"Open GIF Dock"**
3. **Hover** over the dock to show controls:
   - **◀ / ▶** - Navigate between GIFs
   - **⇲** - Resize the dock (drag from bottom-right)
   - **✕** - Close the dock
4. **Drag** anywhere on the dock to move it around

### Playback Controls
- **▶/⏸** - Play/Pause
- **⏮/⏭** - Previous/Next track
- **🔀** - Shuffle mode
- **🔁** - Repeat mode (cycles through: Off → All → One)

---

## 🏗️ Project Structure

```
Gifly/
│
├── main.py                 # Main application window
├── player.py              # Music playback engine
├── dock.py                # Floating GIF dock implementation
├── utils.py               # Utilities and settings management
├── settings.json          # User settings (auto-generated)
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── gifly.ico             # Application icon
```

### Core Components

- **`main.py`** - Main application with modern UI, tab management, and player controls
- **`player.py`** - Music player backend with playlist management and playback features
- **`dock.py`** - Floating GIF dock with hover controls and resizing capabilities
- **`utils.py`** - Settings persistence and utility functions

---

## 🎨 UI Overview

### Tabs Layout

1. **📁 Songs Tab**
   - Music library management
   - Search functionality
   - Add/remove songs
   - Double-click to play

2. **📋 Playlists Tab** 
   - Playlist management (coming soon!)
   - Organize your music collections

3. **🖼 GIFs Tab**
   - GIF library management
   - Add/remove GIFs
   - Context menu support

4. **⚓ Dock Tab**
   - Dock status and controls
   - Open/close floating dock
   - Usage instructions

### Player Controls
- **Now Playing** section with current track
- **Progress bar** with seek functionality
- **Volume control** with visual feedback
- **Playback controls** (shuffle, previous, play/pause, next, repeat)

---

## ⚙️ Settings & Configuration

Gifly automatically saves your preferences in `settings.json`:

```json
{
  "playlist": ["path/to/songs"],
  "last_index": 0,
  "last_position": 45000,
  "volume": 70,
  "gifs": ["path/to/gifs"],
  "shuffle": false,
  "repeat_mode": "none",
  "dock_geometry": [100, 100, 300, 300],
  "window_geometry": [150, 100, 1100, 650]
}
```

**Auto-save feature**: Settings are saved every 10 seconds and on app close.

---

## 🎯 Key Features Deep Dive

### Music Playback Engine
- Built on PyQt5's QMediaPlayer
- Supports wide range of audio formats
- Accurate position tracking
- Smooth seeking functionality

### GIF Dock Technology
- **Always on top** - Stays visible over other applications
- **Frameless & transparent** - Clean, distraction-free appearance
- **Hover controls** - Controls appear only when needed
- **Drag & resize** - Fully customizable positioning and size
- **Song-specific GIFs** - Assign different GIFs to different songs

### Smart State Management
- Remembers playback position for each song
- Saves window and dock size/position
- Persistent volume and playback mode settings
- Cross-platform configuration directory support

---

## 🔧 Troubleshooting

### Common Issues

**Dock doesn't open:**
- Ensure you have added GIFs in the GIFs tab first
- Check if another instance is running

**Audio files not playing:**
- Verify file format support (MP3, WAV, OGG, FLAC, etc.)
- Check if codecs are installed on your system

**Dock controls not appearing:**
- Hover over the dock to reveal controls
- Controls auto-hide after 1.5 seconds of inactivity

### Performance Tips
- Keep GIF file sizes reasonable for smoother performance
- Use supported audio formats for best compatibility
- The app automatically manages memory and resources

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: [Open an issue](https://github.com/Priyanshurajpoot/Gifly/issues) with detailed description
2. **Suggest Features**: Share your ideas for improvements
3. **Code Contributions**: Fork the repo and submit pull requests
4. **Improve Documentation**: Help make Gifly more accessible

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/Priyanshurajpoot/Gifly.git
cd Gifly

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

---

## 📝 Roadmap

### Planned Features
- [ ] **Playlist Management** - Create and manage multiple playlists
- [ ] **GIF-Song Associations** - Assign specific GIFs to specific songs
- [ ] **Themes** - Light/dark mode and custom color schemes
- [ ] **Keyboard Shortcuts** - Global hotkey support
- [ ] **Audio Visualization** - Real-time audio visualizers
- [ ] **Plugin System** - Extensible architecture for add-ons
- [ ] **Cross-Platform Installers** - Native packages for all platforms

### Under Consideration
- [ ] **Online GIF Search** - Built-in GIF search and import
- [ ] **Lyrics Support** - Display synchronized lyrics
- [ ] **Music Streaming** - Integration with streaming services
- [ ] **Mobile Companion** - Mobile app for remote control

---

## 📄 License

This project is licensed under the MIT License:

```text
MIT License

Copyright (c) 2024 Gifly

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Contact

- **🐛 Report Issues**: [GitHub Issues](https://github.com/Priyanshurajpoot/Gifly/issues)
- **🚀 Downloads**: [GitHub Releases](https://github.com/Priyanshurajpoot/Gifly/releases)
- **💬 Discussions**: [GitHub Discussions](https://github.com/Priyanshurajpoot/Gifly/discussions)
- **📧 Email**: priyanshux5xraj@gmail.com
- **👨‍💻 Developer**: [Priyanshu Rajpoot](https://linkedin.com/in/priyanshux5)

---

## 🙏 Acknowledgments

Built with:
- **PyQt5** - Cross-platform GUI toolkit
- **QMediaPlayer** - Robust audio playback engine
- **Python** - Core programming language

Special thanks to:
- The open-source community
- Beta testers and early users
- Contributors and supporters

---

## 🔗 Quick Links

- **📂 Repository**: [Gifly on GitHub](https://github.com/Priyanshurajpoot/Gifly.git)
- **🚀 Releases**: [Latest Releases](https://github.com/Priyanshurajpoot/Gifly/releases)
- **🐛 Issues**: [Report Issues](https://github.com/Priyanshurajpoot/Gifly/issues)
- **👨‍💻 Developer**: [Priyanshu Rajpoot](https://linkedin.com/in/priyanshux5)

---

**Python Developer | Prompt Engineer | AI Enthusiast**  
*Building creative solutions that blend multimedia and user experience*

--- 

*AUTHOR*  
**Priyanshu Rajpoot**  
*MCA Post Graduate | Python Developer | AI Enthusiast*