"""
Node Graph Scene & Graphics Items — Phase 4 Interactive Node Canvas.

Features:
  - Custom QGraphicsScene with grid background
  - NodeGraphicsItem with title bar, category colors, and typed port sockets
  - ConnectionGraphicsItem with smooth Bezier curve wiring
  - Interactive click-and-drag wire creation
"""

import logging

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsScene

from src.models.node_graph_model import (
    PORT_COLORS,
    NodeConnection,
    NodeGraphModel,
    NodeModel,
    NodePort,
)

logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "Animation": "#007acc",
    "Image":     "#ff922b",
    "Video":     "#cc5de8",
    "Audio":     "#51cf66",
    "AI":        "#f06595",
    "Logic":     "#ffd43b",
    "Math":      "#20c997",
    "Render":    "#e74c3c",
}


class PortGraphicsItem(QGraphicsItem):
    """Circular socket item for a node input or output port."""

    def __init__(self, port: NodePort, is_output: bool, parent=None):
        super().__init__(parent)
        self.port = port
        self.is_output = is_output
        self.radius = 5.0
        self.color = QColor(PORT_COLORS.get(port.port_type, "#ffffff"))

    def boundingRect(self) -> QRectF:
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#111"), 1.5))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(self.boundingRect())


class NodeGraphicsItem(QGraphicsItem):
    """Draggable visual box representing a single node in the graph."""

    def __init__(self, model: NodeModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        self.width = 160
        self.title_height = 24
        self.port_spacing = 20
        self.height = self.title_height + max(len(model.inputs), len(model.outputs), 1) * self.port_spacing + 12

        self.setPos(model.x, model.y)
        self.ports: dict[str, PortGraphicsItem] = {}
        self._create_ports()

    def _create_ports(self):
        y = self.title_height + 12
        for port in self.model.inputs:
            p_item = PortGraphicsItem(port, is_output=False, parent=self)
            p_item.setPos(10, y)
            self.ports[port.port_id] = p_item
            y += self.port_spacing

        y = self.title_height + 12
        for port in self.model.outputs:
            p_item = PortGraphicsItem(port, is_output=True, parent=self)
            p_item.setPos(self.width - 10, y)
            self.ports[port.port_id] = p_item
            y += self.port_spacing

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Body background
        bg_color = QColor("#1a1a28") if not self.isSelected() else QColor("#222238")
        border_color = QColor("#007acc") if self.isSelected() else QColor("#333348")

        painter.setPen(QPen(border_color, 2 if self.isSelected() else 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(self.boundingRect(), 6, 6)

        # Title bar background
        cat_color = QColor(CATEGORY_COLORS.get(self.model.category, "#007acc"))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(cat_color))
        title_rect = QRectF(0, 0, self.width, self.title_height)
        painter.drawRoundedRect(title_rect, 6, 6)
        painter.drawRect(QRectF(0, 12, self.width, 12))  # Squared bottom edge for title bar

        # Title text
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.setFont(QFont("sans-serif", 9, QFont.Bold))
        painter.drawText(title_rect.adjusted(8, 0, -8, 0), Qt.AlignLeft | Qt.AlignVCenter, self.model.name)

        # Port labels
        painter.setFont(QFont("sans-serif", 7))
        y = self.title_height + 16
        for port in self.model.inputs:
            painter.setPen(QPen(QColor("#aaa"), 1))
            painter.drawText(QRectF(20, y - 8, 70, 16), Qt.AlignLeft | Qt.AlignVCenter, port.name)
            y += self.port_spacing

        y = self.title_height + 16
        for port in self.model.outputs:
            painter.setPen(QPen(QColor("#aaa"), 1))
            painter.drawText(QRectF(self.width - 90, y - 8, 70, 16), Qt.AlignRight | Qt.AlignVCenter, port.name)
            y += self.port_spacing

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.model.x = self.pos().x()
            self.model.y = self.pos().y()
            if self.scene():
                self.scene().update_connections()
        return super().itemChange(change, value)


class ConnectionGraphicsItem(QGraphicsPathItem):
    """Bezier curve wire connecting two ports."""

    def __init__(self, connection: NodeConnection, start_pos: QPointF, end_pos: QPointF, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setPen(QPen(QColor("#007acc"), 2))
        self.update_path(start_pos, end_pos)

    def update_path(self, p1: QPointF, p2: QPointF):
        path = QPainterPath(p1)
        dx = abs(p2.x() - p1.x()) * 0.5
        c1 = QPointF(p1.x() + dx, p1.y())
        c2 = QPointF(p2.x() - dx, p2.y())
        path.cubicTo(c1, c2, p2)
        self.setPath(path)


class NodeGraphScene(QGraphicsScene):
    """Custom scene hosting node items and wires with grid background."""

    def __init__(self, model: NodeGraphModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.node_items: dict[str, NodeGraphicsItem] = {}
        self.conn_items: list[ConnectionGraphicsItem] = []
        self.rebuild_scene()

    def rebuild_scene(self):
        self.clear()
        self.node_items.clear()
        self.conn_items.clear()

        # Add Nodes
        for node_model in self.model.nodes:
            item = NodeGraphicsItem(node_model)
            self.addItem(item)
            self.node_items[node_model.uuid] = item

        # Add Connections
        self.update_connections()

    def update_connections(self):
        # Remove old connection items
        for conn_item in self.conn_items:
            self.removeItem(conn_item)
        self.conn_items.clear()

        for conn in self.model.connections:
            from_item = self.node_items.get(conn.from_node_id)
            to_item = self.node_items.get(conn.to_node_id)

            if from_item and to_item:
                from_port = from_item.ports.get(conn.from_port_id)
                to_port = to_item.ports.get(conn.to_port_id)

                if from_port and to_port:
                    p1 = from_item.mapToScene(from_port.pos())
                    p2 = to_item.mapToScene(to_port.pos())
                    item = ConnectionGraphicsItem(conn, p1, p2)
                    self.addItem(item)
                    self.conn_items.append(item)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.fillRect(rect, QColor("#12121c"))

        # Grid lines
        grid_size = 20
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        painter.setPen(QPen(QColor("#1c1c2b"), 1))

        x = left
        while x < rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += grid_size

        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += grid_size
