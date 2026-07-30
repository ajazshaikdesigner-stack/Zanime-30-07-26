"""
Toolbox Dock - Global tool selection.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QPushButton,
    QVBoxLayout,
)

from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.base_dock import BaseDock
from src.core.services.service_registry import registry


class ToolboxDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Toolbox", parent)

        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignTop)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        tools = [
            ("Select", "pointer"),
            ("Move", "move"),
            ("Rotate", "rotate"),
            ("Scale", "scale"),
            ("Brush", "brush"),
            ("Erase", "eraser"),
            ("Text", "text"),
            ("Camera", "camera"),
        ]

        for i, (name, icon) in enumerate(tools):
            btn = QPushButton(name)
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            
            # Simple styling for the tool buttons
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    background-color: #333;
                    border: 1px solid #555;
                    border-radius: 4px;
                    text-align: left;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    border: 1px solid #0098ff;
                }
                QPushButton:hover:!checked {
                    background-color: #444;
                }
            """)
            
            self.button_group.addButton(btn, i)
            layout.addWidget(btn)

        self.button_group.idClicked.connect(self._on_tool_selected)

    def _on_tool_selected(self, tool_id: int):
        btn = self.button_group.button(tool_id)
        if btn:
            try:
                registry.get(EventBus).publish(Event.TOOL_CHANGED, btn.text())
            except KeyError:
                pass
