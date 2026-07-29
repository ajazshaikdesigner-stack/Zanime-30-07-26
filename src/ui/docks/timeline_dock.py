"""
Timeline Framework Dock
"""
from src.core.sdk.base_dock import BaseDock
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QSlider, 
                              QTreeWidget, QTreeWidgetItem, QSplitter, QWidget, QLabel)
from PySide6.QtCore import Qt

class TimelineDock(BaseDock):
    def __init__(self, parent=None):
        super().__init__("Timeline", parent)
        
        layout = QVBoxLayout(self.container)
        
        # Playback Controls
        playback_layout = QHBoxLayout()
        playback_layout.addWidget(QPushButton("⏮"))
        playback_layout.addWidget(QPushButton("⏴"))
        playback_layout.addWidget(QPushButton("⏸"))
        playback_layout.addWidget(QPushButton("⏵"))
        playback_layout.addWidget(QPushButton("⏭"))
        playback_layout.addStretch()
        
        zoom_slider = QSlider(Qt.Horizontal)
        zoom_slider.setFixedWidth(100)
        playback_layout.addWidget(QLabel("Zoom:"))
        playback_layout.addWidget(zoom_slider)
        
        layout.addLayout(playback_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Layers Tree
        self.layers_tree = QTreeWidget()
        self.layers_tree.setHeaderLabels(["Layer Name"])
        QTreeWidgetItem(self.layers_tree, ["Audio Track"])
        QTreeWidgetItem(self.layers_tree, ["Character Layer"])
        QTreeWidgetItem(self.layers_tree, ["Background Layer"])
        splitter.addWidget(self.layers_tree)
        
        # Timeline Ruler & Tracks (Mock)
        tracks_widget = QWidget()
        tracks_widget.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333;")
        tracks_layout = QVBoxLayout(tracks_widget)
        tracks_layout.addWidget(QLabel("Ruler: 0s  1s  2s  3s  4s"))
        tracks_layout.addStretch()
        splitter.addWidget(tracks_widget)
        
        layout.addWidget(splitter)
