"""
Execution entry point.
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import ZanimeApp
from src.ui.main_window import ZanimeMainWindow
from PySide6.QtWidgets import QMessageBox

def global_exception_handler(exctype, value, tb):
    """Hooks into global exceptions to prevent hard crashes."""
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    logger.error("Uncaught exception", exc_info=(exctype, value, tb))
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    
    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("ZANIME Critical Error")
        msg_box.setText("An unexpected error occurred.")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()
    except Exception:
        print(error_msg)

sys.excepthook = global_exception_handler

def main():
    app = ZanimeApp(sys.argv)
    
    from src.ui.splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    
    main_window = app.startup_manager.boot(splash)
    
    from src.core.services.service_registry import registry
    from src.core.managers.application_manager import ApplicationManager
    registry.get(ApplicationManager).startup()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
