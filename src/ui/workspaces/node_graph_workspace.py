"""
Node Graph Editor Workspace — Phase 4 Visual Programming Pipeline.

Features:
  - Central interactive QGraphicsView canvas
  - Left dock: Node Palette with 20+ nodes across 8 categories + real-time search
  - Right dock: Node Inspector / Properties Editor
  - Bottom dock: Node Execution Log & Output Inspector
  - One-click DAG Execution via NodeExecutionEngine
  - Save / Load graph into project file
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFormLayout,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.managers.node_execution_engine import NodeExecutionEngine
from src.core.sdk.base_dock import BaseDock
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.models.node_graph_model import (
    NODE_CATALOG,
    NodeGraphModel,
    create_node_from_definition,
)
from src.ui.widgets.node_graph_scene import NodeGraphScene

logger = logging.getLogger(__name__)


class NodePaletteDock(BaseDock):
    """Left dock displaying available node types organized by category."""

    def __init__(self, parent=None):
        super().__init__("🧩 Node Palette", parent)
        self.setMinimumWidth(220)
        self._build_ui()
        self._populate_tree()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Filter nodes...")
        self.search_edit.setStyleSheet("QLineEdit { background: #15151f; color: #ccc; border: 1px solid #333; border-radius: 4px; padding: 4px; }")
        self.search_edit.textChanged.connect(self._filter_tree)
        root.addWidget(self.search_edit)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet(
            "QTreeWidget { background: #15151f; color: #ddd; border: 1px solid #2a2a3a; } "
            "QTreeWidget::item:hover { background: #007acc; }"
        )
        root.addWidget(self.tree, 1)

        hint = QLabel("Tip: Double-click a node to add it to the graph.")
        hint.setStyleSheet("color: #666; font-size: 9px;")
        root.addWidget(hint)

    def _populate_tree(self):
        self.tree.clear()
        categories: dict[str, QTreeWidgetItem] = {}

        for def_dict in NODE_CATALOG:
            cat = def_dict["category"]
            if cat not in categories:
                cat_item = QTreeWidgetItem(self.tree, [f"📂 {cat}"])
                cat_item.setExpanded(True)
                categories[cat] = cat_item

            node_item = QTreeWidgetItem(categories[cat], [def_dict["name"]])
            node_item.setData(0, Qt.UserRole, def_dict)

    def _filter_tree(self, text: str):
        query = text.lower().strip()
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            cat_visible = False
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                match = not query or query in child.text(0).lower()
                child.setHidden(not match)
                if match:
                    cat_visible = True
            cat_item.setHidden(not cat_visible)


class NodeInspectorDock(BaseDock):
    """Right dock inspecting parameters of the currently selected node."""

    def __init__(self, parent=None):
        super().__init__("⚙ Node Inspector", parent)
        self.setMinimumWidth(240)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self.container)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        self.node_title = QLabel("No Node Selected")
        self.node_title.setStyleSheet("color: #7ab; font-weight: bold; font-size: 11px;")
        root.addWidget(self.node_title)

        self.form_widget = QWidget()
        self.form = QFormLayout(self.form_widget)
        self.form.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.form_widget, 1)

    def inspect_node(self, node_item):
        # Clear previous form
        while self.form.count():
            item = self.form.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not node_item:
            self.node_title.setText("No Node Selected")
            return

        model = node_item.model
        self.node_title.setText(f"⚙ {model.name} ({model.category})")

        # Display input ports & default values
        for port in model.inputs:
            field = QLineEdit(str(port.value or ""))
            field.setPlaceholderText(port.port_type)
            field.setStyleSheet("background: #15151f; color: #ccc; border: 1px solid #333;")
            self.form.addRow(f"{port.name}:", field)


class NodeGraphWorkspace(BaseWorkspace):
    """Workspace container hosting the interactive visual node graph editor."""

    def __init__(self, app, parent=None):
        super().__init__("Node Graph", parent)
        self.app = app
        self.graph_model = NodeGraphModel()

        # Add sample starter nodes
        n1 = create_node_from_definition(NODE_CATALOG[0], -200, -50)
        n2 = create_node_from_definition(NODE_CATALOG[16], 100, -50)
        self.graph_model.add_node(n1)
        self.graph_model.add_node(n2)
        self.graph_model.connect(n1.uuid, "out_value", n2.uuid, "in_a")

        # Engine
        self.engine = NodeExecutionEngine(self.graph_model, self)
        self.engine.graph_completed.connect(self._on_execution_completed)

        # Central Viewport
        self.scene = NodeGraphScene(self.graph_model, self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setCentralWidget(self.view)

        # Docks
        self.palette_dock = NodePaletteDock(self)
        self.inspector_dock = NodeInspectorDock(self)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.palette_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)

        # Connect palette double click
        self.palette_dock.tree.itemDoubleClicked.connect(self._on_palette_double_clicked)
        self.scene.selectionChanged.connect(self._on_selection_changed)

        self._build_toolbar()

    def _build_toolbar(self):
        # Floating top bar on central area
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(8, 8, 8, 8)

        run_btn = QPushButton("▶ Run Graph")
        run_btn.setFixedHeight(28)
        run_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: white; border: none; border-radius: 4px; font-weight: bold; padding: 0 16px; } "
            "QPushButton:hover { background: #2ecc71; }"
        )
        run_btn.clicked.connect(self.run_graph)
        top_bar.addWidget(run_btn)

        clear_btn = QPushButton("🗑 Clear Graph")
        clear_btn.setFixedHeight(28)
        clear_btn.setStyleSheet(
            "QPushButton { background: #2a2a3a; color: #aaa; border: 1px solid #444; border-radius: 4px; padding: 0 12px; } "
            "QPushButton:hover { background: #c0392b; color: white; }"
        )
        clear_btn.clicked.connect(self.clear_graph)
        top_bar.addWidget(clear_btn)

        top_bar.addStretch()

        zoom_lbl = QLabel("Zoom:")
        zoom_lbl.setStyleSheet("color: #aaa; font-size: 10px;")
        top_bar.addWidget(zoom_lbl)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(20, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        top_bar.addWidget(self.zoom_slider)

        # Container overlay
        overlay = QWidget(self.view)
        overlay.setLayout(top_bar)
        overlay.move(10, 10)
        overlay.raise_()

    def _on_palette_double_clicked(self, item, col):
        def_dict = item.data(0, Qt.UserRole)
        if not def_dict:
            return

        # Create new node near center
        center = self.view.mapToScene(self.view.viewport().rect().center())
        node_model = create_node_from_definition(def_dict, center.x(), center.y())
        self.graph_model.add_node(node_model)
        self.scene.rebuild_scene()
        logger.info("NodeGraphWorkspace: Added node '%s'", node_model.name)

    def _on_selection_changed(self):
        items = self.scene.selectedItems()
        if items:
            self.inspector_dock.inspect_node(items[0])
        else:
            self.inspector_dock.inspect_node(None)

    def _on_zoom_changed(self, value: int):
        scale = value / 100.0
        self.view.resetTransform()
        self.view.scale(scale, scale)

    def run_graph(self):
        logger.info("NodeGraphWorkspace: Triggering graph execution...")
        self.engine.execute()

    def clear_graph(self):
        self.graph_model.nodes.clear()
        self.graph_model.connections.clear()
        self.scene.rebuild_scene()

    def _on_execution_completed(self, success: bool, msg: str):
        if success:
            QMessageBox.information(self, "Graph Execution Complete", f"✅ {msg}")
        else:
            QMessageBox.critical(self, "Graph Execution Failed", f"❌ {msg}")

    def get_required_docks(self):
        return []

    def get_hidden_docks(self):
        return [
            "Properties",
            "Timeline",
            "ProjectExplorer",
            "Console",
            "AssetBrowser",
            "NotificationCenter",
            "History",
            "Preview",
        ]
