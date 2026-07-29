# Caching System

The `CacheManager` prevents the application from consuming all 16GB of RAM.

## LRU Algorithm
It implements a Least Recently Used (LRU) algorithm. Every time a thumbnail or project file is loaded, it is placed in the cache and its "access order" is updated. 

If the Cache hits its `max_items` threshold (defined by the active `PerformanceMode`), the `CacheManager` will automatically evict the oldest, untouched data from memory.

Users can manually forcefully clear the cache from the Performance Dashboard.
