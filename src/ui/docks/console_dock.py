"""
Console dock for viewing logs.
"""

import logging

from PySide6.QtWidgets import QTextEdit, QVBoxLayout

from src.core.sdk.base_dock import BaseDock


class ConsoleDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Console", parent)

        layout = QVBoxLayout(self.container)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(
            "font-family: Consolas, monospace; background-color: #1e1e1e; color: #d4d4d4;"
        )

        layout.addWidget(self.text_edit)

        # Attach a logging handler
        class QtHandler(logging.Handler):
            def __init__(self, text_edit):
                super().__init__()
                self.text_edit = text_edit

            def emit(self, record):
                msg = self.format(record)
                self.text_edit.append(msg)

        self.handler = QtHandler(self.text_edit)
        self.handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.getLogger().addHandler(self.handler)
