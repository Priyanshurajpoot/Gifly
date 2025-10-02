# dock.py
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QTimer, QPropertyAnimation, QEasingCurve

class GifDock(QWidget):
    closed = pyqtSignal()
    
    def __init__(self, default_gifs=None):
        super().__init__()
        self.setWindowTitle("GIF Dock")

        # Frameless, transparent, always on top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # QLabel for GIF
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.setGeometry(100, 100, 300, 300)

        # GIF storage
        self.default_gifs = default_gifs[:] if default_gifs else []
        self.current_song_gifs = []
        self.gifs = self.default_gifs[:]
        self.current_index = 0
        self.movie = None

        # Control buttons style - modern minimal
        button_style = """
            QPushButton {
                background: rgba(20, 20, 20, 0.85);
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { 
                background: rgba(40, 40, 40, 0.95);
            }
            QPushButton:pressed {
                background: rgba(60, 60, 60, 1);
            }
        """

        # Create buttons
        self.closeBtn = QPushButton("✕", self)
        self.closeBtn.setStyleSheet(button_style)
        self.closeBtn.setFixedSize(32, 32)
        self.closeBtn.clicked.connect(self.close_dock)
        self.closeBtn.setToolTip("Close Dock")

        self.nextBtn = QPushButton("▶", self)
        self.nextBtn.setStyleSheet(button_style)
        self.nextBtn.setFixedSize(32, 32)
        self.nextBtn.clicked.connect(self.next_gif)
        self.nextBtn.setToolTip("Next GIF")

        self.prevBtn = QPushButton("◀", self)
        self.prevBtn.setStyleSheet(button_style)
        self.prevBtn.setFixedSize(32, 32)
        self.prevBtn.clicked.connect(self.prev_gif)
        self.prevBtn.setToolTip("Previous GIF")

        self.resizeBtn = QPushButton("⇲", self)
        self.resizeBtn.setStyleSheet(button_style)
        self.resizeBtn.setFixedSize(32, 32)
        self.resizeBtn.setToolTip("Drag to Resize")
        self.resizeBtn.setCursor(Qt.SizeFDiagCursor)

        # Initially hide buttons
        self.closeBtn.hide()
        self.nextBtn.hide()
        self.prevBtn.hide()
        self.resizeBtn.hide()

        # Dragging and resizing
        self.drag_pos = None
        self.resize_active = False
        self.resize_start_pos = None
        self.resize_start_geometry = None

        # Hover detection
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.hover_active = False
        
        # Timer to hide buttons after inactivity
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide_controls)
        self.hide_timer.setSingleShot(True)

        # Connect resize button mouse handlers
        self.resizeBtn.mousePressEvent = self.resize_button_press
        self.resizeBtn.mouseMoveEvent = self.resize_button_move
        self.resizeBtn.mouseReleaseEvent = self.resize_button_release

        if self.gifs:
            self.play_gif(self.gifs[self.current_index])

    # ---------------- public API ----------------
    def close_dock(self):
        self.closed.emit()
        self.close()

    def update_for_song(self, song_path: str, song_gifs: list):
        """Set GIFs assigned to the current song."""
        self.current_song_gifs = song_gifs[:] if song_gifs else []
        if self.current_song_gifs:
            self.gifs = self.current_song_gifs[:]
        else:
            self.gifs = self.default_gifs[:]
        self.current_index = 0
        if self.gifs:
            self.play_gif(self.gifs[self.current_index])
        else:
            if self.movie:
                self.movie.stop()
                self.movie.deleteLater()
                self.movie = None
            self.label.clear()

    def update_default_gifs(self, default_gifs: list):
        self.default_gifs = default_gifs[:] if default_gifs else []
        if not self.current_song_gifs:
            self.gifs = self.default_gifs[:]
            self.current_index = 0
            if self.gifs:
                self.play_gif(self.gifs[self.current_index])

    def next_gif(self):
        if not self.gifs:
            return
        self.current_index = (self.current_index + 1) % len(self.gifs)
        self.play_gif(self.gifs[self.current_index])

    def prev_gif(self):
        if not self.gifs:
            return
        self.current_index = (self.current_index - 1) % len(self.gifs)
        self.play_gif(self.gifs[self.current_index])

    def play_gif(self, path):
        if self.movie:
            try:
                self.movie.stop()
                self.movie.deleteLater()
            except Exception:
                pass
        try:
            self.movie = QMovie(path)
            self.label.setMovie(self.movie)
            self.movie.start()
        except Exception:
            self.label.clear()
            self.movie = None

    # -------------- Hover controls --------------
    def enterEvent(self, event):
        """Mouse enters widget"""
        self.show_controls()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leaves widget"""
        self.hide_timer.start(1500)  # Hide after 1.5s
        super().leaveEvent(event)

    def show_controls(self):
        """Show control buttons"""
        self.hide_timer.stop()
        self.closeBtn.show()
        self.nextBtn.show()
        self.prevBtn.show()
        self.resizeBtn.show()

    def hide_controls(self):
        """Hide control buttons"""
        if not self.resize_active:
            self.closeBtn.hide()
            self.nextBtn.hide()
            self.prevBtn.hide()
            self.resizeBtn.hide()

    # -------------- window & interaction --------------
    def resizeEvent(self, event):
        self.label.setGeometry(0, 0, self.width(), self.height())

        # Position buttons at top-right
        button_spacing = 4
        x_pos = self.width() - 38
        y_pos = 6

        self.closeBtn.move(x_pos, y_pos)
        self.nextBtn.move(x_pos, y_pos + 36 + button_spacing)
        self.prevBtn.move(x_pos, y_pos + 72 + button_spacing * 2)
        self.resizeBtn.move(self.width() - 38, self.height() - 38)

        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def resize_button_press(self, event):
        if event.button() == Qt.LeftButton:
            self.resize_active = True
            self.resize_start_pos = event.globalPos()
            self.resize_start_geometry = self.geometry()
            event.accept()

    def resize_button_move(self, event):
        if self.resize_active and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.resize_start_pos
            geo = self.resize_start_geometry
            
            min_size = 150
            new_width = max(min_size, geo.width() + delta.x())
            new_height = max(min_size, geo.height() + delta.y())
            
            self.resize(new_width, new_height)
            event.accept()

    def resize_button_release(self, event):
        self.resize_active = False
        self.resize_start_pos = None
        self.resize_start_geometry = None