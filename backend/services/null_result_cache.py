"""
Null Result Cache Service
========================

Caches null/empty results from various data sources to prevent redundant API calls
and reduce costs. Implements intelligent cache invalidation and retry logic.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import aioredis
from loguru import logger

from config.settings import settings


class CacheReason(Enum):
    """Reasons why a result was cached as null"""
    NO_CONTENT_FOUND = "no_content_found"
    API_ERROR = "api_error" 
    TIMEOUT = "timeout"
    INVALID_URL = "invalid_url"
    ACCESS_DENIED = "access_denied"
    RATE_LIMITED = "rate_limited"
    LOW_QUALITY = "low_quality"
    IRRELEVANT_CONTENT = "irrelevant_content"


class DataSource(Enum):
    """Different data sources that can have null results"""
    PERPLEXITY = "perplexity"
    SERPER = "serper"
    WEB_SCRAPING = "web_scraping"
    GITHUB_API = "github_api"
    ARXIV_API = "arxiv_api"
    PUBMED_API = "pubmed_api"
    COMPANY_WEBSITE = "company_website"
    CITATION_EXTRACTION = "citation_extraction"


@dataclass
class NullResultEntry:
    """Represents a cached null result"""
    cache_key: str
    data_source: DataSource
    query_params: Dict[str, Any]
    reason: CacheReason
    cached_at: datetime
    retry_after: datetime
    retry_count: int = 0
    last_retry: Optional[datetime] = None
    permanent: bool = False  # Some results should never be retried
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['data_source'] = self.data_source.value
        data['reason'] = self.reason.value
        data['cached_at'] = self.cached_at.isoformat()
        data['retry_after'] = self.retry_after.isoformat()
        if self.last_retry:
            data['last_retry'] = self.last_retry.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NullResultEntry':
        """Create from dictionary"""
        return cls(
            cache_key=data['cache_key'],
            data_source=DataSource(data['data_source']),
            query_params=data['query_params'],
            reason=CacheReason(data['reason']),
            cached_at=datetime.fromisoformat(data['cached_at']),
            retry_after=datetime.fromisoformat(data['retry_after']),
            retry_count=data.get('retry_count', 0),
            last_retry=datetime.fromisoformat(data['last_retry']) if data.get('last_retry') else None,
            permanent=data.get('permanent', False),
            metadata=data.get('metadata', {})
        )


class NullResultCache:
    """Cache service for null/empty results"""
    
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
        self.cache_prefix = "null_cache:"
        
        # Cache TTL settings by reason (in hours)
        self.ttl_settings = {
            CacheReason.NO_CONTENT_FOUND: 24,      # 24 hours - content might appear
            CacheReason.API_ERROR: 1,              # 1 hour - might be temporary
            CacheReason.TIMEOUT: 4,                # 4 hours - could be temporary
            CacheReason.INVALID_URL: 168,          # 7 days - URLs rarely become valid
            CacheReason.ACCESS_DENIED: 72,         # 3 days - access might change
            CacheReason.RATE_LIMITED: 0.5,         # 30 minutes - retry soon
            CacheReason.LOW_QUALITY: 48,           # 2 days - quality might improve
            CacheReason.IRRELEVANT_CONTENT: 72     # 3 days - relevance is stable
        }
        
        # Retry settings
        self.max_retries = {
            CacheReason.NO_CONTENT_FOUND: 3,
            CacheReason.API_ERROR: 5,
            CacheReason.TIMEOUT: 3,
            CacheReason.INVALID_URL: 1,  # Don't retry invalid URLs much
            CacheReason.ACCESS_DENIED: 2,
            CacheReason.RATE_LIMITED: 10,  # Keep retrying rate limits
            CacheReason.LOW_QUALITY: 2,
            CacheReason.IRRELEVANT_CONTENT: 1
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.redis:
            await self.redis.close()

    def _generate_cache_key(self, data_source: DataSource, query_params: Dict[str, Any]) -> str:
        """Generate a consistent cache key for query parameters"""
        
        # Normalize parameters for consistent hashing
        normalized_params = {}
        
        for key, value in query_params.items():
            if isinstance(value, (list, tuple)):
                normalized_params[key] = sorted(str(v) for v in value)
            elif isinstance(value, dict):
                normalized_params[key] = json.dumps(value, sort_keys=True)
            else:
                normalized_params[key] = str(value)
        
        # Create hash of normalized parameters
        param_string = json.dumps(normalized_params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:12]
        
        return f"{self.cache_prefix}{data_source.value}:{param_hash}"

    async def is_cached_as_null(self, data_source: DataSource, query_params: Dict[str, Any]) -> Tuple[bool, Optional[NullResultEntry]]:
        """Check if a query is cached as null result"""
        
        cache_key = self._generate_cache_key(data_source, query_params)
        
        try:
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                entry = NullResultEntry.from_dict(json.loads(cached_data))
                
                # Check if it's time to retry
                if datetime.now() >= entry.retry_after and not entry.permanent:
                    logger.debug(f"Cache entry {cache_key} is due for retry")
                    return False, entry
                
                logger.debug(f"Found cached null result for {data_source.value}: {entry.reason.value}")
                return True, entry
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking null result cache: {e}")
            return False, None

    async def cache_null_result(self, 
                              data_source: DataSource, 
                              query_params: Dict[str, Any],
                              reason: CacheReason,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """Cache a null result"""
        
        cache_key = self._generate_cache_key(data_source, query_params)
        
        # Check if we already have this cached (for retry logic)
        existing_entry = None
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                existing_entry = NullResultEntry.from_dict(json.loads(cached_data))
        except Exception:
            pass
        
        # Calculate retry time based on reason and retry count
        retry_count = existing_entry.retry_count + 1 if existing_entry else 0
        max_retries = self.max_retries.get(reason, 3)
        
        # Determine if this should be permanent
        permanent = retry_count >= max_retries
        
        # Calculate retry delay with exponential backoff
        base_ttl_hours = self.ttl_settings.get(reason, 24)
        retry_delay_hours = base_ttl_hours * (2 ** min(retry_count, 5))  # Cap exponential growth
        retry_after = datetime.now() + timedelta(hours=retry_delay_hours)
        
        # Create cache entry
        entry = NullResultEntry(
            cache_key=cache_key,
            data_source=data_source,
            query_params=query_params.copy(),
            reason=reason,
            cached_at=datetime.now(),
            retry_after=retry_after,
            retry_count=retry_count,
            last_retry=existing_entry.last_retry if existing_entry else None,
            permanent=permanent,
            metadata=metadata or {}
        )
        
        try:
            # Store in Redis with TTL
            cache_ttl_seconds = int(retry_delay_hours * 3600)
            await self.redis.setex(
                cache_key, 
                cache_ttl_seconds,
                json.dumps(entry.to_dict())
            )
            
            logger.info(f"Cached null result for {data_source.value}: {reason.value} (retry #{retry_count}, permanent={permanent})")
            return cache_key
            
        except Exception as e:
            logger.error(f"Error caching null result: {e}")
            return cache_key

    async def mark_retry_attempted(self, cache_key: str, success: bool = False):
        """Mark that a retry was attempted"""
        
        try:
            cached_data = await self.redis.get(cache_key)
            if not cached_data:
                return
            
            entry = NullResultEntry.from_dict(json.loads(cached_data))
            
            if success:
                # Remove from cache if retry was successful
                await self.redis.delete(cache_key)
                logger.info(f"Removed successful retry from cache: {cache_key}")
            else:
                # Update last retry time
                entry.last_retry = datetime.now()
                
                # Store updated entry
                cache_ttl_seconds = int((entry.retry_after - datetime.now()).total_seconds())
                if cache_ttl_seconds > 0:
                    await self.redis.setex(
                        cache_key,
                        cache_ttl_seconds,
                        json.dumps(entry.to_dict())
                    )
                
        except Exception as e:
            logger.error(f"Error marking retry attempt: {e}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        try:
            # Get all cache keys
            cache_keys = await self.redis.keys(f"{self.cache_prefix}*")
            
            stats = {
                'total_cached_items': len(cache_keys),
                'by_data_source': {},
                'by_reason': {},
                'permanent_cache_count': 0,
                'retry_pending_count': 0,
                'cache_size_bytes': 0
            }
            
            for key in cache_keys:
                try:
                    cached_data = await self.redis.get(key)
                    if cached_data:
                        entry = NullResultEntry.from_dict(json.loads(cached_data))
                        
                        # Count by data source
                        source = entry.data_source.value
                        stats['by_data_source'][source] = stats['by_data_source'].get(source, 0) + 1
                        
                        # Count by reason
                        reason = entry.reason.value
                        stats['by_reason'][reason] = stats['by_reason'].get(reason, 0) + 1
                        
                        # Count permanent vs retry pending
                        if entry.permanent:
                            stats['permanent_cache_count'] += 1
                        elif datetime.now() >= entry.retry_after:
                            stats['retry_pending_count'] += 1
                        
                        # Estimate cache size
                        stats['cache_size_bytes'] += len(cached_data.encode('utf-8'))
                        
                except Exception as e:
                    logger.warning(f"Error processing cache key {key}: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}

    async def clear_expired_entries(self) -> int:
        """Clear expired cache entries (Redis should handle this automatically, but this is for cleanup)"""
        
        cleared_count = 0
        
        try:
            cache_keys = await self.redis.keys(f"{self.cache_prefix}*")
            
            for key in cache_keys:
                try:
                    cached_data = await self.redis.get(key)
                    if cached_data:
                        entry = NullResultEntry.from_dict(json.loads(cached_data))
                        
                        # If entry is past retry time and not permanent, consider removing
                        if (not entry.permanent and 
                            datetime.now() > entry.retry_after + timedelta(hours=24)):
                            
                            await self.redis.delete(key)
                            cleared_count += 1
                            
                except Exception as e:
                    logger.warning(f"Error clearing cache key {key}: {e}")
            
            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} expired cache entries")
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing expired entries: {e}")
            return 0

    async def force_clear_cache(self, data_source: Optional[DataSource] = None) -> int:
        """Force clear cache entries (optionally filtered by data source)"""
        
        try:
            if data_source:
                pattern = f"{self.cache_prefix}{data_source.value}:*"
            else:
                pattern = f"{self.cache_prefix}*"
            
            cache_keys = await self.redis.keys(pattern)
            
            if cache_keys:
                cleared_count = await self.redis.delete(*cache_keys)
                logger.info(f"Force cleared {cleared_count} cache entries")
                return cleared_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error force clearing cache: {e}")
            return 0


# Global cache instance
null_result_cache = NullResultCache()


# Convenience functions for different services
async def check_citation_cache(url: str, citation_type: str) -> Tuple[bool, Optional[NullResultEntry]]:
    """Check if a citation URL is cached as null"""
    
    query_params = {
        'url': url,
        'citation_type': citation_type
    }
    
    async with null_result_cache as cache:
        return await cache.is_cached_as_null(DataSource.CITATION_EXTRACTION, query_params)


async def cache_null_citation(url: str, citation_type: str, reason: CacheReason, metadata: Dict[str, Any] = None):
    """Cache a null citation result"""
    
    query_params = {
        'url': url,
        'citation_type': citation_type
    }
    
    async with null_result_cache as cache:
        return await cache.cache_null_result(
            DataSource.CITATION_EXTRACTION, 
            query_params, 
            reason, 
            metadata
        )


async def check_web_scraping_cache(url: str) -> Tuple[bool, Optional[NullResultEntry]]:
    """Check if a web scraping URL is cached as null"""
    
    query_params = {'url': url}
    
    async with null_result_cache as cache:
        return await cache.is_cached_as_null(DataSource.WEB_SCRAPING, query_params)


async def cache_null_web_scraping(url: str, reason: CacheReason, metadata: Dict[str, Any] = None):
    """Cache a null web scraping result"""
    
    query_params = {'url': url}
    
    async with null_result_cache as cache:
        return await cache.cache_null_result(
            DataSource.WEB_SCRAPING, 
            query_params, 
            reason, 
            metadata
        )


async def check_api_cache(data_source: DataSource, query_params: Dict[str, Any]) -> Tuple[bool, Optional[NullResultEntry]]:
    """Generic API cache check"""
    
    async with null_result_cache as cache:
        return await cache.is_cached_as_null(data_source, query_params)


async def cache_null_api_result(data_source: DataSource, query_params: Dict[str, Any], reason: CacheReason, metadata: Dict[str, Any] = None):
    """Generic API null result caching"""
    
    async with null_result_cache as cache:
        return await cache.cache_null_result(data_source, query_params, reason, metadata)


if __name__ == "__main__":
    # Test the null result cache
    async def test_null_cache():
        print("🗃️  Testing Null Result Cache")
        
        async with NullResultCache() as cache:
            # Test caching a null citation
            test_params = {
                'url': 'https://example.com/nonexistent-paper',
                'citation_type': 'academic_paper'
            }
            
            # Cache a null result
            cache_key = await cache.cache_null_result(
                DataSource.CITATION_EXTRACTION,
                test_params,
                CacheReason.NO_CONTENT_FOUND,
                {'attempted_at': datetime.now().isoformat()}
            )
            
            print(f"Cached null result: {cache_key}")
            
            # Check if it's cached
            is_cached, entry = await cache.is_cached_as_null(
                DataSource.CITATION_EXTRACTION,
                test_params
            )
            
            print(f"Is cached: {is_cached}")
            if entry:
                print(f"Cache reason: {entry.reason.value}")
                print(f"Retry after: {entry.retry_after}")
                print(f"Retry count: {entry.retry_count}")
            
            # Get stats
            stats = await cache.get_cache_stats()
            print(f"Cache stats: {stats}")
    
    asyncio.run(test_null_cache())