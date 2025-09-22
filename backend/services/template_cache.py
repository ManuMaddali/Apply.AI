"""
Template Cache Service

A comprehensive caching service for template previews with LRU eviction,
TTL expiration, and template-specific invalidation capabilities.
"""

import asyncio
import hashlib
import logging
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List, Tuple
from dataclasses import dataclass
from threading import RLock
import weakref

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Union[str, bytes, Dict[str, Any]]
    created_at: datetime
    expires_at: datetime
    template_id: str
    format_type: str
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0

    def __post_init__(self):
        """Calculate size after initialization"""
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        
        # Estimate size in bytes
        if isinstance(self.data, str):
            self.size_bytes = len(self.data.encode('utf-8'))
        elif isinstance(self.data, bytes):
            self.size_bytes = len(self.data)
        elif isinstance(self.data, dict):
            # Rough estimate for dict size
            self.size_bytes = len(str(self.data).encode('utf-8'))
        else:
            self.size_bytes = 1024  # Default estimate

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() > self.expires_at

    def access(self) -> None:
        """Mark entry as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class TemplateCacheService:
    """
    Advanced caching service for template previews with LRU eviction,
    TTL expiration, and template-specific cache invalidation.
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl_hours: int = 1,
        max_memory_mb: int = 100,
        cleanup_interval_seconds: int = 300  # 5 minutes
    ):
        """
        Initialize the template cache service
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl_hours: Default TTL for cache entries in hours
            max_memory_mb: Maximum memory usage in MB
            cleanup_interval_seconds: How often to run cleanup tasks
        """
        self.max_size = max_size
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cleanup_interval = cleanup_interval_seconds
        
        # Thread-safe cache storage using OrderedDict for LRU
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = RLock()
        
        # Template ID to cache keys mapping for invalidation
        self._template_keys: Dict[str, set] = {}
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'invalidations': 0,
            'total_size_bytes': 0,
            'created_at': datetime.now()
        }
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown = False
        
        # Weak reference to instances for cleanup
        self._instances = weakref.WeakSet()
        self._instances.add(self)
        
        logger.info(f"TemplateCacheService initialized: max_size={max_size}, ttl={default_ttl_hours}h, max_memory={max_memory_mb}MB")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_background_cleanup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()

    def _generate_cache_key(
        self,
        template_id: str,
        format_type: str = "html",
        data_hash: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a unique cache key
        
        Args:
            template_id: Template identifier
            format_type: Preview format (html, png, json)
            data_hash: Hash of custom data (optional)
            **kwargs: Additional parameters for key generation
            
        Returns:
            Unique cache key string
        """
        key_parts = [template_id, format_type]
        
        if data_hash:
            key_parts.append(data_hash)
        
        # Add any additional parameters
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _calculate_data_hash(self, data: Any) -> str:
        """Calculate hash for data to use in cache key"""
        if data is None:
            return "none"
        
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            import json
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()[:8]

    def _evict_lru(self) -> None:
        """Evict least recently used entries"""
        with self._lock:
            while len(self._cache) >= self.max_size:
                # Remove oldest entry (LRU)
                key, entry = self._cache.popitem(last=False)
                self._remove_from_template_mapping(entry.template_id, key)
                self._stats['total_size_bytes'] -= entry.size_bytes
                self._stats['evictions'] += 1
                logger.debug(f"Evicted LRU cache entry: {key}")

    def _evict_by_memory(self) -> None:
        """Evict entries to stay under memory limit"""
        with self._lock:
            while self._stats['total_size_bytes'] > self.max_memory_bytes and self._cache:
                # Remove oldest entry
                key, entry = self._cache.popitem(last=False)
                self._remove_from_template_mapping(entry.template_id, key)
                self._stats['total_size_bytes'] -= entry.size_bytes
                self._stats['evictions'] += 1
                logger.debug(f"Evicted cache entry for memory: {key} ({entry.size_bytes} bytes)")

    def _cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries"""
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            self._remove_entry(key)
            self._stats['expirations'] += 1
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)

    def _add_to_template_mapping(self, template_id: str, cache_key: str) -> None:
        """Add cache key to template mapping"""
        if template_id not in self._template_keys:
            self._template_keys[template_id] = set()
        self._template_keys[template_id].add(cache_key)

    def _remove_from_template_mapping(self, template_id: str, cache_key: str) -> None:
        """Remove cache key from template mapping"""
        if template_id in self._template_keys:
            self._template_keys[template_id].discard(cache_key)
            if not self._template_keys[template_id]:
                del self._template_keys[template_id]

    def _remove_entry(self, key: str) -> bool:
        """Remove a cache entry by key"""
        with self._lock:
            entry = self._cache.pop(key, None)
            if entry:
                self._remove_from_template_mapping(entry.template_id, key)
                self._stats['total_size_bytes'] -= entry.size_bytes
                return True
            return False

    def put(
        self,
        template_id: str,
        data: Union[str, bytes, Dict[str, Any]],
        format_type: str = "html",
        custom_data: Any = None,
        ttl_hours: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Store data in cache
        
        Args:
            template_id: Template identifier
            data: Data to cache
            format_type: Type of data (html, png, json)
            custom_data: Custom data used for key generation
            ttl_hours: Custom TTL in hours (uses default if None)
            **kwargs: Additional parameters for cache key
            
        Returns:
            Cache key for the stored data
        """
        # Generate cache key
        data_hash = self._calculate_data_hash(custom_data) if custom_data else None
        cache_key = self._generate_cache_key(template_id, format_type, data_hash, **kwargs)
        
        # Calculate expiration time
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.default_ttl
        expires_at = datetime.now() + ttl
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            data=data,
            created_at=datetime.now(),
            expires_at=expires_at,
            template_id=template_id,
            format_type=format_type
        )
        
        with self._lock:
            # Remove existing entry if present
            if cache_key in self._cache:
                old_entry = self._cache[cache_key]
                self._stats['total_size_bytes'] -= old_entry.size_bytes
            
            # Check if we need to evict entries
            self._evict_lru()
            self._evict_by_memory()
            
            # Store new entry
            self._cache[cache_key] = entry
            self._cache.move_to_end(cache_key)  # Mark as most recently used
            
            # Update mappings and stats
            self._add_to_template_mapping(template_id, cache_key)
            self._stats['total_size_bytes'] += entry.size_bytes
        
        logger.debug(f"Cached {format_type} for template {template_id}: {cache_key}")
        return cache_key

    def get(
        self,
        template_id: str,
        format_type: str = "html",
        custom_data: Any = None,
        **kwargs
    ) -> Optional[Union[str, bytes, Dict[str, Any]]]:
        """
        Retrieve data from cache
        
        Args:
            template_id: Template identifier
            format_type: Type of data to retrieve
            custom_data: Custom data used for key generation
            **kwargs: Additional parameters for cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        # Generate cache key
        data_hash = self._calculate_data_hash(custom_data) if custom_data else None
        cache_key = self._generate_cache_key(template_id, format_type, data_hash, **kwargs)
        
        with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            # Check if expired
            if entry.is_expired():
                self._remove_entry(cache_key)
                self._stats['misses'] += 1
                self._stats['expirations'] += 1
                return None
            
            # Update access info and move to end (most recently used)
            entry.access()
            self._cache.move_to_end(cache_key)
            self._stats['hits'] += 1
            
            logger.debug(f"Cache hit for template {template_id}: {cache_key}")
            return entry.data

    def invalidate_template(self, template_id: str) -> int:
        """
        Invalidate all cache entries for a specific template
        
        Args:
            template_id: Template identifier to invalidate
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_remove = list(self._template_keys.get(template_id, set()))
            
            for key in keys_to_remove:
                self._remove_entry(key)
            
            if keys_to_remove:
                self._stats['invalidations'] += len(keys_to_remove)
                logger.info(f"Invalidated {len(keys_to_remove)} cache entries for template {template_id}")
            
            return len(keys_to_remove)

    def invalidate_format(self, format_type: str) -> int:
        """
        Invalidate all cache entries of a specific format
        
        Args:
            format_type: Format type to invalidate
            
        Returns:
            Number of entries invalidated
        """
        keys_to_remove = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.format_type == format_type:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove_entry(key)
            
            if keys_to_remove:
                self._stats['invalidations'] += len(keys_to_remove)
                logger.info(f"Invalidated {len(keys_to_remove)} cache entries for format {format_type}")
            
            return len(keys_to_remove)

    def clear(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._template_keys.clear()
            self._stats['total_size_bytes'] = 0
            self._stats['invalidations'] += count
        
        logger.info(f"Cleared all cache entries: {count}")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = (
                self._stats['hits'] / (self._stats['hits'] + self._stats['misses'])
                if (self._stats['hits'] + self._stats['misses']) > 0
                else 0.0
            )
            
            return {
                'cache_size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_bytes': self._stats['total_size_bytes'],
                'memory_usage_mb': round(self._stats['total_size_bytes'] / (1024 * 1024), 2),
                'max_memory_mb': self.max_memory_bytes // (1024 * 1024),
                'hit_rate': round(hit_rate, 3),
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'expirations': self._stats['expirations'],
                'invalidations': self._stats['invalidations'],
                'template_count': len(self._template_keys),
                'default_ttl_hours': self.default_ttl.total_seconds() / 3600,
                'uptime_seconds': (datetime.now() - self._stats['created_at']).total_seconds()
            }

    def get_template_stats(self, template_id: str) -> Dict[str, Any]:
        """Get statistics for a specific template"""
        with self._lock:
            template_keys = self._template_keys.get(template_id, set())
            template_entries = [
                self._cache[key] for key in template_keys 
                if key in self._cache
            ]
            
            total_size = sum(entry.size_bytes for entry in template_entries)
            total_accesses = sum(entry.access_count for entry in template_entries)
            
            format_breakdown = {}
            for entry in template_entries:
                if entry.format_type not in format_breakdown:
                    format_breakdown[entry.format_type] = 0
                format_breakdown[entry.format_type] += 1
            
            return {
                'template_id': template_id,
                'cache_entries': len(template_entries),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_accesses': total_accesses,
                'format_breakdown': format_breakdown,
                'oldest_entry': min(
                    (entry.created_at for entry in template_entries),
                    default=None
                ),
                'newest_entry': max(
                    (entry.created_at for entry in template_entries),
                    default=None
                )
            }

    async def start_background_cleanup(self) -> None:
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._shutdown = False
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
            logger.info("Started background cache cleanup task")

    async def _background_cleanup(self) -> None:
        """Background task for cache maintenance"""
        while not self._shutdown:
            try:
                # Clean up expired entries
                expired_count = self._cleanup_expired()
                
                # Log stats periodically
                stats = self.get_stats()
                if expired_count > 0 or stats['cache_size'] > 0:
                    logger.debug(
                        f"Cache stats: size={stats['cache_size']}, "
                        f"memory={stats['memory_usage_mb']}MB, "
                        f"hit_rate={stats['hit_rate']}, "
                        f"expired={expired_count}"
                    )
                
                # Wait before next cleanup
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {e}")
                await asyncio.sleep(self.cleanup_interval)

    async def shutdown(self) -> None:
        """Shutdown the cache service"""
        self._shutdown = True
        
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("TemplateCacheService shutdown complete")


# Global cache instance
_global_cache: Optional[TemplateCacheService] = None


def get_template_cache() -> TemplateCacheService:
    """Get or create global template cache instance"""
    global _global_cache
    
    if _global_cache is None:
        _global_cache = TemplateCacheService()
        
        # Start background cleanup if in async context
        try:
            loop = asyncio.get_running_loop()
            if loop and not loop.is_closed():
                asyncio.create_task(_global_cache.start_background_cleanup())
        except RuntimeError:
            # Not in async context, cleanup will be started when needed
            pass
    
    return _global_cache


async def shutdown_global_cache() -> None:
    """Shutdown global cache instance"""
    global _global_cache
    
    if _global_cache:
        await _global_cache.shutdown()
        _global_cache = None




