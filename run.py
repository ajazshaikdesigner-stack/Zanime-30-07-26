"""
Execution entry point.
"""

import os
import sys

# Ensure project root is in sys.path so local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The following imports occur after modifying `sys.path` intentionally.
# They are kept here because the path mutation must happen first.  noqa: E402
from PySide6.QtWidgets import QMessageBox  # noqa: E402
from src.core.bootstrap import ApplicationBootstrap  # noqa: E402


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
    bootstrap = ApplicationBootstrap(sys.argv)
    app = bootstrap.initialize_app()

    from src.ui.splash_screen import SplashScreen

    splash = SplashScreen()
    splash.show()

    _ = bootstrap.boot(splash)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
