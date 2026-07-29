"""
Window Manager for handling dialogs and layout state.
"""
import logging
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class WindowManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.main_window = None
        
    def set_main_window(self, window):
        self.main_window = window
        logger.info("WindowManager: Main Window registered.")
        
    def spawn_dialog(self, dialog_class, *args, **kwargs):
        """Helper to spawn centered dialogs with correct parenting."""
        dialog = dialog_class(self.main_window, *args, **kwargs)
        return dialog.exec()
