"""
Welcome Workspace - The First Launch Experience for ZANIME Genesis.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_workspace import BaseWorkspace
from src.ui.widgets.welcome_cards import DemoProjectCard, ProjectCard, QuickActionButton

logger = logging.getLogger(__name__)

MOCK_PROJECTS = [
    {
        "name": "Hero Character Setup",
        "modified": "Today",
        "version": "1.0",
        "size": "45MB",
        "pinned": True,
    },
    {
        "name": "City Background Night",
        "modified": "Yesterday",
        "version": "0.9",
        "size": "120MB",
        "pinned": True,
    },
    {
        "name": "Fight Scene Rough",
        "modified": "3 days ago",
        "version": "1.2",
        "size": "34MB",
        "pinned": False,
    },
    {
        "name": "Dialogue Test 01",
        "modified": "Last week",
        "version": "1.0",
        "size": "12MB",
        "pinned": False,
    },
    {
        "name": "Title Sequence",
        "modified": "Last month",
        "version": "2.1",
        "size": "89MB",
        "pinned": False,
    },
]


class WelcomeWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Welcome to Zanime", parent)
        self.app = app

        self.setStyleSheet("background-color: #1e1e24;")
        self.center = QWidget()
        main_layout = QVBoxLayout(self.center)
        main_layout.setContentsMargins(40, 40, 40, 20)
        main_layout.setSpacing(20)

        # 1. TOP BAR
        top_layout = QHBoxLayout()
        logo = QLabel("ZANIME")
        logo.setStyleSheet(
            "font-size: 32px; font-weight: bold; color: #4CAF50; letter-spacing: 2px;"
        )
        version = QLabel("Genesis v0.9.9")
        version.setStyleSheet("font-size: 14px; color: #888; padding-top: 10px;")
        top_layout.addWidget(logo)
        top_layout.addWidget(version)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # 2. CENTER (Left and Right)
        center_layout = QHBoxLayout()
        center_layout.setSpacing(40)

        # 2A. CENTER LEFT (Quick Actions & Demo)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        lbl_quick = QLabel("Quick Actions")
        lbl_quick.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #888; text-transform: uppercase;"
        )
        left_layout.addWidget(lbl_quick)

        left_layout.addWidget(QuickActionButton("New Project"))
        left_layout.addWidget(QuickActionButton("Open Project"))
        left_layout.addWidget(QuickActionButton("Import Project"))
        left_layout.addWidget(QuickActionButton("Recover Autosave"))

        left_layout.addSpacing(20)
        lbl_demo = QLabel("Demo Project")
        lbl_demo.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #888; text-transform: uppercase;"
        )
        left_layout.addWidget(lbl_demo)

        self.demo_card = DemoProjectCard()
        self.demo_card.clicked.connect(self._open_demo)
        left_layout.addWidget(self.demo_card)
        left_layout.addStretch()

        center_layout.addWidget(left_panel, 1)

        # 2B. CENTER RIGHT (Projects)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        search_layout = QHBoxLayout()
        lbl_rec = QLabel("Recent Projects")
        lbl_rec.setStyleSheet("font-size: 18px; font-weight: bold; color: #ddd;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search projects...")
        self.search_box.setStyleSheet(
            "padding: 8px; border-radius: 4px; background-color: #2b2d36; border: 1px solid #3a3f4b; color: #fff;"
        )
        self.search_box.textChanged.connect(self._filter_projects)

        search_layout.addWidget(lbl_rec)
        search_layout.addStretch()
        search_layout.addWidget(self.search_box, 1)
        right_layout.addLayout(search_layout)

        # Scroll Area for Projects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.projects_container = QWidget()
        self.projects_container.setStyleSheet("background: transparent;")
        self.projects_layout = QVBoxLayout(self.projects_container)
        self.projects_layout.setSpacing(10)
        self.projects_layout.setContentsMargins(0, 0, 10, 0)

        scroll.setWidget(self.projects_container)
        right_layout.addWidget(scroll)

        center_layout.addWidget(right_panel, 2)
        main_layout.addLayout(center_layout, 1)

        # 3. BOTTOM BAR (Learning & Links)
        bottom_layout = QHBoxLayout()
        links = [
            "Getting Started",
            "Documentation",
            "FAQ",
            "Keyboard Shortcuts",
            "Settings",
            "Exit",
        ]
        for link in links:
            btn = QPushButton(link)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                "border: none; color: #888; font-size: 12px; background: transparent; padding: 5px;"
            )
            bottom_layout.addWidget(btn)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)
        self.setCentralWidget(self.center)

        self._populate_projects()

    def _populate_projects(self):
        self.project_cards = []

        # Add Pinned Projects First
        pinned_lbl = QLabel("Pinned")
        pinned_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #666; text-transform: uppercase;"
        )
        self.projects_layout.addWidget(pinned_lbl)

        for p in MOCK_PROJECTS:
            if p["pinned"]:
                card = ProjectCard(p)
                card.clicked.connect(self._open_project)
                self.projects_layout.addWidget(card)
                self.project_cards.append(card)

        self.projects_layout.addSpacing(10)

        rec_lbl = QLabel("Recent")
        rec_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #666; text-transform: uppercase;"
        )
        self.projects_layout.addWidget(rec_lbl)

        for p in MOCK_PROJECTS:
            if not p["pinned"]:
                card = ProjectCard(p)
                card.clicked.connect(self._open_project)
                self.projects_layout.addWidget(card)
                self.project_cards.append(card)

        self.projects_layout.addStretch()

    def _filter_projects(self, text):
        search_text = text.lower()
        for card in self.project_cards:
            if search_text in card.project_data["name"].lower():
                card.show()
            else:
                card.hide()

    def _open_demo(self):
        logger.info("WelcomeWizard: Opening Demo Project 'The Crystal Forest'")
        # Graceful error handling for missing demo project per requirements
        QMessageBox.information(
            self,
            "Demo Project",
            "The Crystal Forest demo project is currently downloading or unavailable.\n\nComing Soon!",
        )

    def _open_project(self, data):
        logger.info(f"WelcomeWizard: Opening project: {data.get('name')}")
