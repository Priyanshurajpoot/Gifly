# player.py
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, pyqtSignal, QObject
import random

class MusicPlayer(QObject):
    song_changed = pyqtSignal(str)          # emits file path when song changes
    finished = pyqtSignal()                 # emits when a song ends
    position_changed = pyqtSignal(int)      # emits current position in ms
    duration_changed = pyqtSignal(int)      # emits total duration in ms
    state_changed = pyqtSignal(int)         # emits when playback state changes

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.playlist = []
        self.current_index = -1

        # Playback features
        self.shuffle = False
        self.repeat_mode = 'none'  # 'none', 'one', 'all'

        # Connect signals
        self.player.mediaStatusChanged.connect(self._check_end)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.stateChanged.connect(self._on_state_changed)

    # ---------- Playlist management ----------
    def load_songs(self, file_paths):
        """Add multiple songs to playlist."""
        if not file_paths:
            return
        self.playlist.extend(file_paths)
        if self.current_index == -1 and self.playlist:
            self.current_index = 0
            self.load_current()

    def clear_playlist(self):
        self.stop()
        self.playlist = []
        self.current_index = -1
        self.song_changed.emit("")

    def remove_song(self, index):
        if 0 <= index < len(self.playlist):
            removed = self.playlist.pop(index)
            if index == self.current_index:
                self.stop()
                if self.playlist:
                    self.current_index = min(index, len(self.playlist) - 1)
                    self.load_current()
                else:
                    self.current_index = -1
                    self.song_changed.emit("")
            elif index < self.current_index:
                self.current_index -= 1
            return removed
        return None

    # ---------- Load / play ----------
    def load_current(self):
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.song_changed.emit(file_path)

    def play(self):
        if not self.playlist:
            return
        if self.current_index == -1:
            self.current_index = 0
            self.load_current()
        if self.player.mediaStatus() != QMediaPlayer.NoMedia:
            self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def toggle(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    # ---------- Navigation ----------
    def next_song(self):
        if not self.playlist:
            return
        if self.repeat_mode == 'one':
            self.load_current()
            self.play()
            return

        if self.shuffle:
            if len(self.playlist) > 1:
                next_index = self.current_index
                while next_index == self.current_index:
                    next_index = random.randrange(0, len(self.playlist))
                self.current_index = next_index
            else:
                self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)

        self.load_current()
        self.play()

    def prev_song(self):
        if not self.playlist:
            return
        if self.repeat_mode == 'one':
            self.load_current()
            self.play()
            return

        if self.shuffle:
            if len(self.playlist) > 1:
                prev_index = self.current_index
                while prev_index == self.current_index:
                    prev_index = random.randrange(0, len(self.playlist))
                self.current_index = prev_index
            else:
                self.current_index = 0
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.load_current()
        self.play()

    # ---------- Control ----------
    def set_volume(self, volume):
        """Set volume (0-100)"""
        self.player.setVolume(int(volume))

    def set_position(self, position):
        """Seek to position in milliseconds"""
        self.player.setPosition(int(position))

    def get_position(self):
        """Get current position in milliseconds"""
        return int(self.player.position())

    def get_duration(self):
        """Get total duration in milliseconds"""
        return int(self.player.duration())

    def is_playing(self):
        return self.player.state() == QMediaPlayer.PlayingState

    def get_state(self):
        return self.player.state()

    # ---------- Signal handlers ----------
    def _check_end(self, status):
        try:
            from PyQt5.QtMultimedia import QMediaPlayer as _QMP
            if status == _QMP.EndOfMedia:
                self.finished.emit()
                if self.repeat_mode == 'one':
                    self.load_current()
                    self.play()
                else:
                    if self.repeat_mode == 'all':
                        self.next_song()
                    else:
                        if not self.shuffle:
                            if self.current_index == len(self.playlist) - 1:
                                self.stop()
                                return
                        self.next_song()
        except Exception:
            pass

    def _on_position_changed(self, position):
        self.position_changed.emit(int(position))

    def _on_duration_changed(self, duration):
        self.duration_changed.emit(int(duration))

    def _on_state_changed(self, state):
        self.state_changed.emit(state)

    # ---------- Mode setters ----------
    def set_shuffle(self, enabled: bool):
        self.shuffle = bool(enabled)

    def set_repeat_mode(self, mode: str):
        if mode in ('none', 'one', 'all'):
            self.repeat_mode = mode