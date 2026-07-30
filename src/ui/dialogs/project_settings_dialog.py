"""
Project Settings Dialog
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.models.base import ProjectModel


class ProjectSettingsDialog(QDialog):
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setWindowTitle("Project Settings")
        self.setFixedSize(550, 500)

        self.model: ProjectModel = self.project_manager.project_model

        if not self.model:
            # Fallback if no project is loaded
            self.model = ProjectModel()

        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow("Project Name:", self.name_edit)

        self.author_edit = QLineEdit()
        form_layout.addRow("Author:", self.author_edit)

        self.company_edit = QLineEdit()
        form_layout.addRow("Company:", self.company_edit)

        self.copyright_edit = QLineEdit()
        form_layout.addRow("Copyright:", self.copyright_edit)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Japanese", "Spanish", "French"])
        form_layout.addRow("Language:", self.lang_combo)

        self.art_combo = QComboBox()
        self.art_combo.addItems(["Anime", "Cartoon", "Storybook", "Manga", "Custom"])
        form_layout.addRow("Art Style:", self.art_combo)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(
            [
                "1280x720 (720p)",
                "1920x1080 (1080p)",
                "2560x1440 (1440p)",
                "3840x2160 (4K)",
            ]
        )
        form_layout.addRow("Resolution:", self.resolution_combo)

        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["16:9", "4:3", "1:1"])
        form_layout.addRow("Aspect Ratio:", self.aspect_combo)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["12", "24", "30", "60"])
        form_layout.addRow("FPS:", self.fps_combo)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        form_layout.addRow("Description:", self.desc_edit)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._on_save)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def _populate_data(self):
        self.name_edit.setText(self.model.name)
        self.author_edit.setText(self.model.author)
        self.company_edit.setText(self.model.company)
        self.copyright_edit.setText(self.model.copyright)
        self.desc_edit.setText(self.model.description)

        self.lang_combo.setCurrentText(self.model.language)
        self.art_combo.setCurrentText(self.model.art_style)
        self.aspect_combo.setCurrentText(self.model.aspect_ratio)

        fps_index = self.fps_combo.findText(str(self.model.fps))
        if fps_index >= 0:
            self.fps_combo.setCurrentIndex(fps_index)

        res_str = f"{self.model.resolution[0]}x{self.model.resolution[1]}"
        for i in range(self.resolution_combo.count()):
            if self.resolution_combo.itemText(i).startswith(res_str):
                self.resolution_combo.setCurrentIndex(i)
                break

    def _on_save(self):
        self.model.name = self.name_edit.text()
        self.model.author = self.author_edit.text()
        self.model.company = self.company_edit.text()
        self.model.copyright = self.copyright_edit.text()
        self.model.description = self.desc_edit.toPlainText()
        self.model.fps = int(self.fps_combo.currentText())
        self.model.language = self.lang_combo.currentText()
        self.model.art_style = self.art_combo.currentText()
        self.model.aspect_ratio = self.aspect_combo.currentText()

        res_text = self.resolution_combo.currentText().split(" ")[0]
        w, h = res_text.split("x")
        self.model.resolution = (int(w), int(h))

        self.accept()
