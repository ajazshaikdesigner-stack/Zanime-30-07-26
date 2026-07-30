"""
Theme Engine for dynamic QSS and scaling.
"""

import json
import logging
import os

from PySide6.QtWidgets import QApplication

from src.core.managers.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class ThemeEngine:
    def __init__(self, config: ConfigurationManager, app: QApplication):
        self.config = config
        self.app = app
        self.current_theme = self.config.get("default_theme", "dark")
        self.theme_dir = "src/ui/theme"

        if not os.path.exists(self.theme_dir) or not os.path.exists(
            os.path.join(self.theme_dir, "palette.json")
        ):
            os.makedirs(self.theme_dir, exist_ok=True)
            self._generate_default_theme()

    def _generate_default_theme(self):
        palette = {
            "dark": {
                "bg_color": "#1e1e1e",
                "fg_color": "#e0e0e0",
                "accent_color": "#007acc",
                "border_color": "#3f3f46",
            },
            "light": {
                "bg_color": "#ffffff",
                "fg_color": "#111111",
                "accent_color": "#007acc",
                "border_color": "#cccccc",
            },
        }
        with open(os.path.join(self.theme_dir, "palette.json"), "w") as f:
            json.dump(palette, f, indent=4)

        base_qss = """
QMainWindow {
    background-color: @bg_color;
    color: @fg_color;
}
QWidget {
    background-color: @bg_color;
    color: @fg_color;
    font-size: @font_size;
}
QMenuBar {
    background-color: @bg_color;
    border-bottom: 1px solid @border_color;
}
QToolBar {
    border-bottom: 1px solid @border_color;
}
QStatusBar {
    background-color: @accent_color;
    color: #ffffff;
}
QPushButton {
    background-color: @accent_color;
    color: #ffffff;
    border-radius: 4px;
    padding: 5px;
}
QDockWidget::title {
    background: @bg_color;
    border-bottom: 1px solid @border_color;
    padding: 6px;
}
        """
        with open(os.path.join(self.theme_dir, "base.qss"), "w") as f:
            f.write(base_qss)

    def apply_theme(self):
        """Generates and applies the QSS to the QApplication."""
        from PySide6.QtGui import QFont

        screen = self.app.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        scale = dpi / 96.0

        logger.info(
            f"ThemeEngine: Applying '{self.current_theme}' theme (DPI Scale: {scale:.2f})"
        )

        try:
            with open(os.path.join(self.theme_dir, "palette.json"), "r") as f:
                palettes = json.load(f)
            with open(os.path.join(self.theme_dir, "base.qss"), "r") as f:
                qss = f.read()

            active_palette = palettes.get(self.current_theme, palettes["dark"])

            # Replace all palette token variables (longest keys first to avoid partial matches)
            for key in sorted(active_palette.keys(), key=len, reverse=True):
                qss = qss.replace(f"@{key}", active_palette[key])

            font_size_pt = int(10 * scale)
            qss = qss.replace("@font_size", f"{font_size_pt}pt")

            # Apply global font
            font_family = active_palette.get("font_family", "Segoe UI")
            app_font = QFont(font_family, font_size_pt)
            self.app.setFont(app_font)

            self.app.setStyleSheet(qss)
            logger.info(f"ThemeEngine: Theme applied successfully ({len(qss)} chars QSS)")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to apply theme: {e}")
