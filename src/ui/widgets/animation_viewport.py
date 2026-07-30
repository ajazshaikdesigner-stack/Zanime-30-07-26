"""
Animation Viewport
"""

from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class AnimationViewport(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(0, 0, 1920, 1080)
        self.setScene(self.scene_obj)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.scene_obj.addText("Animation Viewport: Select an object to animate")
