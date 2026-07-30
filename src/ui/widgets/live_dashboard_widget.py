"""
Live Dashboard Widget - Displays real-time System Metrics.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from src.models.performance_model import SystemMetrics


class LiveDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        title = QLabel("Hardware Telemetry (AMD Target)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        grid = QGridLayout()

        # CPU
        grid.addWidget(QLabel("CPU Usage (Ryzen 5):"), 0, 0)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        grid.addWidget(self.cpu_bar, 0, 1)

        # RAM
        grid.addWidget(QLabel("RAM Usage (16GB):"), 1, 0)
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        grid.addWidget(self.ram_bar, 1, 1)

        # VRAM
        grid.addWidget(QLabel("VRAM Usage (RX6500M 4GB):"), 2, 0)
        self.vram_bar = QProgressBar()
        self.vram_bar.setRange(0, 100)
        grid.addWidget(self.vram_bar, 2, 1)

        # GPU
        grid.addWidget(QLabel("GPU Load:"), 3, 0)
        self.gpu_bar = QProgressBar()
        self.gpu_bar.setRange(0, 100)
        grid.addWidget(self.gpu_bar, 3, 1)

        # Cache
        grid.addWidget(QLabel("Active Cache Size:"), 4, 0)
        self.cache_lbl = QLabel("0 MB")
        self.cache_lbl.setStyleSheet("font-weight: bold; color: #ffaa00;")
        grid.addWidget(self.cache_lbl, 4, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def update_metrics(self, m: SystemMetrics):
        self.cpu_bar.setValue(int(m.cpu_usage))
        self.ram_bar.setValue(int(m.ram_usage))
        self.vram_bar.setValue(int(m.vram_usage))
        self.gpu_bar.setValue(int(m.gpu_usage))
        self.cache_lbl.setText(f"{m.cache_size_mb:.1f} MB")

        # Change color based on threshold
        if m.ram_usage > 85:
            self.ram_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        else:
            self.ram_bar.setStyleSheet("")
