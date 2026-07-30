"""
Cache Manager - Implements LRU logic using OrderedDict to prevent memory overflow.
"""

import logging
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, max_items: int = 1000):
        self.max_items = max_items
        # OrderedDict gives O(1) move-to-end for LRU tracking
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def set(self, key: str, value: Any):
        if key in self._cache:
            # Refresh position: move to end (most recently used)
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.max_items:
                # Evict least recently used (first item)
                evicted_key, _ = self._cache.popitem(last=False)
                logger.debug("Cache evicted: %s", evicted_key)
        self._cache[key] = value

    def get(self, key: str) -> Any:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def clear(self):
        self._cache.clear()
        logger.info("Cache forcefully cleared.")

    def get_size_mock_mb(self) -> float:
        # For UI demonstration
        return len(self._cache) * 0.15  # Assume avg 150kb per cached item
