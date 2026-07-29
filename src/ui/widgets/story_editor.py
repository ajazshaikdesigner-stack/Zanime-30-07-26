"""
Story Editor component with Toolbar
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QToolBar
from PySide6.QtGui import QAction

class StoryEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tools Toolbar
        self.toolbar = QToolBar("Story Tools")
        self.action_rewrite = QAction("Rewrite", self)
        self.action_expand = QAction("Expand", self)
        self.action_shorten = QAction("Shorten", self)
        self.action_continue = QAction("Continue", self)
        self.action_simplify = QAction("Simplify", self)
        self.action_grammar = QAction("Grammar Check", self)
        
        self.toolbar.addAction(self.action_rewrite)
        self.toolbar.addAction(self.action_expand)
        self.toolbar.addAction(self.action_shorten)
        self.toolbar.addAction(self.action_continue)
        self.toolbar.addAction(self.action_simplify)
        self.toolbar.addAction(self.action_grammar)
        
        layout.addWidget(self.toolbar)
        
        # Text Editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Once upon a time...")
        layout.addWidget(self.text_edit)
        
    def set_locked(self, locked: bool):
        self.text_edit.setReadOnly(locked)
        self.toolbar.setDisabled(locked)
