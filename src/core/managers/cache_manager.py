"""
Cache Manager - Implements LRU logic to prevent memory overflow.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, max_items: int = 1000):
        self.max_items = max_items
        self._cache: dict[str, Any] = {}
        self._access_order: list[str] = []

    def set(self, key: str, value: Any):
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_items:
            # Evict least recently used (first item)
            evicted_key = self._access_order.pop(0)
            del self._cache[evicted_key]
            logger.debug(f"Cache evicted: {evicted_key}")

        self._cache[key] = value
        self._access_order.append(key)

    def get(self, key: str) -> Any:
        if key in self._cache:
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def clear(self):
        self._cache.clear()
        self._access_order.clear()
        logger.info("Cache forcefully cleared.")

    def get_size_mock_mb(self) -> float:
        # For UI demonstration
        return len(self._cache) * 0.15  # Assume avg 150kb per cached item
