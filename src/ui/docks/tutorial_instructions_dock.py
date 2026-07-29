"""
Tutorial Instructions Dock - Displays guidance and Next/Prev buttons.
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from src.models.tutorial_model import TutorialStep
from PySide6.QtCore import Qt

class TutorialInstructionsDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Guide", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.title_lbl = QLabel("Title")
        self.title_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_lbl)
        
        self.inst_lbl = QLabel("Instructions")
        self.inst_lbl.setWordWrap(True)
        self.inst_lbl.setStyleSheet("min-height: 100px;")
        self.inst_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.inst_lbl)
        
        controls = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next Step")
        self.next_btn.setStyleSheet("background-color: #2b5797; color: white;")
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.next_btn)
        
        layout.addLayout(controls)
        layout.addStretch()
        
    def update_step(self, step: TutorialStep):
        self.title_lbl.setText(step.title)
        self.inst_lbl.setText(step.instruction_text)
