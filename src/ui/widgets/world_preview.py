"""
World Preview Component.
Simulates environmental lighting and weather overlays.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class WorldPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Top bar for view controls
        controls = QHBoxLayout()

        self.sim_lighting = QComboBox()
        self.sim_lighting.addItems(
            ["Default", "Sunset (Sim)", "Night (Sim)", "Fog (Sim)"]
        )
        controls.addWidget(QLabel("Simulation:"))
        controls.addWidget(self.sim_lighting)

        layout.addLayout(controls)

        # Center view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        layout.addWidget(self.view)

        # Bottom bar for zoom
        bottom_controls = QHBoxLayout()
        bottom_controls.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 300)
        self.zoom_slider.setValue(100)
        bottom_controls.addWidget(self.zoom_slider)

        layout.addLayout(bottom_controls)

        # Connect zoom
        self.zoom_slider.valueChanged.connect(self._on_zoom)

    def _on_zoom(self, value):
        scale = value / 100.0
        self.view.resetTransform()
        self.view.scale(scale, scale)

    def load_image(self, path: str):
        self.scene.clear()
        if path:
            from PySide6.QtGui import QPixmap

            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.scene.addPixmap(pixmap)
            else:
                self.scene.addText(f"Failed to load: {path}")
        else:
            self.scene.addText("No preview available.")
