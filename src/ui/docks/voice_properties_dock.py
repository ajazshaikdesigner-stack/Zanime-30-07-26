"""
Voice Properties Dock - Inspector for fine-tuning voice generation.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class VoicePropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Voice Properties", parent)

        layout = QVBoxLayout(self.container)

        form = QFormLayout()

        self.pitch = QDoubleSpinBox()
        self.pitch.setRange(0.1, 2.0)
        self.pitch.setSingleStep(0.1)
        self.pitch.setValue(1.0)
        form.addRow("Pitch:", self.pitch)

        self.speed = QDoubleSpinBox()
        self.speed.setRange(0.5, 2.0)
        self.speed.setSingleStep(0.1)
        self.speed.setValue(1.0)
        form.addRow("Speed:", self.speed)

        self.volume = QDoubleSpinBox()
        self.volume.setRange(0.0, 1.0)
        self.volume.setSingleStep(0.1)
        self.volume.setValue(1.0)
        form.addRow("Volume:", self.volume)

        self.emotion = QComboBox()
        self.emotion.addItems(
            [
                "Neutral",
                "Happy",
                "Sad",
                "Angry",
                "Excited",
                "Scared",
                "Shouting",
                "Whisper",
            ]
        )
        form.addRow("Emotion:", self.emotion)

        layout.addLayout(form)

        self.generate_btn = QPushButton("Generate AI Voice & Lip Sync")
        layout.addWidget(self.generate_btn)

        layout.addStretch()

    def load_clip(self, clip):
        self.volume.setValue(clip.volume)
        self.emotion.setCurrentText(clip.emotion)
