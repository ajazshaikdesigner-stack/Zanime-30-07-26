"""
Dialogue Editor Viewport - Text entry and waveform mock.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class DialogueEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        lbl = QLabel("Enter Dialogue / Narration Text:")
        layout.addWidget(lbl)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type what the character will say here...")
        layout.addWidget(self.text_edit)

        self.waveform_mock = QLabel("Audio Waveform & Viseme Preview Area")
        self.waveform_mock.setAlignment(Qt.AlignCenter)
        self.waveform_mock.setStyleSheet(
            "border: 1px solid #555; background: #000; color: #0f0; min-height: 150px;"
        )
        layout.addWidget(self.waveform_mock)
