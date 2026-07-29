import pytest
from src.core.managers.cache_manager import CacheManager
from src.core.managers.performance_manager import PerformanceManager
from src.models.performance_model import PerformanceMode

def test_cache_manager():
    cache = CacheManager(max_items=3)
    cache.set("A", 1)
    cache.set("B", 2)
    cache.set("C", 3)
    
    assert cache.get("A") == 1
    assert len(cache._cache) == 3
    
    # Trigger eviction (A was just accessed, so B is now least recently used)
    cache.set("D", 4)
    assert cache.get("B") is None
    assert cache.get("A") == 1
    assert cache.get("D") == 4

def test_performance_manager():
    manager = PerformanceManager()
    assert manager.mode == PerformanceMode.BALANCED
    
    manager.set_mode(PerformanceMode.BATTERY_SAVER)
    assert manager.cache.max_items == 500
