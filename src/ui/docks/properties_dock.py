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
from typing import Any

from src.core.sdk.base_dock import BaseDock


from src.core.services.service_registry import registry
from src.core.events.event_bus import EventBus
from src.core.events.event_types import Event
from src.core.sdk.inspectable import IInspectable

class PropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Properties", parent)

        self.layout = QVBoxLayout(self.container)
        
        # We wrap the form layout in a scroll area to handle many properties
        from PySide6.QtWidgets import QScrollArea, QWidget
        from PySide6.QtCore import Qt
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll_content = QWidget()
        self.form_layout = QFormLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)
        self.layout.addStretch()

        self._current_inspectable: IInspectable | None = None
        
        try:
            registry.get(EventBus).subscribe(Event.SELECTION_CHANGED, self._on_selection_changed)
        except KeyError:
            pass

    def _on_selection_changed(self, selected_items: list):
        # Clear current layout
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._current_inspectable = None
        
        if not selected_items:
            self.form_layout.addRow(QLabel("No selection."))
            return

        # For simplicity, we just inspect the first item
        item = selected_items[0]
        if isinstance(item, IInspectable):
            self._current_inspectable = item
            self._build_properties(item.get_properties())
        else:
            self.form_layout.addRow(QLabel(f"Selected: {type(item).__name__} (Not Inspectable)"))

    def _build_properties(self, properties: list[dict]):
        for prop in properties:
            pid = prop["id"]
            ptype = prop["type"]
            val = prop.get("value")
            
            if ptype == "string":
                widget = QLineEdit(str(val) if val else "")
                widget.textEdited.connect(lambda text, p=pid: self._update_property(p, text))
                self.form_layout.addRow(prop["label"], widget)
            elif ptype == "int":
                widget = QSpinBox()
                if "min" in prop: widget.setMinimum(prop["min"])
                if "max" in prop: widget.setMaximum(prop["max"])
                widget.setValue(int(val) if val else 0)
                widget.valueChanged.connect(lambda v, p=pid: self._update_property(p, v))
                self.form_layout.addRow(prop["label"], widget)
            elif ptype == "bool":
                widget = QCheckBox()
                widget.setChecked(bool(val))
                widget.stateChanged.connect(lambda v, p=pid: self._update_property(p, bool(v)))
                self.form_layout.addRow(prop["label"], widget)
            elif ptype == "enum":
                widget = QComboBox()
                opts = prop.get("options", [])
                widget.addItems(opts)
                if val in opts:
                    widget.setCurrentText(val)
                widget.currentTextChanged.connect(lambda t, p=pid: self._update_property(p, t))
                self.form_layout.addRow(prop["label"], widget)
            else:
                self.form_layout.addRow(prop["label"], QLabel(str(val)))

    def _update_property(self, property_id: str, value: Any):
        if self._current_inspectable:
            self._current_inspectable.set_property(property_id, value)
