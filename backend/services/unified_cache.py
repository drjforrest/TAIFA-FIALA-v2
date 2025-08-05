"""
Unified Cache Service
====================

Comprehensive caching layer for all API services including:
- Positive result caching (successful responses)
- Negative result caching (null/failed responses)  
- Intelligent cache warming
- Cache invalidation strategies
- Multi-tier caching (memory + Redis)
"""

import asyncio
import json
import hashlib
import pickle
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import time

import redis.asyncio as aioredis
from loguru import logger
from cachetools import TTLCache

from config.settings import settings
from services.null_result_cache import DataSource, CacheReason


class CacheType(Enum):
    """Types of cache entries"""
    POSITIVE = "positive"  # Successful API responses
    NEGATIVE = "negative"  # Failed/null responses
    METADATA = "metadata"  # Cache metadata and stats


class CompressionLevel(Enum):
    """Compression levels for cached data"""
    NONE = 0
    LIGHT = 1  # JSON compression
    MEDIUM = 6  # gzip compression
    HEAVY = 9  # maximum gzip compression


@dataclass
class CacheEntry:
    """Unified cache entry structure"""
    key: str
    data_source: DataSource
    cache_type: CacheType
    content: Any
    content_hash: str
    cached_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    compression_level: CompressionLevel = CompressionLevel.NONE
    metadata: Dict[str, Any] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() >= self.expires_at
    
    def is_stale(self, stale_threshold_minutes: int = 60) -> bool:
        """Check if cache entry is stale but not expired"""
        stale_time = datetime.now() - timedelta(minutes=stale_threshold_minutes)
        return self.cached_at <= stale_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['data_source'] = self.data_source.value
        data['cache_type'] = self.cache_type.value
        data['compression_level'] = self.compression_level.value
        data['cached_at'] = self.cached_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(
            key=data['key'],
            data_source=DataSource(data['data_source']),
            cache_type=CacheType(data['cache_type']),
            content=data['content'],
            content_hash=data['content_hash'],
            cached_at=datetime.fromisoformat(data['cached_at']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            access_count=data.get('access_count', 0),
            last_accessed=datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None,
            compression_level=CompressionLevel(data.get('compression_level', 0)),
            metadata=data.get('metadata', {})
        )


class UnifiedCacheService:
    """Comprehensive caching service with multi-tier architecture"""
    
    def __init__(self, redis_url: Optional[str] = None):
        # Build Redis URL with password if provided
        if redis_url:
            self.redis_url = redis_url
        else:
            base_url = settings.REDIS_URL or "redis://localhost:6379"
            redis_password = getattr(settings, 'REDIS_PASSWORD', None)
            
            if redis_password:
                # Parse the URL and add password
                if "://" in base_url:
                    protocol, rest = base_url.split("://", 1)
                    if "@" in rest:
                        # Password already in URL
                        self.redis_url = base_url
                    else:
                        # Add password to URL
                        self.redis_url = f"{protocol}://default:{redis_password}@{rest}"
                else:
                    self.redis_url = base_url
            else:
                self.redis_url = base_url
        
        self.redis: Optional[aioredis.Redis] = None
        
        # Memory cache (L1) - for frequently accessed small items
        self.memory_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes
        
        # Cache prefixes
        self.cache_prefix = "unified_cache:"
        self.lock_prefix = "cache_lock:"
        
        # Cache TTL settings by data source and result type (in hours)
        self.ttl_settings = {
            # Positive results - cache successful responses longer
            (DataSource.PERPLEXITY, CacheType.POSITIVE): 24,
            (DataSource.SERPER, CacheType.POSITIVE): 12,
            (DataSource.WEB_SCRAPING, CacheType.POSITIVE): 6,
            (DataSource.GITHUB_API, CacheType.POSITIVE): 4,
            (DataSource.ARXIV_API, CacheType.POSITIVE): 48,  # Research papers change rarely
            (DataSource.PUBMED_API, CacheType.POSITIVE): 48,
            (DataSource.COMPANY_WEBSITE, CacheType.POSITIVE): 24,
            (DataSource.CITATION_EXTRACTION, CacheType.POSITIVE): 12,
            
            # Negative results - shorter cache times for retries
            (DataSource.PERPLEXITY, CacheType.NEGATIVE): 4,
            (DataSource.SERPER, CacheType.NEGATIVE): 2,
            (DataSource.WEB_SCRAPING, CacheType.NEGATIVE): 6,
            (DataSource.GITHUB_API, CacheType.NEGATIVE): 1,
            (DataSource.ARXIV_API, CacheType.NEGATIVE): 8,
            (DataSource.PUBMED_API, CacheType.NEGATIVE): 8,
            (DataSource.COMPANY_WEBSITE, CacheType.NEGATIVE): 12,
            (DataSource.CITATION_EXTRACTION, CacheType.NEGATIVE): 3,
        }
        
        # Compression thresholds (bytes)
        self.compression_thresholds = {
            CompressionLevel.NONE: 0,
            CompressionLevel.LIGHT: 1024,      # 1KB
            CompressionLevel.MEDIUM: 10240,    # 10KB
            CompressionLevel.HEAVY: 102400     # 100KB
        }
        
        # Stats tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'memory_hits': 0,
            'redis_hits': 0,
            'compressions': 0,
            'decompressions': 0
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.redis = await aioredis.from_url(
            self.redis_url, 
            decode_responses=False,  # Handle binary data for compression
            socket_keepalive=True,
            socket_keepalive_options={}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.redis:
            await self.redis.close()

    def _generate_cache_key(self, data_source: DataSource, cache_type: CacheType, 
                           query_params: Dict[str, Any]) -> str:
        """Generate consistent cache key"""
        
        # Normalize parameters
        normalized_params = self._normalize_params(query_params)
        
        # Create hash
        param_string = json.dumps(normalized_params, sort_keys=True)
        param_hash = hashlib.sha256(param_string.encode()).hexdigest()[:16]
        
        return f"{self.cache_prefix}{data_source.value}:{cache_type.value}:{param_hash}"

    def _normalize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parameters for consistent hashing"""
        normalized = {}
        
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                normalized[key] = sorted(str(v) for v in value)
            elif isinstance(value, dict):
                normalized[key] = json.dumps(value, sort_keys=True)
            elif isinstance(value, str):
                # Normalize whitespace and case for text queries
                if key in ['query', 'search_term', 'content']:
                    normalized[key] = ' '.join(value.lower().split())
                else:
                    normalized[key] = value
            else:
                normalized[key] = str(value)
        
        return normalized

    def _calculate_content_hash(self, content: Any) -> str:
        """Calculate hash of content for deduplication"""
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        return hashlib.md5(content_str.encode()).hexdigest()

    def _compress_content(self, content: Any) -> Tuple[bytes, CompressionLevel]:
        """Compress content based on size"""
        
        # Serialize content
        if isinstance(content, (dict, list)):
            serialized = json.dumps(content).encode('utf-8')
        else:
            serialized = str(content).encode('utf-8')
        
        content_size = len(serialized)
        
        # Determine compression level
        if content_size >= self.compression_thresholds[CompressionLevel.HEAVY]:
            compressed = gzip.compress(serialized, compresslevel=9)
            compression_level = CompressionLevel.HEAVY
        elif content_size >= self.compression_thresholds[CompressionLevel.MEDIUM]:
            compressed = gzip.compress(serialized, compresslevel=6)
            compression_level = CompressionLevel.MEDIUM
        elif content_size >= self.compression_thresholds[CompressionLevel.LIGHT]:
            compressed = gzip.compress(serialized, compresslevel=1)
            compression_level = CompressionLevel.LIGHT
        else:
            compressed = serialized
            compression_level = CompressionLevel.NONE
        
        if compression_level != CompressionLevel.NONE:
            self.stats['compressions'] += 1
            logger.debug(f"Compressed {content_size} bytes to {len(compressed)} bytes ({compression_level.value})")
        
        return compressed, compression_level

    def _decompress_content(self, compressed_data: bytes, compression_level: CompressionLevel) -> Any:
        """Decompress content"""
        
        if compression_level == CompressionLevel.NONE:
            content_str = compressed_data.decode('utf-8')
        else:
            decompressed = gzip.decompress(compressed_data)
            content_str = decompressed.decode('utf-8')
            self.stats['decompressions'] += 1
        
        # Try to parse as JSON, fallback to string
        try:
            return json.loads(content_str)
        except json.JSONDecodeError:
            return content_str

    async def get(self, data_source: DataSource, query_params: Dict[str, Any], 
                 cache_type: CacheType = CacheType.POSITIVE) -> Optional[Any]:
        """Get cached result"""
        
        cache_key = self._generate_cache_key(data_source, cache_type, query_params)
        
        # Try memory cache first (L1)
        if cache_key in self.memory_cache:
            self.stats['memory_hits'] += 1
            self.stats['hits'] += 1
            return self.memory_cache[cache_key]
        
        # Try Redis cache (L2)
        try:
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                # Deserialize cache entry
                entry_dict = pickle.loads(cached_data)
                entry = CacheEntry.from_dict(entry_dict)
                
                # Check if expired
                if entry.is_expired():
                    await self.redis.delete(cache_key)
                    self.stats['misses'] += 1
                    return None
                
                # Decompress content
                if isinstance(entry.content, bytes):
                    content = self._decompress_content(entry.content, entry.compression_level)
                else:
                    content = entry.content
                
                # Update access stats
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Store updated entry back
                await self.redis.setex(
                    cache_key,
                    int((entry.expires_at - datetime.now()).total_seconds()),
                    pickle.dumps(entry.to_dict())
                )
                
                # Add to memory cache if small enough
                if len(str(content)) < 10240:  # 10KB limit for memory cache
                    self.memory_cache[cache_key] = content
                
                self.stats['redis_hits'] += 1
                self.stats['hits'] += 1
                return content
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            self.stats['misses'] += 1
            return None

    async def set(self, data_source: DataSource, query_params: Dict[str, Any], 
                 content: Any, cache_type: CacheType = CacheType.POSITIVE,
                 custom_ttl_hours: Optional[float] = None) -> bool:
        """Set cached result"""
        
        cache_key = self._generate_cache_key(data_source, cache_type, query_params)
        
        # Calculate TTL
        if custom_ttl_hours:
            ttl_hours = custom_ttl_hours
        else:
            ttl_hours = self.ttl_settings.get((data_source, cache_type), 24)
        
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        # Compress content
        compressed_content, compression_level = self._compress_content(content)
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            data_source=data_source,
            cache_type=cache_type,
            content=compressed_content,
            content_hash=self._calculate_content_hash(content),
            cached_at=datetime.now(),
            expires_at=expires_at,
            compression_level=compression_level,
            metadata={
                'original_size': len(str(content)),
                'compressed_size': len(compressed_content),
                'query_params_hash': hashlib.md5(json.dumps(query_params, sort_keys=True).encode()).hexdigest()
            }
        )
        
        try:
            # Store in Redis
            ttl_seconds = int(ttl_hours * 3600)
            await self.redis.setex(
                cache_key,
                ttl_seconds,
                pickle.dumps(entry.to_dict())
            )
            
            # Add to memory cache if small enough
            if len(str(content)) < 10240:  # 10KB limit
                self.memory_cache[cache_key] = content
            
            self.stats['sets'] += 1
            logger.debug(f"Cached {data_source.value} {cache_type.value} result for {ttl_hours}h")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, data_source: DataSource, query_params: Dict[str, Any],
                    cache_type: CacheType = CacheType.POSITIVE) -> bool:
        """Delete cached result"""
        
        cache_key = self._generate_cache_key(data_source, cache_type, query_params)
        
        try:
            # Remove from Redis
            deleted_count = await self.redis.delete(cache_key)
            
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            if deleted_count > 0:
                self.stats['deletes'] += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        
        try:
            keys = await self.redis.keys(f"{self.cache_prefix}{pattern}")
            
            if keys:
                deleted_count = await self.redis.delete(*keys)
                
                # Clear matching keys from memory cache
                memory_keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in memory_keys_to_delete:
                    del self.memory_cache[key]
                
                self.stats['deletes'] += deleted_count
                logger.info(f"Invalidated {deleted_count} cache entries matching pattern: {pattern}")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        
        try:
            # Get Redis info
            redis_info = await self.redis.info('memory')
            
            # Get cache keys by type
            all_keys = await self.redis.keys(f"{self.cache_prefix}*")
            
            stats = {
                'memory_cache': {
                    'size': len(self.memory_cache),
                    'max_size': self.memory_cache.maxsize,
                    'ttl': self.memory_cache.ttl
                },
                'redis_cache': {
                    'total_keys': len(all_keys),
                    'memory_usage_bytes': redis_info.get('used_memory', 0),
                    'memory_usage_human': redis_info.get('used_memory_human', '0B')
                },
                'performance': self.stats.copy(),
                'hit_rate': self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0,
                'by_data_source': {},
                'by_cache_type': {},
                'compression_stats': {
                    'compressions': self.stats['compressions'],
                    'decompressions': self.stats['decompressions']
                }
            }
            
            # Analyze keys by data source and type
            for key in all_keys[:1000]:  # Sample first 1000 keys
                try:
                    cached_data = await self.redis.get(key)
                    if cached_data:
                        entry_dict = pickle.loads(cached_data)
                        entry = CacheEntry.from_dict(entry_dict)
                        
                        source = entry.data_source.value
                        cache_type = entry.cache_type.value
                        
                        if source not in stats['by_data_source']:
                            stats['by_data_source'][source] = 0
                        stats['by_data_source'][source] += 1
                        
                        if cache_type not in stats['by_cache_type']:
                            stats['by_cache_type'][cache_type] = 0
                        stats['by_cache_type'][cache_type] += 1
                        
                except Exception as e:
                    logger.warning(f"Error analyzing cache key {key}: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}

    async def warm_cache(self, warming_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Warm cache with frequently accessed data"""
        
        results = {
            'total_tasks': len(warming_tasks),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for task in warming_tasks:
            try:
                data_source = DataSource(task['data_source'])
                query_params = task['query_params']
                cache_type = CacheType(task.get('cache_type', 'positive'))
                
                # Check if already cached
                existing = await self.get(data_source, query_params, cache_type)
                if existing is not None:
                    continue
                
                # Warm the cache by executing the actual API call
                # This would be implemented based on the specific data source
                if data_source == DataSource.SERPER:
                    # Example: warm Serper cache
                    from services.serper_service import SerperService
                    async with SerperService() as serper:
                        result = await serper.search_web(query_params.get('query', ''))
                        if result and result.results:
                            await self.set(data_source, query_params, result.results, cache_type)
                            results['successful'] += 1
                
                # Add other data sources as needed
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                logger.error(f"Error warming cache for task {task}: {e}")
        
        logger.info(f"Cache warming completed: {results['successful']} successful, {results['failed']} failed")
        return results

    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        
        cleaned_count = 0
        
        try:
            # Get all cache keys
            all_keys = await self.redis.keys(f"{self.cache_prefix}*")
            
            for key in all_keys:
                try:
                    cached_data = await self.redis.get(key)
                    if cached_data:
                        entry_dict = pickle.loads(cached_data)
                        entry = CacheEntry.from_dict(entry_dict)
                        
                        if entry.is_expired():
                            await self.redis.delete(key)
                            cleaned_count += 1
                            
                except Exception as e:
                    logger.warning(f"Error checking cache key {key}: {e}")
            
            # Clear expired entries from memory cache (TTLCache handles this automatically)
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired cache entries")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache entries: {e}")
            return 0


# Global unified cache instance
unified_cache = UnifiedCacheService()


# Convenience functions for different use cases
async def cache_api_response(data_source: DataSource, query_params: Dict[str, Any], 
                           response_data: Any, ttl_hours: Optional[float] = None) -> bool:
    """Cache a successful API response"""
    async with unified_cache as cache:
        return await cache.set(data_source, query_params, response_data, 
                              CacheType.POSITIVE, ttl_hours)


async def get_cached_response(data_source: DataSource, query_params: Dict[str, Any]) -> Optional[Any]:
    """Get cached API response"""
    async with unified_cache as cache:
        return await cache.get(data_source, query_params, CacheType.POSITIVE)


async def cache_null_response(data_source: DataSource, query_params: Dict[str, Any], 
                            reason: str, ttl_hours: Optional[float] = None) -> bool:
    """Cache a null/failed response"""
    async with unified_cache as cache:
        null_data = {'reason': reason, 'cached_at': datetime.now().isoformat()}
        return await cache.set(data_source, query_params, null_data, 
                              CacheType.NEGATIVE, ttl_hours)


async def is_null_cached(data_source: DataSource, query_params: Dict[str, Any]) -> bool:
    """Check if a null response is cached"""
    async with unified_cache as cache:
        result = await cache.get(data_source, query_params, CacheType.NEGATIVE)
        return result is not None


if __name__ == "__main__":
    # Test the unified cache
    async def test_unified_cache():
        print("🗄️  Testing Unified Cache Service")
        
        async with UnifiedCacheService() as cache:
            # Test caching positive result
            test_params = {'query': 'African AI startups', 'limit': 10}
            test_data = {'results': ['startup1', 'startup2'], 'count': 2}
            
            await cache.set(DataSource.SERPER, test_params, test_data, CacheType.POSITIVE)
            
            # Test getting cached result
            cached_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
            print(f"Cached result: {cached_result}")
            
            # Test cache stats
            stats = await cache.get_cache_stats()
            print(f"Cache stats: {json.dumps(stats, indent=2)}")
    
    asyncio.run(test_unified_cache())