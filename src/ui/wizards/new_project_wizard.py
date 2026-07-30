"""
New Project Wizard - Multi-step QWizard for project creation
"""

import os

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)


class ProjectNamePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 1: Project Name & Location")
        self.setSubTitle("Choose a name and save location for your new project.")

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setText("Untitled_Project")
        self.registerField("project_name*", self.name_edit)
        form.addRow("Project Name:", self.name_edit)

        loc_layout = QHBoxLayout()
        self.loc_edit = QLineEdit()
        self.loc_edit.setText(os.path.expanduser("~"))
        self.registerField("project_location*", self.loc_edit)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)

        loc_layout.addWidget(self.loc_edit)
        loc_layout.addWidget(btn_browse)
        form.addRow("Location:", loc_layout)

        layout.addLayout(form)

    def _browse(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if dir_path:
            self.loc_edit.setText(dir_path)


class TemplatePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 2: Project Template")
        self.setSubTitle("Select a starting template.")

        layout = QVBoxLayout(self)

        self.template_combo = QComboBox()
        self.template_combo.addItems(
            [
                "Blank",
                "Fantasy",
                "Adventure",
                "Kids Story",
                "Educational",
                "Animal Story",
                "Demo Project",
            ]
        )
        self.registerField("template", self.template_combo, "currentText")

        layout.addWidget(QLabel("Template:"))
        layout.addWidget(self.template_combo)
        layout.addStretch()


class SettingsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 3: Configurations")
        self.setSubTitle("Set resolution, framerate, language, and art style.")

        layout = QFormLayout(self)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Japanese", "Spanish", "French"])
        self.registerField("language", self.lang_combo, "currentText")
        layout.addRow("Language:", self.lang_combo)

        self.res_combo = QComboBox()
        self.res_combo.addItems(
            ["1280x720 (720p)", "1920x1080 (1080p)", "3840x2160 (4K)"]
        )
        self.res_combo.setCurrentIndex(1)
        self.registerField("resolution", self.res_combo, "currentText")
        layout.addRow("Resolution:", self.res_combo)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["24", "30", "60"])
        self.registerField("fps", self.fps_combo, "currentText")
        layout.addRow("Frame Rate:", self.fps_combo)

        self.art_combo = QComboBox()
        self.art_combo.addItems(["Anime", "Cartoon", "Storybook", "Manga", "Custom"])
        self.registerField("art_style", self.art_combo, "currentText")
        layout.addRow("Art Style:", self.art_combo)


class SummaryPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 4: Create Project")
        self.setSubTitle("Review your settings.")

        layout = QVBoxLayout(self)
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

    def initializePage(self):
        name = self.field("project_name")
        loc = self.field("project_location")
        temp = self.field("template")
        res = self.field("resolution")
        fps = self.field("fps")
        art = self.field("art_style")

        summary = (
            f"<b>Name:</b> {name}<br>"
            f"<b>Location:</b> {loc}<br>"
            f"<b>Template:</b> {temp}<br>"
            f"<b>Resolution:</b> {res}<br>"
            f"<b>FPS:</b> {fps}<br>"
            f"<b>Art Style:</b> {art}<br>"
            f"<br>Click Finish to generate the project."
        )
        self.summary_label.setText(summary)


class NewProjectWizard(QWizard):
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager

        self.setWindowTitle("Create New ZANIME Project")
        self.setFixedSize(600, 450)

        self.addPage(ProjectNamePage())
        self.addPage(TemplatePage())
        self.addPage(SettingsPage())
        self.addPage(SummaryPage())

    def accept(self):
        # Extract data and pass to project manager
        name = self.field("project_name")
        loc = self.field("project_location")
        # Template and other config logic would be applied to the ProjectModel here

        full_path = os.path.join(loc, f"{name}.zanime")

        self.project_manager.create_project(name, full_path)

        # We can update the model with the wizard fields
        if self.project_manager.project_model:
            self.project_manager.project_model.language = self.field("language")
            self.project_manager.project_model.fps = int(self.field("fps"))
            self.project_manager.project_model.art_style = self.field("art_style")

            res_str = self.field("resolution").split(" ")[0]
            w, h = res_str.split("x")
            self.project_manager.project_model.resolution = (int(w), int(h))

            self.project_manager.save_project()

        super().accept()
