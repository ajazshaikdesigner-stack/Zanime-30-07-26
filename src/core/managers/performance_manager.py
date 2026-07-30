"""
Performance Manager - Background monitoring.
"""

import logging
import random
import time

from PySide6.QtCore import QObject, QThread, Signal

from src.core.managers.cache_manager import CacheManager
from src.models.performance_model import PerformanceMode, SystemMetrics

logger = logging.getLogger(__name__)


class ResourceMonitor(QThread):
    metrics_updated = Signal(SystemMetrics)

    def __init__(self, cache_manager: CacheManager, parent=None):
        super().__init__(parent)
        self.cache_manager = cache_manager
        self.running = True

    def run(self):
        while self.running:
            # In production, use psutil for real hardware stats.
            # Here we mock the behavior to fit the target AMD hardware constraints.
            m = SystemMetrics(
                cpu_usage=random.uniform(5.0, 35.0),
                ram_usage=random.uniform(40.0, 60.0),  # Assuming 16GB
                vram_usage=random.uniform(20.0, 80.0),  # Assuming 4GB RX6500M
                gpu_usage=random.uniform(10.0, 90.0),
                cache_size_mb=self.cache_manager.get_size_mock_mb(),
            )
            try:
                self.metrics_updated.emit(m)
            except RuntimeError:
                logger.debug(
                    "ResourceMonitor: Signal source deleted while emitting metrics"
                )
            time.sleep(2.0)

    def stop(self):
        self.running = False
        self.wait()


class PerformanceManager(QObject):
    def __init__(self):
        super().__init__()
        self.cache = CacheManager(max_items=5000)
        self.monitor = ResourceMonitor(self.cache)
        self.mode = PerformanceMode.BALANCED

    def start_monitoring(self):
        self.monitor.start()

    def stop_monitoring(self):
        self.monitor.stop()

    def set_mode(self, mode: PerformanceMode):
        self.mode = mode
        logger.info(f"Performance Mode set to: {self.mode.name}")

        # Adjust constraints dynamically
        if self.mode == PerformanceMode.PERFORMANCE:
            self.cache.max_items = 10000
        elif self.mode == PerformanceMode.BATTERY_SAVER:
            self.cache.max_items = 500
        else:
            self.cache.max_items = 5000
