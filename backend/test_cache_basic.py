#!/usr/bin/env python3
"""
Basic Cache System Test
======================
Tests core caching functionality without database dependencies.
"""

import asyncio
import json
import time
from datetime import datetime
import os
import sys

# Add backend to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.unified_cache import UnifiedCacheService, DataSource, CacheType
from services.null_result_cache import NullResultCache, CacheReason
import redis.asyncio as aioredis


async def test_redis_connection():
    """Test Redis connection"""
    print("🔍 Testing Redis Connection...")
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        redis_password = os.getenv('REDIS_PASSWORD')
        
        if redis_password:
            if "://" in redis_url:
                protocol, rest = redis_url.split("://", 1)
                if "@" not in rest:
                    redis_url = f"{protocol}://default:{redis_password}@{rest}"
        
        redis = aioredis.from_url(redis_url, decode_responses=True)
        result = await redis.ping()
        await redis.close()
        print(f"✅ Redis connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def test_unified_cache():
    """Test unified cache basic operations"""
    print("\n🧪 Testing Unified Cache...")
    
    try:
        async with UnifiedCacheService() as cache:
            # Test data
            test_params = {'query': 'test_african_ai', 'limit': 10}
            test_data = {'results': ['startup1', 'startup2'], 'total': 2}
            
            print("  📝 Testing cache SET operation...")
            success = await cache.set(
                DataSource.SERPER, 
                test_params, 
                test_data, 
                CacheType.POSITIVE,
                0.01  # Short TTL for testing
            )
            print(f"     Result: {'✅ Success' if success else '❌ Failed'}")
            
            print("  📖 Testing cache GET operation...")
            cached_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
            get_success = cached_result is not None and cached_result['total'] == 2
            print(f"     Result: {'✅ Success' if get_success else '❌ Failed'}")
            if cached_result:
                print(f"     Retrieved: {cached_result}")
            
            print("  📊 Testing cache stats...")
            stats = await cache.get_cache_stats()
            stats_success = 'performance' in stats
            print(f"     Result: {'✅ Success' if stats_success else '❌ Failed'}")
            if stats_success:
                print(f"     Hit rate: {stats.get('hit_rate', 0):.2f}")
                print(f"     Total hits: {stats.get('performance', {}).get('hits', 0)}")
                print(f"     Total sets: {stats.get('performance', {}).get('sets', 0)}")
            
            return success and get_success and stats_success
            
    except Exception as e:
        print(f"❌ Unified cache test failed: {e}")
        return False


async def test_null_cache():
    """Test null result cache"""
    print("\n🚫 Testing Null Result Cache...")
    
    try:
        async with NullResultCache() as null_cache:
            print("  📝 Testing null result caching...")
            cache_key = await null_cache.cache_null_result(
                DataSource.WEB_SCRAPING,
                {'url': 'https://invalid-test-url.com'},
                CacheReason.INVALID_URL,
                {'test': True}
            )
            
            cache_success = cache_key is not None
            print(f"     Cache operation: {'✅ Success' if cache_success else '❌ Failed'}")
            
            print("  📖 Testing null result retrieval...")
            is_cached, entry = await null_cache.is_cached_as_null(
                DataSource.WEB_SCRAPING,
                {'url': 'https://invalid-test-url.com'}
            )
            
            check_success = is_cached and entry is not None
            print(f"     Retrieval: {'✅ Success' if check_success else '❌ Failed'}")
            if entry:
                print(f"     Reason: {entry.reason.value}")
                print(f"     Retry after: {entry.retry_after}")
            
            print("  📊 Testing null cache stats...")
            stats = await null_cache.get_cache_stats()
            stats_success = stats.get('total_cached_items', 0) > 0
            print(f"     Stats: {'✅ Success' if stats_success else '❌ Failed'}")
            if stats_success:
                print(f"     Total items: {stats.get('total_cached_items', 0)}")
                print(f"     By reason: {stats.get('by_reason', {})}")
            
            return cache_success and check_success and stats_success
            
    except Exception as e:
        print(f"❌ Null cache test failed: {e}")
        return False


async def test_cache_performance():
    """Test cache performance"""
    print("\n⚡ Testing Cache Performance...")
    
    try:
        async with UnifiedCacheService() as cache:
            print("  🏃 Running performance test with 20 operations...")
            
            # Set operations
            start_time = time.time()
            for i in range(20):
                test_params = {'query': f'perf_test_{i}', 'index': i}
                test_data = {'result': f'data_{i}', 'timestamp': datetime.now().isoformat()}
                await cache.set(DataSource.SERPER, test_params, test_data, CacheType.POSITIVE, 0.1)
            
            set_time = time.time() - start_time
            print(f"     Set operations: {set_time:.3f}s ({20/set_time:.1f} ops/sec)")
            
            # Get operations
            start_time = time.time()
            hits = 0
            for i in range(20):
                test_params = {'query': f'perf_test_{i}', 'index': i}
                result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
                if result:
                    hits += 1
            
            get_time = time.time() - start_time
            print(f"     Get operations: {get_time:.3f}s ({20/get_time:.1f} ops/sec)")
            print(f"     Hit rate: {hits}/20 ({hits/20*100:.1f}%)")
            
            return hits == 20
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


async def test_cache_compression():
    """Test cache compression"""
    print("\n🗜️  Testing Cache Compression...")
    
    try:
        async with UnifiedCacheService() as cache:
            # Create large data that should trigger compression
            large_data = {
                'content': 'A' * 10000,  # 10KB of data
                'results': [{'item': i, 'description': 'B' * 500} for i in range(50)]
            }
            
            test_params = {'query': 'compression_test', 'size': 'large'}
            
            print("  📝 Caching large data (should trigger compression)...")
            success = await cache.set(
                DataSource.PERPLEXITY,
                test_params,
                large_data,
                CacheType.POSITIVE,
                0.01
            )
            print(f"     Cache operation: {'✅ Success' if success else '❌ Failed'}")
            
            print("  📖 Retrieving compressed data...")
            retrieved_data = await cache.get(DataSource.PERPLEXITY, test_params, CacheType.POSITIVE)
            compression_success = (retrieved_data is not None and 
                                 retrieved_data['content'] == large_data['content'])
            print(f"     Retrieval: {'✅ Success' if compression_success else '❌ Failed'}")
            
            print("  📊 Checking compression stats...")
            stats = await cache.get_cache_stats()
            compressions = stats.get('compression_stats', {}).get('compressions', 0)
            print(f"     Compressions performed: {compressions}")
            
            return success and compression_success
            
    except Exception as e:
        print(f"❌ Compression test failed: {e}")
        return False


async def test_cache_ttl():
    """Test cache TTL (Time To Live)"""
    print("\n⏰ Testing Cache TTL...")
    
    try:
        async with UnifiedCacheService() as cache:
            test_params = {'query': 'ttl_test', 'expire': True}
            test_data = {'message': 'this should expire'}
            
            print("  📝 Setting cache with 3-second TTL...")
            await cache.set(DataSource.SERPER, test_params, test_data, 
                          CacheType.POSITIVE, 0.001)  # ~3.6 seconds
            
            print("  📖 Immediate retrieval (should work)...")
            immediate_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
            immediate_success = immediate_result is not None
            print(f"     Result: {'✅ Found' if immediate_success else '❌ Not found'}")
            
            print("  ⏳ Waiting 5 seconds for expiration...")
            await asyncio.sleep(5)
            
            print("  📖 Post-expiration retrieval (should fail)...")
            expired_result = await cache.get(DataSource.SERPER, test_params, CacheType.POSITIVE)
            expiration_success = expired_result is None
            print(f"     Result: {'✅ Correctly expired' if expiration_success else '❌ Still cached'}")
            
            return immediate_success and expiration_success
            
    except Exception as e:
        print(f"❌ TTL test failed: {e}")
        return False


async def main():
    """Run all cache tests"""
    print("🚀 TAIFA-FIALA Cache System Basic Tests")
    print("=" * 50)
    
    # Environment check
    print("🔍 Environment Check:")
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_password = os.getenv('REDIS_PASSWORD', 'Not set')
    print(f"   Redis URL: {redis_url}")
    print(f"   Redis Password: {'Set' if redis_password != 'Not set' else 'Not set'}")
    
    # Test Redis connection
    redis_ok = await test_redis_connection()
    if not redis_ok:
        print("\n❌ Cannot proceed without Redis. Please start Redis and try again.")
        return
    
    # Run tests
    tests = [
        ("Unified Cache", test_unified_cache),
        ("Null Result Cache", test_null_cache),
        ("Cache Performance", test_cache_performance),
        ("Cache Compression", test_cache_compression),
        ("Cache TTL", test_cache_ttl),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All cache tests passed! System is ready for production.")
        print("💡 Next steps:")
        print("   - Start the backend: ./start_backend_dev.sh")
        print("   - Test cache endpoints: curl http://localhost:8000/api/etl/cache/unified/stats")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Please review the issues above.")
    
    # Save results
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total,
        'passed_tests': passed,
        'failed_tests': total - passed,
        'success_rate': passed/total*100,
        'results': [{'test': name, 'passed': result} for name, result in results]
    }
    
    with open('cache_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Results saved to: cache_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())