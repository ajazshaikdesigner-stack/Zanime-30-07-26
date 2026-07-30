"""
Welcome screen shown when no project is loaded.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from src.core.managers.configuration_manager import ConfigurationManager
from src.core.managers.notification_manager import NotificationManager
from src.core.managers.project_manager import ProjectManager
from src.core.managers.workspace_manager import WorkspaceManager
from src.core.services.service_registry import registry


class WelcomeScreen(QDialog):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Welcome to ZANIME")
        self.setFixedSize(700, 450)

        # We assume the QSS theme is already applied globally by ThemeEngine
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(40)

        # Left Panel (Actions)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        title = QLabel("ZANIME")
        title.setStyleSheet("font-size: 28pt; font-weight: bold; color: #007acc;")
        left_panel.addWidget(title)

        subtitle = QLabel("Start creating today.")
        subtitle.setStyleSheet("font-size: 12pt; color: #aaaaaa; margin-bottom: 20px;")
        left_panel.addWidget(subtitle)

        btn_new = QPushButton("New Project")
        btn_new.setMinimumHeight(40)
        btn_new.clicked.connect(self._on_new_project)

        btn_open = QPushButton("Open Existing Project")
        btn_open.setMinimumHeight(40)
        btn_open.clicked.connect(self._on_open_project)

        btn_demo = QPushButton("Open Demo Project")
        btn_demo.setMinimumHeight(40)
        btn_demo.clicked.connect(self._on_demo_project)

        left_panel.addWidget(btn_new)
        left_panel.addWidget(btn_open)
        left_panel.addWidget(btn_demo)
        left_panel.addStretch()

        # Right Panel (Recent Projects)
        right_panel = QVBoxLayout()
        recent_label = QLabel("Recent Projects")
        recent_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #e0e0e0;"
        )

        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #3f3f46;
                background-color: #252526;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3f3f46;
            }
            QListWidget::item:hover {
                background-color: #2d2d30;
            }
        """)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_clicked)
        self._populate_recent()

        right_panel.addWidget(recent_label)
        right_panel.addWidget(self.recent_list)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

    def _populate_recent(self):
        recents = registry.get(ConfigurationManager).get("recent_projects", [])
        if not recents:
            self.recent_list.addItem("No recent projects found.")
            self.recent_list.item(0).setFlags(Qt.NoItemFlags)  # Unselectable
        else:
            for proj in recents:
                name = os.path.basename(proj).replace(".zanime", "")
                # Format: [Icon] Name | Path | Pinned/Fav mock
                item_text = f"★ {name}\n{proj}\nLast Opened: Today | Duration: 00:00:00"

                item = QListWidgetItem(item_text)
                self.recent_list.addItem(item)

    def _on_new_project(self):
        from src.ui.wizards.new_project_wizard import NewProjectWizard

        wizard = NewProjectWizard(registry.get(ProjectManager), self)
        if wizard.exec() and registry.get(ProjectManager).current_project_path:
            self._update_recents(registry.get(ProjectManager).current_project_path)
            self.accept()

    def _on_open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Zanime Projects (*.zanime)"
        )
        if path:
            registry.get(ProjectManager).open_project(path)
            self._update_recents(path)
            self.accept()

    def _on_demo_project(self):
        from src.core.managers.demo_manager import DemoProjectManager

        demo_path = DemoProjectManager.ensure_demo_project()
        registry.get(ProjectManager).open_project(demo_path)
        self._update_recents(demo_path)
        registry.get(WorkspaceManager).set_workspace("Home")
        self.accept()

    def _on_recent_clicked(self, item):
        path = item.text()
        if os.path.exists(path):
            registry.get(ProjectManager).open_project(path)
            self._update_recents(path)
            self.accept()
        else:
            registry.get(NotificationManager).show_error(f"Project not found: {path}")

    def _update_recents(self, path):
        recents = registry.get(ConfigurationManager).get("recent_projects", [])
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        registry.get(ConfigurationManager).set_user(
            "recent_projects", recents[:10]
        )  # Keep last 10
