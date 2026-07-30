"""
Character Properties Dock - Tabbed interface for DNA, Outfits, Accessories.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.sdk.base_dock import BaseDock


class CharacterPropertiesDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Character Properties", parent)

        layout = QVBoxLayout(self.container)

        self.tabs = QTabWidget()
        self._setup_dna_tab()
        self._setup_outfit_tab()
        self._setup_accessories_tab()

        layout.addWidget(self.tabs)

        self.generate_btn = QPushButton("Generate with AI")
        layout.addWidget(self.generate_btn)

    def _setup_dna_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.dna_name = QLineEdit()
        form.addRow("Name:", self.dna_name)

        self.dna_age = QSpinBox()
        self.dna_age.setRange(0, 999)
        form.addRow("Age:", self.dna_age)

        self.dna_gender = QComboBox()
        self.dna_gender.addItems(["Male", "Female", "Non-binary", "Other", "Unknown"])
        form.addRow("Gender:", self.dna_gender)

        self.dna_hair = QComboBox()
        self.dna_hair.addItems(["Short", "Long", "Bald", "Curly", "Straight", "Spiky"])
        form.addRow("Hair Style:", self.dna_hair)

        self.dna_bio = QTextEdit()
        self.dna_bio.setMaximumHeight(80)
        form.addRow("Biography:", self.dna_bio)

        self.tabs.addTab(tab, "DNA")

    def _setup_outfit_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.outfit_list = QListWidget()
        layout.addWidget(self.outfit_list)

        btn_layout = QHBoxLayout()
        self.add_outfit_btn = QPushButton("Add")
        self.del_outfit_btn = QPushButton("Remove")
        btn_layout.addWidget(self.add_outfit_btn)
        btn_layout.addWidget(self.del_outfit_btn)
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, "Outfits")

    def _setup_accessories_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.acc_list = QListWidget()
        layout.addWidget(self.acc_list)

        btn_layout = QHBoxLayout()
        self.add_acc_btn = QPushButton("Add")
        self.del_acc_btn = QPushButton("Remove")
        btn_layout.addWidget(self.add_acc_btn)
        btn_layout.addWidget(self.del_acc_btn)
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, "Accessories")
