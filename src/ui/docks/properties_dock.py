"""
Properties Dock - Inspector framework
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class PropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Properties", parent)

        layout = QVBoxLayout(self.container)

        # Form Layout for Property Inspector
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        # Example Properties
        self.form_layout.addRow("Name:", QLineEdit("Object1"))

        spin = QSpinBox()
        spin.setRange(0, 100)
        spin.setValue(50)
        self.form_layout.addRow("Opacity:", spin)

        self.form_layout.addRow("Visible:", QCheckBox())

        combo = QComboBox()
        combo.addItems(["Linear", "Ease In", "Ease Out"])
        self.form_layout.addRow("Interpolation:", combo)

        # Color preview
        color_btn = QPushButton()
        color_btn.setStyleSheet("background-color: #ff0000; border: 1px solid #777;")
        color_btn.setFixedSize(24, 24)
        self.form_layout.addRow("Color:", color_btn)

        # Image Preview
        preview_label = QLabel("Image Preview")
        preview_label.setStyleSheet("background-color: #222; border: 1px solid #444;")
        preview_label.setFixedSize(120, 80)
        self.form_layout.addRow(preview_label)

        layout.addStretch()
