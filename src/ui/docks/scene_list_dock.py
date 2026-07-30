"""
Scene List Dock - Tree view for Scenes and their nested Shots.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from src.core.sdk.base_dock import BaseDock


class SceneListDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Scene List", parent)

        layout = QVBoxLayout(self.container)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Timeline"])
        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        self.add_scene_btn = QPushButton("+ Scene")
        self.add_shot_btn = QPushButton("+ Shot")
        btn_layout.addWidget(self.add_scene_btn)
        btn_layout.addWidget(self.add_shot_btn)

        layout.addLayout(btn_layout)

    def populate(self, storyboard_model):
        self.tree.clear()
        for i, scene in enumerate(storyboard_model.scenes):
            scene_item = QTreeWidgetItem([f"Scene {i+1}: {scene.name}"])
            scene_item.setData(0, 99, ("scene", scene.uuid))

            for j, shot in enumerate(scene.shots):
                shot_item = QTreeWidgetItem([f"Shot {j+1} [{shot.shot_type}]"])
                shot_item.setData(0, 99, ("shot", shot.uuid))
                scene_item.addChild(shot_item)

            self.tree.addTopLevelItem(scene_item)
        self.tree.expandAll()
