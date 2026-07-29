"""
Data Models for Performance Optimization & Stability.
"""
from dataclasses import dataclass
from enum import Enum

class PerformanceMode(Enum):
    BATTERY_SAVER = 1
    BALANCED = 2
    QUALITY = 3
    PERFORMANCE = 4

@dataclass
class SystemMetrics:
    cpu_usage: float = 0.0 # Percentage 0-100
    ram_usage: float = 0.0 # Percentage 0-100
    vram_usage: float = 0.0 # Percentage 0-100
    gpu_usage: float = 0.0 # Percentage 0-100
    cache_size_mb: float = 0.0
