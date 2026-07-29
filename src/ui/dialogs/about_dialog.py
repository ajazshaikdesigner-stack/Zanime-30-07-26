"""
About Dialog - System and Version Information.
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from src.models.release_model import SystemDiagnosticReport, LicenseTier
import platform

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ZANIME")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("ZANIME Genesis")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel("Version: 0.9.9 (Release Candidate)")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Diagnostic Info
        diag = SystemDiagnosticReport()
        info = (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}\n"
            f"License: {LicenseTier.COMMUNITY.value}\n"
            f"Hardware: {diag.cpu_info} / {diag.gpu_info} / {diag.installed_ram}"
        )
        info_lbl = QLabel(info)
        info_lbl.setStyleSheet("background: #111; padding: 10px; border: 1px solid #333; margin-top: 20px;")
        layout.addWidget(info_lbl)
        
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
