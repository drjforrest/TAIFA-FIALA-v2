#!/usr/bin/env python3
"""
Comprehensive Caching System Test Suite
=======================================

Tests the unified caching system, null result cache, and all integrations.
Run this script to validate the caching implementation before production.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import os
import sys

# Add backend to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.unified_cache import UnifiedCacheService, DataSource, CacheType
from services.null_result_cache import NullResultCache, CacheReason
from services.citation_extractor import CitationExtractor
import redis.asyncio as aioredis


class CacheTestSuite:
    """Comprehensive test suite for caching system"""
    
    def __init__(self):
        self.test_results = []
        self.redis_available = False
        
    async def check_redis_connection(self) -> bool:
        """Check if Redis is available"""
        try:
            # Try to connect to Redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            redis_password = os.getenv('REDIS_PASSWORD')
            
            if redis_password:
                if "://" in redis_url:
                    protocol, rest = redis_url.split("://", 1)
                    if "@" not in rest:
                        redis_url = f"{protocol}://default:{redis_password}@{rest}"
            
            redis = await aioredis.from_url(redis_url, decode_responses=True)
            await redis.ping()
            await redis.close()
            print("✅ Redis connection successful")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            print("💡 Make sure Redis is running and REDIS_URL/REDIS_PASSWORD are set correctly")
            return False
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_unified_cache_basic_operations(self):
        """Test basic unified cache operations"""
        print("\n🧪 Testing Unified Cache Basic Operations")
        
        try:
            async with UnifiedCacheService() as cache:
                # Test data
                test_params = {'query': 'test_african_ai', 'limit': 10}
                test_data = {'results': ['startup1', 'startup2'], 'total': 2}
                
                # Test set operation
                success = await cache.set(
                    DataSource.SERPER, 
                    test_params, 
                    test_data, 
                    CacheType.POSITIVE,
                    0.01  # 36 seconds for testing
                )
                self.log_test("Unified Cache - Set Operation", success)
                
                # Test get operation
                cached_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
                get_success = cached_result is not None and cached_result['total'] == 2
                self.log_test("Unified Cache - Get Operation", get_success, 
                            f"Retrieved: {cached_result}")
                
                # Test cache stats
                stats = await cache.get_cache_stats()
                stats_success = 'performance' in stats and stats['performance']['sets'] > 0
                self.log_test("Unified Cache - Stats Retrieval", stats_success,
                            f"Hit rate: {stats.get('hit_rate', 0):.2f}")
                
                # Test delete operation
                delete_success = await cache.delete(DataSource.SERPER, test_params, CacheType.POSITIVE)
                self.log_test("Unified Cache - Delete Operation", delete_success)
                
        except Exception as e:
            self.log_test("Unified Cache - Basic Operations", False, str(e))
    
    async def test_null_result_cache(self):
        """Test null result cache functionality"""
        print("\n🧪 Testing Null Result Cache")
        
        try:
            async with NullResultCache() as null_cache:
                # Test caching null result
                cache_key = await null_cache.cache_null_result(
                    DataSource.WEB_SCRAPING,
                    {'url': 'https://invalid-test-url.com'},
                    CacheReason.INVALID_URL,
                    {'test': True}
                )
                
                cache_success = cache_key is not None
                self.log_test("Null Cache - Cache Null Result", cache_success)
                
                # Test checking cached null result
                is_cached, entry = await null_cache.is_cached_as_null(
                    DataSource.WEB_SCRAPING,
                    {'url': 'https://invalid-test-url.com'}
                )
                
                check_success = is_cached and entry is not None
                self.log_test("Null Cache - Check Cached Result", check_success,
                            f"Reason: {entry.reason.value if entry else 'None'}")
                
                # Test cache stats
                stats = await null_cache.get_cache_stats()
                stats_success = stats.get('total_cached_items', 0) > 0
                self.log_test("Null Cache - Stats Retrieval", stats_success,
                            f"Total items: {stats.get('total_cached_items', 0)}")
                
        except Exception as e:
            self.log_test("Null Cache - Operations", False, str(e))
    
    async def test_cache_compression(self):
        """Test cache compression functionality"""
        print("\n🧪 Testing Cache Compression")
        
        try:
            async with UnifiedCacheService() as cache:
                # Test with large data that should trigger compression
                large_data = {
                    'content': 'A' * 50000,  # 50KB of data
                    'results': [{'item': i, 'description': 'B' * 1000} for i in range(100)]
                }
                
                test_params = {'query': 'compression_test', 'size': 'large'}
                
                # Cache the large data
                success = await cache.set(
                    DataSource.PERPLEXITY,
                    test_params,
                    large_data,
                    CacheType.POSITIVE,
                    0.01  # Short TTL for testing
                )
                
                self.log_test("Cache Compression - Set Large Data", success)
                
                # Retrieve and verify
                retrieved_data = await cache.get(DataSource.PERPLEXITY, test_params, CacheType.POSITIVE)
                compression_success = (retrieved_data is not None and 
                                     retrieved_data['content'] == large_data['content'])
                
                self.log_test("Cache Compression - Retrieve Compressed Data", compression_success)
                
                # Check compression stats
                stats = await cache.get_cache_stats()
                compression_stats = stats.get('compression_stats', {}).get('compressions', 0) > 0
                self.log_test("Cache Compression - Compression Stats", compression_stats,
                            f"Compressions: {stats.get('compression_stats', {}).get('compressions', 0)}")
                
        except Exception as e:
            self.log_test("Cache Compression", False, str(e))
    
    async def test_citation_cache_integration(self):
        """Test citation extractor cache integration"""
        print("\n🧪 Testing Citation Cache Integration")
        
        try:
            from services.null_result_cache import check_citation_cache, cache_null_citation
            
            # Test caching invalid citation
            test_url = "https://twitter.com/invalid-citation"
            await cache_null_citation(test_url, "academic_paper", CacheReason.IRRELEVANT_CONTENT)
            
            # Test checking cached citation
            is_cached, entry = await check_citation_cache(test_url, "academic_paper")
            
            integration_success = is_cached and entry is not None
            self.log_test("Citation Cache - Integration Test", integration_success,
                        f"URL cached as: {entry.reason.value if entry else 'None'}")
            
        except Exception as e:
            self.log_test("Citation Cache Integration", False, str(e))
    
    async def test_cache_performance(self):
        """Test cache performance with multiple operations"""
        print("\n🧪 Testing Cache Performance")
        
        try:
            async with UnifiedCacheService() as cache:
                # Perform multiple cache operations to test performance
                num_operations = 50
                start_time = time.time()
                
                # Set multiple items
                for i in range(num_operations):
                    test_params = {'query': f'performance_test_{i}', 'index': i}
                    test_data = {'result': f'data_{i}', 'timestamp': datetime.now().isoformat()}
                    
                    await cache.set(DataSource.SERPER, test_params, test_data, CacheType.POSITIVE, 0.1)
                
                set_time = time.time() - start_time
                
                # Get multiple items
                start_time = time.time()
                hits = 0
                
                for i in range(num_operations):
                    test_params = {'query': f'performance_test_{i}', 'index': i}
                    result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
                    if result:
                        hits += 1
                
                get_time = time.time() - start_time
                
                performance_success = hits == num_operations
                self.log_test("Cache Performance - Bulk Operations", performance_success,
                            f"Set: {set_time:.3f}s, Get: {get_time:.3f}s, Hit rate: {hits}/{num_operations}")
                
                # Test memory vs Redis performance
                stats = await cache.get_cache_stats()
                memory_hits = stats.get('performance', {}).get('memory_hits', 0)
                redis_hits = stats.get('performance', {}).get('redis_hits', 0)
                
                self.log_test("Cache Performance - Memory vs Redis", True,
                            f"Memory hits: {memory_hits}, Redis hits: {redis_hits}")
                
        except Exception as e:
            self.log_test("Cache Performance", False, str(e))
    
    async def test_cache_ttl_and_expiration(self):
        """Test cache TTL and expiration logic"""
        print("\n🧪 Testing Cache TTL and Expiration")
        
        try:
            async with UnifiedCacheService() as cache:
                # Set item with very short TTL
                test_params = {'query': 'ttl_test', 'expire': True}
                test_data = {'message': 'this should expire'}
                
                await cache.set(DataSource.SERPER, test_params, test_data, 
                              CacheType.POSITIVE, 0.002)  # ~7 seconds
                
                # Immediately check - should be there
                immediate_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
                immediate_success = immediate_result is not None
                self.log_test("Cache TTL - Immediate Retrieval", immediate_success)
                
                # Wait for expiration
                print("    Waiting for cache expiration...")
                await asyncio.sleep(8)
                
                # Check after expiration - should be None
                expired_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
                expiration_success = expired_result is None
                self.log_test("Cache TTL - Post-Expiration Retrieval", expiration_success,
                            "Item correctly expired from cache")
                
        except Exception as e:
            self.log_test("Cache TTL and Expiration", False, str(e))
    
    async def test_error_handling(self):
        """Test cache error handling"""
        print("\n🧪 Testing Cache Error Handling")
        
        try:
            async with UnifiedCacheService() as cache:
                # Test with invalid data source
                try:
                    # This should handle gracefully
                    result = await cache.get("invalid_source", {}, CacheType.POSITIVE)
                    error_handling_success = True  # If we get here, error was handled
                except Exception:
                    error_handling_success = False
                
                self.log_test("Cache Error Handling - Invalid Data Source", error_handling_success)
                
                # Test with extremely large cache key
                large_params = {f'key_{i}': f'value_{i}' * 1000 for i in range(100)}
                
                try:
                    await cache.set(DataSource.SERPER, large_params, {'test': True}, CacheType.POSITIVE)
                    large_key_success = True
                except Exception:
                    large_key_success = False
                
                self.log_test("Cache Error Handling - Large Cache Key", large_key_success)
                
        except Exception as e:
            self.log_test("Cache Error Handling", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏁 CACHE SYSTEM TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n📊 Cache Performance Recommendations:")
        if passed_tests >= total_tests * 0.8:
            print("✅ Cache system is ready for production!")
            print("💡 Consider enabling cache warming for frequently accessed data")
        else:
            print("⚠️  Cache system needs attention before production")
            print("🔧 Review failed tests and fix issues")
        
        # Save results to file
        with open('cache_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'test_date': datetime.now().isoformat()
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: cache_test_results.json")
    
    async def run_all_tests(self):
        """Run all cache tests"""
        print("🚀 Starting Comprehensive Cache System Tests")
        print("="*60)
        
        # Check Redis availability first
        self.redis_available = await self.check_redis_connection()
        
        if not self.redis_available:
            print("\n⚠️  Redis not available. Some tests will be skipped.")
            print("💡 Install and start Redis for full testing:")
            print("   - macOS: brew install redis && brew services start redis")
            print("   - Ubuntu: sudo apt install redis-server && sudo systemctl start redis")
            print("   - Docker: docker run -d -p 6379:6379 redis:alpine")
            return
        
        # Run all test suites
        test_suites = [
            self.test_unified_cache_basic_operations,
            self.test_null_result_cache,
            self.test_cache_compression,
            self.test_citation_cache_integration,
            self.test_cache_performance,
            self.test_cache_ttl_and_expiration,
            self.test_error_handling
        ]
        
        for test_suite in test_suites:
            try:
                await test_suite()
            except Exception as e:
                self.log_test(f"Test Suite: {test_suite.__name__}", False, str(e))
        
        self.print_summary()


async def main():
    """Main test execution"""
    print("🧪 TAIFA-FIALA Cache System Test Suite")
    print("=====================================\n")
    
    # Check environment variables
    print("🔍 Checking Environment Setup:")
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_password = os.getenv('REDIS_PASSWORD')
    
    print(f"Redis URL: {redis_url}")
    if redis_password:
        print("Redis Password: ✅ Set")
    else:
        print("Redis Password: ⚠️  Not set (OK for local development)")
    
    # Run tests
    test_suite = CacheTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())