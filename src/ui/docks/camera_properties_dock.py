"""
Camera Properties Dock
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class CameraPropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Properties", parent)

        layout = QVBoxLayout(self.container)

        form = QFormLayout()

        self.lens = QComboBox()
        self.lens.addItems(["24mm", "35mm", "50mm", "85mm", "200mm"])
        form.addRow("Lens:", self.lens)

        self.focus_dist = QDoubleSpinBox()
        self.focus_dist.setRange(0.1, 1000.0)
        self.focus_dist.setValue(10.0)
        form.addRow("Focus Dist (m):", self.focus_dist)

        self.dof = QDoubleSpinBox()
        self.dof.setRange(1.0, 22.0)
        self.dof.setValue(5.6)
        form.addRow("f-Stop:", self.dof)

        self.comp_rule = QComboBox()
        self.comp_rule.addItems(
            ["Rule of Thirds", "Golden Ratio", "Center", "Leading Lines"]
        )
        form.addRow("Composition:", self.comp_rule)

        self.transition = QComboBox()
        self.transition.addItems(["Cut", "Fade", "Cross Fade", "Whip Pan"])
        form.addRow("Transition In:", self.transition)

        layout.addLayout(form)

        self.generate_btn = QPushButton("AI Director Plan")
        layout.addWidget(self.generate_btn)

        layout.addStretch()

    def load_camera(self, camera):
        self.lens.setCurrentText(camera.lens_type)
        self.focus_dist.setValue(camera.focus_distance)
        self.dof.setValue(camera.depth_of_field)
