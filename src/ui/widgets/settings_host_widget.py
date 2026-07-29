"""
Settings Host Widget - Uses QStackedWidget to host the admin panels.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton
from PySide6.QtCore import Qt

class SettingsHostWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # General
        self.w_general = QLabel("General Settings\n(Preferences, Paths)")
        self.w_general.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.w_general)
        
        # Backup
        self.w_backup = QWidget()
        bl = QVBoxLayout(self.w_backup)
        bl.addWidget(QLabel("Backup & Recovery System"))
        self.btn_backup = QPushButton("Create Manual Backup Snapshot")
        bl.addWidget(self.btn_backup)
        bl.addStretch()
        self.stack.addWidget(self.w_backup)
        
        # Diagnostics
        self.w_diag = QWidget()
        dl = QVBoxLayout(self.w_diag)
        dl.addWidget(QLabel("Diagnostics & Crash Reports"))
        self.btn_crash = QPushButton("Simulate Crash & Send Dump")
        dl.addWidget(self.btn_crash)
        self.diag_log = QLabel("")
        dl.addWidget(self.diag_log)
        dl.addStretch()
        self.stack.addWidget(self.w_diag)
        
        # Updates
        self.w_updates = QWidget()
        ul = QVBoxLayout(self.w_updates)
        ul.addWidget(QLabel("Software Updates"))
        self.btn_update = QPushButton("Check for Updates")
        ul.addWidget(self.btn_update)
        ul.addStretch()
        self.stack.addWidget(self.w_updates)
        
        # License
        self.w_license = QWidget()
        ll = QVBoxLayout(self.w_license)
        ll.addWidget(QLabel("License Tier:"))
        self.lbl_tier = QLabel("Loading...")
        self.lbl_tier.setStyleSheet("font-size: 20px; font-weight: bold; color: gold;")
        ll.addWidget(self.lbl_tier)
        ll.addStretch()
        self.stack.addWidget(self.w_license)
        
    def switch_to(self, index: int):
        self.stack.setCurrentIndex(index)
