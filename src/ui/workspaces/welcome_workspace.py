"""
Welcome Workspace - Premium first-launch experience for ZANIME.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.managers.project_manager import ProjectManager
from src.core.managers.workspace_manager import WorkspaceManager
from src.core.sdk.base_workspace import BaseWorkspace
from src.core.services.service_registry import registry
from src.ui.widgets.welcome_cards import DemoProjectCard, ProjectCard, QuickActionButton

logger = logging.getLogger(__name__)

MOCK_PROJECTS = [
    {"name": "Hero Character Setup",    "modified": "Today",       "version": "1.0", "size": "45 MB",  "pinned": True},
    {"name": "City Background Night",   "modified": "Yesterday",   "version": "0.9", "size": "120 MB", "pinned": True},
    {"name": "Fight Scene Rough",       "modified": "3 days ago",  "version": "1.2", "size": "34 MB",  "pinned": False},
    {"name": "Dialogue Test 01",        "modified": "Last week",   "version": "1.0", "size": "12 MB",  "pinned": False},
    {"name": "Title Sequence",          "modified": "Last month",  "version": "2.1", "size": "89 MB",  "pinned": False},
]


class WelcomeWorkspace(BaseWorkspace):
    def __init__(self, app, parent=None):
        super().__init__("Welcome to Zanime", parent)
        self.app = app

        self.setStyleSheet("background-color: #0d0f17;")
        root = QWidget()
        root.setStyleSheet("background-color: #0d0f17;")
        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Hero Header ──────────────────────────────────────────────────
        hero = self._build_hero()
        main.addWidget(hero)

        # ── Body (2 columns) ─────────────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(32, 24, 32, 16)
        body.setSpacing(28)

        body.addLayout(self._build_left_panel(), 1)
        body.addLayout(self._build_right_panel(), 2)

        main.addLayout(body, 1)

        # ── Footer ───────────────────────────────────────────────────────
        footer = self._build_footer()
        main.addWidget(footer)

        self.setCentralWidget(root)
        self._populate_projects()

    # ── Section builders ─────────────────────────────────────────────────

    def _build_hero(self):
        hero = QWidget()
        hero.setFixedHeight(120)
        hero.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d0f17, stop:0.3 #130d28, stop:0.7 #130d28, stop:1 #0d0f17);
            border-bottom: 1px solid #1e2235;
        """)
        layout = QHBoxLayout(hero)
        layout.setContentsMargins(36, 0, 36, 0)
        layout.setSpacing(0)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title_lbl = QLabel("ZANIME")
        title_lbl.setStyleSheet(
            "font-size: 32pt; font-weight: 900; color: #7c3aed; "
            "letter-spacing: 4px; background: transparent;"
        )
        version_lbl = QLabel("v2  Genesis")
        version_lbl.setStyleSheet(
            "font-size: 11pt; color: #4c1d95; padding-top: 16px; "
            "letter-spacing: 1px; background: transparent;"
        )
        title_row.addWidget(title_lbl)
        title_row.addWidget(version_lbl)
        title_row.addStretch()
        text_col.addLayout(title_row)

        tagline = QLabel("AI-Powered 2D Animation Studio  —  Create. Animate. Tell Your Story.")
        tagline.setStyleSheet(
            "font-size: 10pt; color: #475569; background: transparent; letter-spacing: 0.5px;"
        )
        text_col.addWidget(tagline)

        layout.addLayout(text_col)
        layout.addStretch()

        # Right side: stat badges
        stats_row = QHBoxLayout()
        stats_row.setSpacing(24)
        for count, label in [("14", "Workspaces"), ("∞", "AI Tools"), ("1", "Studio")]:
            stat = QVBoxLayout()
            count_lbl = QLabel(count)
            count_lbl.setStyleSheet(
                "font-size: 18pt; font-weight: bold; color: #a78bfa; background: transparent;"
            )
            count_lbl.setAlignment(Qt.AlignCenter)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 8pt; color: #475569; background: transparent;")
            lbl.setAlignment(Qt.AlignCenter)
            stat.addWidget(count_lbl)
            stat.addWidget(lbl)
            stats_row.addLayout(stat)
        layout.addLayout(stats_row)

        return hero

    def _build_left_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Section header
        qa_lbl = QLabel("QUICK ACTIONS")
        qa_lbl.setStyleSheet(
            "font-size: 7pt; font-weight: bold; color: #334155; "
            "letter-spacing: 2px; padding-bottom: 4px; background: transparent;"
        )
        layout.addWidget(qa_lbl)

        # Quick action buttons (icon + label + subtitle)
        actions = [
            ("⊕", "New Project",      "Start from scratch",          self._on_new_project),
            ("📂", "Open Project",     "Browse existing projects",    self._on_open_project),
            ("📥", "Import Project",   "Import from ZIP or folder",   self._on_import),
            ("♻", "Recover Autosave", "Restore unsaved work",        self._on_recover),
        ]
        for emoji, text, sub, handler in actions:
            btn = QuickActionButton(emoji, text, sub)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addSpacing(16)

        # Demo card
        demo_lbl = QLabel("FEATURED PROJECT")
        demo_lbl.setStyleSheet(
            "font-size: 7pt; font-weight: bold; color: #334155; "
            "letter-spacing: 2px; padding-bottom: 4px; background: transparent;"
        )
        layout.addWidget(demo_lbl)

        self.demo_card = DemoProjectCard()
        self.demo_card.clicked.connect(self._open_demo)
        layout.addWidget(self.demo_card)

        layout.addStretch()
        return layout

    def _build_right_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Header row
        header_row = QHBoxLayout()
        rec_lbl = QLabel("Recent Projects")
        rec_lbl.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #e2e8f0; background: transparent;"
        )
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search projects...")
        self.search_box.setFixedWidth(220)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 7px 12px;
                border-radius: 20px;
                background-color: #13151f;
                border: 1px solid #1e2235;
                color: #e2e8f0;
                font-size: 9pt;
            }
            QLineEdit:focus { border-color: #7c3aed; }
        """)
        self.search_box.textChanged.connect(self._filter_projects)
        header_row.addWidget(rec_lbl)
        header_row.addStretch()
        header_row.addWidget(self.search_box)
        layout.addLayout(header_row)

        # Scroll area for project cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #0d0f17; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #1e2235; border-radius: 3px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #2d3154; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.projects_container = QWidget()
        self.projects_container.setStyleSheet("background: transparent;")
        self.projects_layout = QVBoxLayout(self.projects_container)
        self.projects_layout.setSpacing(8)
        self.projects_layout.setContentsMargins(0, 0, 6, 0)
        scroll.setWidget(self.projects_container)
        layout.addWidget(scroll)
        return layout

    def _build_footer(self):
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet(
            "background-color: #0a0c14; border-top: 1px solid #1e2235;"
        )
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(0)

        links = [
            ("Getting Started",    self._on_getting_started),
            ("Documentation",      self._on_docs),
            ("Keyboard Shortcuts", self._on_shortcuts),
            ("Settings",           self._on_settings),
        ]
        for i, (label, handler) in enumerate(links):
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    border: none; color: #334155; font-size: 8pt;
                    background: transparent; padding: 0 14px;
                }
                QPushButton:hover { color: #a78bfa; }
            """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
            if i < len(links) - 1:
                sep = QLabel("·")
                sep.setStyleSheet("color: #1e2235; background: transparent;")
                layout.addWidget(sep)

        layout.addStretch()

        copyright_lbl = QLabel("© 2026 ZANIME Studio")
        copyright_lbl.setStyleSheet("color: #1e293b; font-size: 8pt; background: transparent;")
        layout.addWidget(copyright_lbl)
        return footer

    # ── Project population ────────────────────────────────────────────────

    def _populate_projects(self):
        self.project_cards = []

        pinned_lbl = QLabel("PINNED")
        pinned_lbl.setStyleSheet(
            "font-size: 7pt; font-weight: bold; color: #334155; "
            "letter-spacing: 2px; padding: 4px 0; background: transparent;"
        )
        self.projects_layout.addWidget(pinned_lbl)

        for p in MOCK_PROJECTS:
            if p["pinned"]:
                card = ProjectCard(p)
                card.clicked.connect(self._open_project)
                self.projects_layout.addWidget(card)
                self.project_cards.append(card)

        self.projects_layout.addSpacing(8)

        rec_lbl = QLabel("RECENT")
        rec_lbl.setStyleSheet(
            "font-size: 7pt; font-weight: bold; color: #334155; "
            "letter-spacing: 2px; padding: 4px 0; background: transparent;"
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
        for card in self.project_cards:
            card.setVisible(text.lower() in card.project_data["name"].lower())

    # ── Handlers ──────────────────────────────────────────────────────────

    def _on_new_project(self):
        if self.app:
            from src.ui.wizards.new_project_wizard import NewProjectWizard
            wizard = NewProjectWizard(registry.get(ProjectManager), self)
            if wizard.exec():
                registry.get(WorkspaceManager).set_workspace("Home")

    def _on_open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open ZANIME Project", "", "Zanime Projects (*.zanime);;All Files (*)")
        if path:
            try:
                registry.get(ProjectManager).open_project(path)
                registry.get(WorkspaceManager).set_workspace("Home")
            except Exception as e:
                QMessageBox.warning(self, "Open Project", f"Could not open project:\n{e}")

    def _on_import(self):
        QMessageBox.information(self, "Import Project",
            "Import from ZIP or folder — coming in the next release.")

    def _on_recover(self):
        QMessageBox.information(self, "Recover Autosave",
            "No autosave found. Your work was last saved successfully.")

    def _open_demo(self):
        logger.info("WelcomeWorkspace: Opening Demo Project 'The Crystal Forest'")
        from src.core.managers.demo_manager import DemoProjectManager
        demo_path = DemoProjectManager.ensure_demo_project()
        try:
            registry.get(ProjectManager).open_project(demo_path)
            registry.get(WorkspaceManager).set_workspace("Home")
        except Exception as e:
            QMessageBox.warning(self, "Open Demo", f"Could not open demo project:\n{e}")

    def _open_project(self, data):
        logger.info(f"WelcomeWorkspace: Opening project: {data.get('name')}")
        from src.core.managers.demo_manager import DemoProjectManager
        demo_path = DemoProjectManager.ensure_demo_project()
        try:
            registry.get(ProjectManager).open_project(demo_path)
            registry.get(WorkspaceManager).set_workspace("Home")
        except Exception as e:
            QMessageBox.warning(self, "Open Project", f"Could not open project:\n{e}")

    def _on_getting_started(self):
        registry.get(WorkspaceManager).set_workspace("Home")

    def _on_docs(self):
        import webbrowser
        webbrowser.open("https://github.com/zanime/docs")

    def _on_shortcuts(self):
        QMessageBox.information(self, "Keyboard Shortcuts",
            "Ctrl+N — New Project\nCtrl+O — Open\nCtrl+S — Save\n"
            "Ctrl+Z — Undo\nCtrl+Y — Redo\nF11 — Full Screen\nCtrl+Q — Exit")

    def _on_settings(self):
        registry.get(WorkspaceManager).set_workspace("Settings")
