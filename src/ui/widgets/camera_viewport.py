"""
Camera Viewport - QGraphicsView drawing compositional guides.
"""

from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class CameraViewport(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(0, 0, 1920, 1080)
        self.setScene(self.scene_obj)
        self.setRenderHint(QPainter.Antialiasing)

        self.scene_obj.addText("Camera Viewport: Simulate Lens and DoF")
        self.composition_mode = "Rule of Thirds"

    def set_composition_mode(self, mode: str):
        self.composition_mode = mode
        self.viewport().update()

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        pen = QPen(QColor(0, 255, 0, 150))
        painter.setPen(pen)
        w, h = 1920, 1080

        if self.composition_mode == "Rule of Thirds":
            painter.drawLine(w / 3, 0, w / 3, h)
            painter.drawLine(2 * w / 3, 0, 2 * w / 3, h)
            painter.drawLine(0, h / 3, w, h / 3)
            painter.drawLine(0, 2 * h / 3, w, 2 * h / 3)
        elif self.composition_mode == "Center":
            painter.drawLine(w / 2, 0, w / 2, h)
            painter.drawLine(0, h / 2, w, h / 2)
