"""
Movie Canvas - QGraphicsView
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class MovieCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(0, 0, 1920, 1080)
        self.setScene(self.scene_obj)

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Draw target bounds
        self.scene_obj.addRect(0, 0, 1920, 1080, QPen(Qt.black, 2))

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        # Draw Rule of Thirds
        pen = QPen(QColor(255, 255, 255, 100))
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        w = 1920
        h = 1080

        painter.drawLine(w / 3, 0, w / 3, h)
        painter.drawLine(2 * w / 3, 0, 2 * w / 3, h)
        painter.drawLine(0, h / 3, w, h / 3)
        painter.drawLine(0, 2 * h / 3, w, 2 * h / 3)

        # Draw Safe Area
        safe_pen = QPen(QColor(255, 0, 0, 150))
        painter.setPen(safe_pen)
        margin = w * 0.1
        painter.drawRect(QRectF(margin, margin, w - 2 * margin, h - 2 * margin))
