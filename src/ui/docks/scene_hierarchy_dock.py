"""
Scene Hierarchy Dock
Displays Movie -> Scene -> Shot -> Layers -> Objects
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import QVBoxLayout, QTreeWidget, QTreeWidgetItem

class SceneHierarchyDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Hierarchy", parent)
        
        layout = QVBoxLayout(self.container)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Movie Structure"])
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        
        layout.addWidget(self.tree)
        
    def populate(self, movie_scenes):
        self.tree.clear()
        movie_node = QTreeWidgetItem(["Movie Root"])
        
        for scene in movie_scenes:
            scene_node = QTreeWidgetItem([scene.name])
            scene_node.setData(0, 99, ("scene", scene.uuid))
            
            for shot in scene.shots:
                shot_node = QTreeWidgetItem([shot.name])
                shot_node.setData(0, 99, ("shot", shot.uuid))
                
                # Mock layer folders
                char_layer = QTreeWidgetItem(["Layer: Characters"])
                for obj in shot.objects:
                    obj_node = QTreeWidgetItem([obj.name])
                    obj_node.setData(0, 99, ("object", obj.uuid))
                    char_layer.addChild(obj_node)
                    
                shot_node.addChild(char_layer)
                scene_node.addChild(shot_node)
                
            movie_node.addChild(scene_node)
            
        self.tree.addTopLevelItem(movie_node)
        self.tree.expandAll()
