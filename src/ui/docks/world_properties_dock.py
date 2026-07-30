"""
World Properties Dock
"""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_dock import BaseDock


class WorldPropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("World Properties", parent)

        layout = QVBoxLayout(self.container)

        self.stack = QStackedWidget()
        self._setup_env_form()
        self._setup_prop_form()

        layout.addWidget(self.stack)

        self.generate_btn = QPushButton("Generate with AI")
        layout.addWidget(self.generate_btn)

    def _setup_env_form(self):
        self.env_widget = QWidget()
        form = QFormLayout(self.env_widget)

        self.env_name = QLineEdit()
        form.addRow("Name:", self.env_name)

        self.env_style = QComboBox()
        self.env_style.addItems(["Anime", "Realistic", "Cartoon", "Painterly"])
        form.addRow("Style:", self.env_style)

        self.env_lighting = QComboBox()
        self.env_lighting.addItems(["Daylight", "Night", "Sunset", "Moody", "Studio"])
        form.addRow("Lighting:", self.env_lighting)

        self.env_weather = QComboBox()
        self.env_weather.addItems(["Sunny", "Rain", "Snow", "Fog", "Cloudy"])
        form.addRow("Weather:", self.env_weather)

        self.env_season = QComboBox()
        self.env_season.addItems(["Summer", "Winter", "Rainy", "Autumn", "Spring"])
        form.addRow("Season:", self.env_season)

        self.stack.addWidget(self.env_widget)

    def _setup_prop_form(self):
        self.prop_widget = QWidget()
        form = QFormLayout(self.prop_widget)

        self.prop_name = QLineEdit()
        form.addRow("Name:", self.prop_name)

        self.prop_material = QComboBox()
        self.prop_material.addItems(["Wood", "Metal", "Plastic", "Stone", "Cloth"])
        form.addRow("Material:", self.prop_material)

        self.prop_size = QComboBox()
        self.prop_size.addItems(["Small", "Medium", "Large"])
        form.addRow("Size:", self.prop_size)

        self.stack.addWidget(self.prop_widget)

    def show_env_properties(self):
        self.stack.setCurrentWidget(self.env_widget)

    def show_prop_properties(self):
        self.stack.setCurrentWidget(self.prop_widget)
