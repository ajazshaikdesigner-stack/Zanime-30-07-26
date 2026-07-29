"""
Splash Screen shown on application startup.
"""
from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QPixmap, QColor, QFont
from PySide6.QtCore import Qt

class SplashScreen(QSplashScreen):
    def __init__(self, parent=None):
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor("#1e1e1e"))
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.title = QLabel("ZANIME")
        self.title.setStyleSheet("font-size: 42pt; font-weight: bold; color: #007acc; font-family: 'Segoe UI';")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.subtitle = QLabel("AI Powered 2D Animation Studio")
        self.subtitle.setStyleSheet("font-size: 14pt; color: #e0e0e0; font-family: 'Segoe UI';")
        self.subtitle.setAlignment(Qt.AlignCenter)
        
        self.loading_label = QLabel("Initializing...")
        self.loading_label.setStyleSheet("font-size: 10pt; color: #aaaaaa; font-family: 'Segoe UI';")
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3f3f46;
                background-color: #2d2d30;
                height: 4px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        layout.addStretch()
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch()
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        layout.setContentsMargins(50, 50, 50, 50)
        
    def update_progress(self, value: int, message: str):
        self.progress_bar.setValue(value)
        self.loading_label.setText(message)
        self.repaint()  # Force UI update during synchronous startup
