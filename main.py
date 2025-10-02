# main.py
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QSlider, QLabel, QListWidget, QHBoxLayout, QMenu,
    QTabWidget, QMessageBox, QGroupBox, QSplitter, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, QRect, QSize
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QMediaPlayer
from player import MusicPlayer
from dock import GifDock
import utils

# Professional color scheme - Dark theme with subtle accents
COLORS = {
    'bg': '#1a1a1a',           # Main background
    'panel': '#242424',        # Panel background
    'panel_light': '#2d2d2d',  # Lighter panel
    'border': '#3a3a3a',       # Border color
    'text': '#e8e8e8',         # Primary text
    'text_dim': '#999999',     # Dim text
    'accent': '#0d7aff',       # Primary accent (blue)
    'accent_hover': '#3d8fff', # Accent hover
    'accent_pressed': '#0a5fcf',# Accent pressed
    'success': '#2ea043',      # Success green
    'warning': '#db6e1f',      # Warning orange
    'danger': '#da3633'        # Danger red
}

class GiflyPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gifly - Music Player")
        self.setMinimumSize(1100, 650)

        # Load settings first
        self.settings = utils.load_settings()

        # Core components
        self.music_player = MusicPlayer()
        self.music_player.song_changed.connect(self.on_song_changed)
        self.music_player.finished.connect(self.on_song_finished)
        self.music_player.position_changed.connect(self.update_position)
        self.music_player.duration_changed.connect(self.update_duration)
        self.music_player.state_changed.connect(self.on_state_changed)

        # Data
        self.song_gifs = self.settings.get("song_gifs", {})
        self.gif_list = self.settings.get("gifs", [])
        self.dock = None
        self._saved_dock_geometry = None

        # Apply theme
        self.apply_theme()

        # Setup UI
        self.setup_ui()

        # Restore saved state
        self.restore_state()

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_state)
        self.save_timer.start(10000)  # Save every 10 seconds

    def setup_ui(self):
        """Initialize the user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {COLORS['border']}; }}")

        # Left panel - Library & tabs
        left_panel = self.create_left_panel()
        
        # Right panel - Player controls
        right_panel = self.create_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background: {COLORS['panel']};
                color: {COLORS['text_dim']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)
        self.statusBar().showMessage("Ready")

    def create_left_panel(self):
        """Create left panel with tabs"""
        panel = QWidget()
        panel.setStyleSheet(f"background: {COLORS['panel']};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background: {COLORS['bg']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: {COLORS['panel']};
                color: {COLORS['text']};
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 12px;
                font-weight: 500;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 70px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['bg']};
                color: {COLORS['accent']};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background: {COLORS['panel_light']};
            }}
        """)

        # Create tabs
        self.create_songs_tab()
        self.create_playlist_tab()
        self.create_gifs_tab()
        self.create_dock_tab()

        layout.addWidget(self.tabs)
        return panel

    def create_songs_tab(self):
        """Create songs library tab"""
        tab = QWidget()
        tab.setStyleSheet(f"background: {COLORS['bg']};")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QLabel("Songs")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 18px;
            font-weight: 600;
            padding: 2px 0;
        """)
        layout.addWidget(header)

        # Search bar
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("🔍 Search songs...")
        self.searchBox.textChanged.connect(self.filter_songs)
        self.searchBox.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['panel_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 10px 14px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['accent']};
            }}
        """)
        layout.addWidget(self.searchBox)

        # Songs list
        self.songsListWidget = QListWidget()
        self.songsListWidget.itemDoubleClicked.connect(self.play_selected_song)
        self.songsListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.songsListWidget.customContextMenuRequested.connect(self.show_song_menu)
        self.songsListWidget.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['panel_light']};
            }}
            QListWidget::item:selected {{
                background: {COLORS['accent']};
                color: white;
            }}
        """)
        layout.addWidget(self.songsListWidget)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        self.addSongsBtn = QPushButton("+ Add Songs")
        self.addSongsBtn.clicked.connect(self.openFiles)
        self.addSongsBtn.setStyleSheet(self.get_button_style())
        actions_layout.addWidget(self.addSongsBtn)

        self.clearSongsBtn = QPushButton("Clear All")
        self.clearSongsBtn.clicked.connect(self.clear_all_songs)
        self.clearSongsBtn.setStyleSheet(self.get_button_style(danger=True))
        actions_layout.addWidget(self.clearSongsBtn)

        layout.addLayout(actions_layout)
        self.tabs.addTab(tab, "Songs")

    def create_playlist_tab(self):
        """Create playlist tab"""
        tab = QWidget()
        tab.setStyleSheet(f"background: {COLORS['bg']};")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QLabel("Playlists")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 18px;
            font-weight: 600;
            padding: 2px 0;
        """)
        layout.addWidget(header)

        # Playlist widget
        self.playlistsWidget = QListWidget()
        self.playlistsWidget.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['panel_light']};
            }}
            QListWidget::item:selected {{
                background: {COLORS['accent']};
                color: white;
            }}
        """)
        layout.addWidget(self.playlistsWidget)

        # Info message
        info = QLabel("Playlist management coming soon!")
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px; padding: 8px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        layout.addStretch()
        self.tabs.addTab(tab, "Playlists")

    def create_gifs_tab(self):
        """Create GIFs management tab"""
        tab = QWidget()
        tab.setStyleSheet(f"background: {COLORS['bg']};")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Header
        header = QLabel("GIFs")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 18px;
            font-weight: 600;
            padding: 2px 0;
        """)
        layout.addWidget(header)

        # Info label
        info = QLabel("Manage your GIF collection. These will be displayed in the dock.")
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px; padding: 4px 0 8px 0;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # GIFs list
        self.gifListWidget = QListWidget()
        self.gifListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.gifListWidget.customContextMenuRequested.connect(self.show_gif_menu)
        self.gifListWidget.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['panel_light']};
            }}
            QListWidget::item:selected {{
                background: {COLORS['accent']};
                color: white;
            }}
        """)
        layout.addWidget(self.gifListWidget)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        self.addGifBtn = QPushButton("+ Add GIFs")
        self.addGifBtn.clicked.connect(self.add_gifs)
        self.addGifBtn.setStyleSheet(self.get_button_style())
        actions_layout.addWidget(self.addGifBtn)

        self.removeGifBtn = QPushButton("Remove")
        self.removeGifBtn.clicked.connect(self.remove_selected_gif)
        self.removeGifBtn.setStyleSheet(self.get_button_style())
        actions_layout.addWidget(self.removeGifBtn)

        self.clearGifsBtn = QPushButton("Clear All")
        self.clearGifsBtn.clicked.connect(self.clear_all_gifs)
        self.clearGifsBtn.setStyleSheet(self.get_button_style(danger=True))
        actions_layout.addWidget(self.clearGifsBtn)

        layout.addLayout(actions_layout)
        self.tabs.addTab(tab, "GIFs")

    def create_dock_tab(self):
        """Create dock control tab"""
        tab = QWidget()
        tab.setStyleSheet(f"background: {COLORS['bg']};")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header = QLabel("Dock")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 18px;
            font-weight: 600;
            padding: 2px 0;
        """)
        layout.addWidget(header)

        # Dock status
        status_group = QGroupBox("Status")
        status_group.setStyleSheet(self.get_groupbox_style())
        status_layout = QVBoxLayout()
        
        self.dockStatusLabel = QLabel("Dock: Closed")
        self.dockStatusLabel.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; font-weight: 600;")
        status_layout.addWidget(self.dockStatusLabel)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Control button
        self.dockBtn = QPushButton("Open GIF Dock")
        self.dockBtn.clicked.connect(self.toggleDock)
        self.dockBtn.setMinimumHeight(50)
        self.dockBtn.setStyleSheet(self.get_button_style(primary=True))
        layout.addWidget(self.dockBtn)

        # Instructions
        info_group = QGroupBox("Instructions")
        info_group.setStyleSheet(self.get_groupbox_style())
        info_layout = QVBoxLayout()
        
        instructions = QLabel(
            "• Drag anywhere to move the dock\n"
            "• Hover to show controls\n"
            "• Use ◀ / ▶ to change GIFs\n"
            "• Use ⇲ to resize\n"
            "• Add GIFs in the GIFs tab"
        )
        instructions.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; line-height: 1.8;")
        instructions.setWordWrap(True)
        info_layout.addWidget(instructions)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Dock")

    def create_right_panel(self):
        """Create right panel with player controls"""
        panel = QWidget()
        panel.setStyleSheet(f"background: {COLORS['bg']};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Now Playing section
        now_playing_group = QGroupBox("Now Playing")
        now_playing_group.setStyleSheet(self.get_groupbox_style())
        now_playing_layout = QVBoxLayout()
        
        self.currentSongLabel = QLabel("No song loaded")
        self.currentSongLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 15px;
            font-weight: 600;
            padding: 12px;
        """)
        self.currentSongLabel.setWordWrap(True)
        self.currentSongLabel.setAlignment(Qt.AlignCenter)
        now_playing_layout.addWidget(self.currentSongLabel)
        now_playing_group.setLayout(now_playing_layout)
        layout.addWidget(now_playing_group)

        # Progress section
        self.create_progress_section(layout)

        # Playback controls
        self.create_playback_controls(layout)

        # Volume control
        self.create_volume_control(layout)

        layout.addStretch()
        return panel

    def create_progress_section(self, parent_layout):
        """Create progress bar and time labels"""
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)

        # Time labels
        time_layout = QHBoxLayout()
        self.currentTimeLabel = QLabel("0:00")
        self.currentTimeLabel.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px;")
        self.totalTimeLabel = QLabel("0:00")
        self.totalTimeLabel.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 12px;")
        time_layout.addWidget(self.currentTimeLabel)
        time_layout.addStretch()
        time_layout.addWidget(self.totalTimeLabel)
        progress_layout.addLayout(time_layout)

        # Progress slider
        self.progressSlider = QSlider(Qt.Horizontal)
        self.progressSlider.setRange(0, 100)
        self.progressSlider.sliderMoved.connect(self.seek_position)
        self.progressSlider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {COLORS['panel_light']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['accent']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {COLORS['accent']};
            }}
        """)
        progress_layout.addWidget(self.progressSlider)
        parent_layout.addLayout(progress_layout)

    def create_playback_controls(self, parent_layout):
        """Create playback control buttons"""
        controls_group = QGroupBox("Controls")
        controls_group.setStyleSheet(self.get_groupbox_style())
        controls_layout = QVBoxLayout()

        # Main control buttons
        main_controls = QHBoxLayout()
        main_controls.setSpacing(12)
        main_controls.addStretch()

        # Shuffle
        self.shuffleBtn = QPushButton("🔀")
        self.shuffleBtn.setCheckable(True)
        self.shuffleBtn.setFixedSize(44, 44)
        self.shuffleBtn.clicked.connect(self.toggle_shuffle)
        self.shuffleBtn.setToolTip("Shuffle")
        self.shuffleBtn.setStyleSheet(self.get_control_button_style())
        main_controls.addWidget(self.shuffleBtn)

        # Previous
        self.prevBtn = QPushButton("⏮")
        self.prevBtn.setFixedSize(44, 44)
        self.prevBtn.clicked.connect(self.play_prev)
        self.prevBtn.setToolTip("Previous")
        self.prevBtn.setStyleSheet(self.get_control_button_style())
        main_controls.addWidget(self.prevBtn)

        # Play/Pause (larger)
        self.playBtn = QPushButton("▶")
        self.playBtn.setFixedSize(64, 64)
        self.playBtn.clicked.connect(self.togglePlay)
        self.playBtn.setToolTip("Play/Pause")
        self.playBtn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-radius: 32px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent']};
                color: {COLORS['accent']};
            }}
            QPushButton:pressed {{
                background: {COLORS['panel_light']};
            }}
        """)
        main_controls.addWidget(self.playBtn)

        # Next
        self.nextBtn = QPushButton("⏭")
        self.nextBtn.setFixedSize(44, 44)
        self.nextBtn.clicked.connect(self.play_next)
        self.nextBtn.setToolTip("Next")
        self.nextBtn.setStyleSheet(self.get_control_button_style())
        main_controls.addWidget(self.nextBtn)

        # Repeat
        self.repeatBtn = QPushButton("🔁")
        self.repeatBtn.setCheckable(True)
        self.repeatBtn.setFixedSize(44, 44)
        self.repeatBtn.clicked.connect(self.toggle_repeat)
        self.repeatBtn.setToolTip("Repeat")
        self.repeatBtn.setStyleSheet(self.get_control_button_style())
        main_controls.addWidget(self.repeatBtn)

        main_controls.addStretch()
        controls_layout.addLayout(main_controls)
        controls_group.setLayout(controls_layout)
        parent_layout.addWidget(controls_group)

    def create_volume_control(self, parent_layout):
        """Create volume slider"""
        volume_group = QGroupBox("Volume")
        volume_group.setStyleSheet(self.get_groupbox_style())
        volume_layout = QHBoxLayout()

        self.volumeLabel = QLabel("🔊")
        self.volumeLabel.setStyleSheet("font-size: 16px;")
        volume_layout.addWidget(self.volumeLabel)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.valueChanged.connect(self.changeVolume)
        self.volumeSlider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {COLORS['panel_light']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['accent']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {COLORS['accent']};
            }}
        """)
        volume_layout.addWidget(self.volumeSlider)

        self.volumeValue = QLabel("70")
        self.volumeValue.setStyleSheet(f"color: {COLORS['text']}; font-weight: 600; min-width: 35px; text-align: right;")
        volume_layout.addWidget(self.volumeValue)

        volume_group.setLayout(volume_layout)
        parent_layout.addWidget(volume_group)

    # ============ Styling Helpers ============
    def apply_theme(self):
        """Apply application-wide theme"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {COLORS['bg']};
            }}
            QWidget {{
                color: {COLORS['text']};
                font-family: 'Segoe UI', 'San Francisco', Arial, sans-serif;
            }}
            QMenu {{
                background: {COLORS['panel']};
                border: 1px solid {COLORS['border']};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background: {COLORS['accent']};
            }}
        """)

    def get_button_style(self, primary=False, danger=False):
        """Generate button stylesheet"""
        if danger:
            bg = COLORS['danger']
            hover = '#e74c3c'
        elif primary:
            bg = COLORS['accent']
            hover = COLORS['accent_hover']
        else:
            bg = COLORS['panel_light']
            hover = COLORS['border']

        return f"""
            QPushButton {{
                background: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
            QPushButton:pressed {{
                background: {COLORS['accent_pressed'] if primary else COLORS['panel']};
            }}
        """

    def get_control_button_style(self):
        """Generate control button stylesheet"""
        return f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-radius: 22px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent']};
                color: {COLORS['accent']};
            }}
            QPushButton:pressed {{
                background: {COLORS['panel_light']};
            }}
            QPushButton:checked {{
                border-color: {COLORS['accent']};
                color: {COLORS['accent']};
            }}
        """

    def get_groupbox_style(self):
        """Generate groupbox stylesheet"""
        return f"""
            QGroupBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: 600;
                font-size: 13px;
                color: {COLORS['text']};
                background: {COLORS['panel']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background: {COLORS['panel']};
            }}
        """

    # ============ File Management ============
    def openFiles(self):
        """Open file dialog to add songs"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Audio Files", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.aac *.wma)"
        )
        if files:
            self.music_player.load_songs(files)
            self.refresh_songs_list()
            self.save_state()
            self.statusBar().showMessage(f"Added {len(files)} song(s)", 3000)

    def refresh_songs_list(self):
        """Refresh the songs list widget"""
        self.songsListWidget.clear()
        for song in self.music_player.playlist:
            self.songsListWidget.addItem(os.path.basename(song))

    def filter_songs(self, text):
        """Filter songs based on search text"""
        for i in range(self.songsListWidget.count()):
            item = self.songsListWidget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def play_selected_song(self, item):
        """Play song when double-clicked"""
        index = self.songsListWidget.row(item)
        if 0 <= index < len(self.music_player.playlist):
            self.music_player.current_index = index
            self.music_player.load_current()
            self.music_player.play()
            self.save_state()

    def show_song_menu(self, pos):
        """Show context menu for songs"""
        item = self.songsListWidget.itemAt(pos)
        if item:
            menu = QMenu(self)
            remove_action = menu.addAction("Remove from Library")
            
            action = menu.exec_(self.songsListWidget.mapToGlobal(pos))
            if action == remove_action:
                self.delete_song(item)

    def delete_song(self, item):
        """Remove a song from the playlist"""
        index = self.songsListWidget.row(item)
        if 0 <= index < len(self.music_player.playlist):
            song_path = self.music_player.playlist[index]
            self.music_player.remove_song(index)
            self.songsListWidget.takeItem(index)
            
            if song_path in self.song_gifs:
                del self.song_gifs[song_path]
            
            self.save_state()
            self.statusBar().showMessage("Song removed", 2000)

    def clear_all_songs(self):
        """Clear all songs from playlist"""
        if self.music_player.playlist:
            reply = QMessageBox.question(
                self, 'Clear All Songs',
                'Remove all songs from library?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.music_player.clear_playlist()
                self.songsListWidget.clear()
                self.currentSongLabel.setText("No song loaded")
                self.song_gifs.clear()
                self.save_state()

    # ============ GIF Management ============
    def add_gifs(self):
        """Add GIF files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select GIF Files", "", "GIF Files (*.gif)"
        )
        if files:
            for gif in files:
                if gif not in self.gif_list:
                    self.gif_list.append(gif)
            self.refresh_gif_list()
            self.save_state()
            if self.dock and self.dock.isVisible():
                self.dock.update_default_gifs(self.gif_list)
            self.statusBar().showMessage(f"Added {len(files)} GIF(s)", 3000)

    def remove_selected_gif(self):
        """Remove selected GIF"""
        current_item = self.gifListWidget.currentItem()
        if current_item:
            index = self.gifListWidget.row(current_item)
            if 0 <= index < len(self.gif_list):
                self.gif_list.pop(index)
                self.refresh_gif_list()
                self.save_state()
                if self.dock and self.dock.isVisible():
                    self.dock.update_default_gifs(self.gif_list)

    def show_gif_menu(self, pos):
        """Show context menu for GIFs"""
        item = self.gifListWidget.itemAt(pos)
        if item:
            menu = QMenu(self)
            delete_action = menu.addAction("Remove GIF")
            action = menu.exec_(self.gifListWidget.mapToGlobal(pos))
            if action == delete_action:
                index = self.gifListWidget.row(item)
                if 0 <= index < len(self.gif_list):
                    self.gif_list.pop(index)
                    self.refresh_gif_list()
                    self.save_state()
                    if self.dock and self.dock.isVisible():
                        self.dock.update_default_gifs(self.gif_list)

    def clear_all_gifs(self):
        """Clear all GIFs"""
        if self.gif_list:
            reply = QMessageBox.question(
                self, 'Clear All GIFs',
                'Remove all GIFs?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.gif_list.clear()
                self.refresh_gif_list()
                self.save_state()
                if self.dock and self.dock.isVisible():
                    self.dock.update_default_gifs(self.gif_list)

    def refresh_gif_list(self):
        """Refresh GIF list widget"""
        self.gifListWidget.clear()
        for gif in self.gif_list:
            self.gifListWidget.addItem(os.path.basename(gif))

    # ============ Dock Control ============
    def toggleDock(self):
        """Toggle GIF dock visibility"""
        if not self.gif_list:
            QMessageBox.warning(
                self, "No GIFs",
                "Please add some GIFs first in the GIFs tab!"
            )
            return

        if not self.dock:
            self.dock = GifDock(default_gifs=self.gif_list)
            self.dock.closed.connect(self.on_dock_closed)
            if self._saved_dock_geometry:
                self.dock.setGeometry(self._saved_dock_geometry)
            self.dock.show()
            
            current_song = None
            if 0 <= self.music_player.current_index < len(self.music_player.playlist):
                current_song = self.music_player.playlist[self.music_player.current_index]
            self.update_dock_for_song(current_song)
            
            self.dockBtn.setText("Close Dock")
            self.dockStatusLabel.setText("Dock: Open")
        else:
            if self.dock.isVisible():
                self.dock.hide()
                self.dockBtn.setText("Open Dock")
                self.dockStatusLabel.setText("Dock: Hidden")
            else:
                current_song = None
                if 0 <= self.music_player.current_index < len(self.music_player.playlist):
                    current_song = self.music_player.playlist[self.music_player.current_index]
                self.update_dock_for_song(current_song)
                self.dock.show()
                self.dockBtn.setText("Close Dock")
                self.dockStatusLabel.setText("Dock: Open")

    def on_dock_closed(self):
        """Handle dock close event"""
        self.dockBtn.setText("Open Dock")
        self.dockStatusLabel.setText("Dock: Closed")
        self.save_state()

    def update_dock_for_song(self, song_path):
        """Update dock GIFs for current song"""
        if not self.dock:
            return
        if song_path and song_path in self.song_gifs and self.song_gifs[song_path]:
            self.dock.update_for_song(song_path, self.song_gifs[song_path])
        else:
            self.dock.update_for_song(song_path or "", [])

    # ============ Playback Controls ============
    def togglePlay(self):
        """Toggle play/pause"""
        if not self.music_player.playlist:
            QMessageBox.information(self, "No Songs", "Please add songs first!")
            return
        
        self.music_player.toggle()
        self.save_state()

    def play_next(self):
        """Play next song"""
        if self.music_player.playlist:
            self.music_player.next_song()
            self.save_state()

    def play_prev(self):
        """Play previous song"""
        if self.music_player.playlist:
            self.music_player.prev_song()
            self.save_state()

    def seek_position(self, position):
        """Seek to position"""
        self.music_player.set_position(position)

    def changeVolume(self, value):
        """Change volume"""
        self.music_player.set_volume(value)
        self.volumeValue.setText(str(value))
        
        # Update icon
        if value == 0:
            self.volumeLabel.setText("🔇")
        elif value < 33:
            self.volumeLabel.setText("🔈")
        elif value < 66:
            self.volumeLabel.setText("🔉")
        else:
            self.volumeLabel.setText("🔊")
        
        self.settings["volume"] = value
        self.save_state()

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        enabled = self.shuffleBtn.isChecked()
        self.music_player.set_shuffle(enabled)
        self.settings["shuffle"] = enabled
        self.save_state()
        self.statusBar().showMessage(f"Shuffle {'ON' if enabled else 'OFF'}", 2000)

    def toggle_repeat(self):
        """Cycle through repeat modes"""
        if not hasattr(self, "current_repeat_mode"):
            self.current_repeat_mode = "none"
        
        if self.current_repeat_mode == "none":
            self.current_repeat_mode = "all"
            self.repeatBtn.setChecked(True)
            msg = "Repeat: All"
        elif self.current_repeat_mode == "all":
            self.current_repeat_mode = "one"
            self.repeatBtn.setChecked(True)
            msg = "Repeat: One"
        else:
            self.current_repeat_mode = "none"
            self.repeatBtn.setChecked(False)
            msg = "Repeat: Off"
        
        self.music_player.set_repeat_mode(self.current_repeat_mode)
        self.settings["repeat_mode"] = self.current_repeat_mode
        self.save_state()
        self.statusBar().showMessage(msg, 2000)

    # ============ Event Handlers ============
    def on_song_changed(self, file_path):
        """Handle song change"""
        song_name = os.path.basename(file_path) if file_path else "No song"
        self.statusBar().showMessage(f"Now Playing: {song_name}")
        self.currentSongLabel.setText(song_name)
        self.update_dock_for_song(file_path)
        self.save_state()

    def on_song_finished(self):
        """Handle song finish"""
        self.save_state()

    def on_state_changed(self, state):
        """Handle playback state change"""
        if state == QMediaPlayer.PlayingState:
            self.playBtn.setText("⏸")
        else:
            self.playBtn.setText("▶")

    def update_position(self, position):
        """Update progress slider and time label"""
        self.progressSlider.blockSignals(True)
        self.progressSlider.setValue(position)
        self.progressSlider.blockSignals(False)
        self.currentTimeLabel.setText(utils.format_time(position))

    def update_duration(self, duration):
        """Update total duration"""
        self.progressSlider.setRange(0, duration if duration > 0 else 0)
        self.totalTimeLabel.setText(utils.format_time(duration))

    # ============ State Management ============
    def restore_state(self):
        """Restore saved state on startup"""
        # Restore playlist
        playlist = self.settings.get("playlist", [])
        if playlist:
            self.music_player.load_songs(playlist)
            self.refresh_songs_list()

        # Restore playback position
        last_index = self.settings.get("last_index", -1)
        last_position = self.settings.get("last_position", 0)
        if last_index is not None and 0 <= last_index < len(self.music_player.playlist):
            self.music_player.current_index = last_index
            self.music_player.load_current()
            QTimer.singleShot(300, lambda: self.music_player.set_position(last_position))

        # Restore volume
        volume = self.settings.get("volume", 70)
        self.volumeSlider.setValue(volume)
        self.music_player.set_volume(volume)
        self.volumeValue.setText(str(volume))

        # Restore shuffle and repeat
        self.music_player.set_shuffle(self.settings.get("shuffle", False))
        self.shuffleBtn.setChecked(self.music_player.shuffle)
        
        repeat_mode = self.settings.get("repeat_mode", "none")
        self.music_player.set_repeat_mode(repeat_mode)
        self.current_repeat_mode = repeat_mode
        self.repeatBtn.setChecked(repeat_mode != 'none')

        # Restore dock geometry
        dock_geom = self.settings.get("dock_geometry")
        if dock_geom and len(dock_geom) == 4:
            self._saved_dock_geometry = QRect(*dock_geom)

        # Restore window geometry
        win_geom = self.settings.get("window_geometry")
        if win_geom and len(win_geom) == 4:
            self.setGeometry(QRect(*win_geom))
        else:
            self.setGeometry(150, 100, 1100, 650)

        # Refresh GIF list
        self.refresh_gif_list()

    def save_state(self):
        """Save current state to settings"""
        self.settings["playlist"] = self.music_player.playlist
        self.settings["last_index"] = self.music_player.current_index
        
        try:
            self.settings["last_position"] = int(self.music_player.get_position())
        except:
            self.settings["last_position"] = 0
        
        self.settings["volume"] = int(self.volumeSlider.value())
        self.settings["gifs"] = self.gif_list
        self.settings["song_gifs"] = self.song_gifs
        self.settings["shuffle"] = self.music_player.shuffle
        self.settings["repeat_mode"] = self.music_player.repeat_mode

        # Save dock geometry
        if self.dock:
            geom = self.dock.geometry()
            self.settings["dock_geometry"] = [geom.x(), geom.y(), geom.width(), geom.height()]

        # Save window geometry
        geom = self.geometry()
        self.settings["window_geometry"] = [geom.x(), geom.y(), geom.width(), geom.height()]

        utils.save_settings(self.settings)

    def closeEvent(self, event):
        """Handle application close"""
        self.save_state()
        super().closeEvent(event)


# ============ Application Entry Point ============
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Gifly")
    app.setOrganizationName("Gifly")
    
    window = GiflyPlayer()
    window.show()
    
    sys.exit(app.exec_())