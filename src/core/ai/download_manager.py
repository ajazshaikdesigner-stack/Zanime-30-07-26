"""
Download Manager for fetching heavy tensor files.
"""
import logging
import uuid
from typing import Dict
from PySide6.QtCore import QObject, QTimer, Signal

logger = logging.getLogger(__name__)

class DownloadManager(QObject):
    progress_updated = Signal(str, int) # download_id, percentage
    completed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.active_downloads: Dict[str, QTimer] = {}
        self.progress_map: Dict[str, int] = {}
        
    def download_model(self, model_url: str, dest_path: str) -> str:
        """Starts a mock download and returns a download_id."""
        logger.info(f"DownloadManager: Queued {model_url} -> {dest_path}")
        dl_id = str(uuid.uuid4())
        self.progress_map[dl_id] = 0
        
        # Mock download progress using a QTimer
        timer = QTimer(self)
        timer.timeout.connect(lambda: self._simulate_progress(dl_id))
        timer.start(500)
        self.active_downloads[dl_id] = timer
        return dl_id
        
    def _simulate_progress(self, dl_id: str):
        if dl_id in self.progress_map:
            self.progress_map[dl_id] += 20
            self.progress_updated.emit(dl_id, self.progress_map[dl_id])
            if self.progress_map[dl_id] >= 100:
                self.active_downloads[dl_id].stop()
                del self.active_downloads[dl_id]
                self.completed.emit(dl_id)
                logger.info(f"DownloadManager: Completed {dl_id}")
                
    def pause(self, dl_id: str):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id].stop()
            
    def resume(self, dl_id: str):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id].start()
            
    def verify_checksum(self, file_path: str, expected_hash: str) -> bool:
        logger.info(f"DownloadManager: Verifying checksum for {file_path}")
        return True # Mock success
