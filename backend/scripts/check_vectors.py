#!/usr/bin/env python3
"""
Quick Vector Database Status Checker
Check current status of vector embeddings and coverage
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from config.database import get_supabase
from services.vector_service import get_vector_service


async def check_vector_status():
    """Check current vector database status"""
    try:
        print("🔍 TAIFA-FIALA Vector Database Status Check")
        print("=" * 50)
        
        # Initialize services
        print("🔧 Initializing services...")
        supabase = get_supabase()
        vector_service = await get_vector_service()
        
        # Get database counts
        print("\n📊 Database Status:")
        innovations_response = supabase.table('innovations').select('id', count='exact').execute()
        publications_response = supabase.table('publications').select('id', count='exact').execute()
        
        total_innovations = innovations_response.count if innovations_response.count is not None else 0
        total_publications = publications_response.count if publications_response.count is not None else 0
        total_documents = total_innovations + total_publications
        
        print(f"   • Innovations in DB: {total_innovations}")
        print(f"   • Publications in DB: {total_publications}")
        print(f"   • Total Documents: {total_documents}")
        
        # Get vector database stats
        print("\n🔍 Vector Database Status:")
        vector_stats = await vector_service.get_stats()
        
        total_vectors = vector_stats.get('total_vectors', 0)
        index_fullness = vector_stats.get('index_fullness', 0)
        dimension = vector_stats.get('dimension', 0)
        
        print(f"   • Total Vectors: {total_vectors}")
        print(f"   • Index Fullness: {index_fullness}")
        print(f"   • Vector Dimension: {dimension}")
        
        # Calculate coverage
        coverage_percentage = round((total_vectors / max(1, total_documents)) * 100, 1) if total_documents > 0 else 0
        missing_vectors = max(0, total_documents - total_vectors)
        
        print(f"\n📈 Coverage Analysis:")
        print(f"   • Vector Coverage: {coverage_percentage}%")
        print(f"   • Missing Vectors: {missing_vectors}")
        
        # Status assessment
        if total_vectors == 0:
            status = "🔴 NEEDS REBUILD - No vectors found"
        elif coverage_percentage < 50:
            status = "🟡 POOR COVERAGE - Rebuild recommended"
        elif coverage_percentage < 90:
            status = "🟠 PARTIAL COVERAGE - Some documents missing"
        else:
            status = "🟢 GOOD COVERAGE - Ready for search"
        
        print(f"\n🎯 Status: {status}")
        
        # Test search if vectors exist
        if total_vectors > 0:
            print(f"\n🧪 Testing Search Quality:")
            test_queries = ["AI agriculture", "machine learning healthcare", "fintech innovation"]
            
            for query in test_queries[:2]:  # Test first 2 queries
                try:
                    results = await vector_service.search_innovations(query, top_k=3)
                    avg_score = sum(r.score for r in results) / len(results) if results else 0
                    
                    print(f"   • '{query}': {len(results)} results, avg score: {avg_score:.3f}")
                    
                    if results:
                        best_result = results[0]
                        print(f"     └─ Best: '{best_result.metadata.get('title', 'No title')[:50]}...' (score: {best_result.score:.3f})")
                    
                except Exception as e:
                    print(f"   • '{query}': ERROR - {str(e)}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if total_vectors == 0:
            print("   • Run: python scripts/rebuild_vectors.py")
            print("   • Or use API: POST /api/vector/rebuild")
        elif coverage_percentage < 90:
            print("   • Consider running: python scripts/rebuild_vectors.py")
            print("   • Check for new documents that need vectorization")
        else:
            print("   • Vector database is healthy!")
            print("   • Monitor regularly with: GET /api/vector/stats")
        
        print("\n" + "=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Error checking vector status: {e}")
        return False


async def quick_search_test(query: str = "AI innovation Africa"):
    """Quick search test"""
    try:
        print(f"\n🔍 Quick Search Test: '{query}'")
        print("-" * 40)
        
        vector_service = await get_vector_service()
        results = await vector_service.search_innovations(query, top_k=5)
        
        if not results:
            print("❌ No results found - vector database may be empty")
            return False
        
        print(f"✅ Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            title = result.metadata.get('title', 'No title')
            score = result.score
            innovation_type = result.metadata.get('innovation_type', 'Unknown')
            
            print(f"   {i}. {title[:60]}...")
            print(f"      Score: {score:.3f} | Type: {innovation_type}")
        
        avg_score = sum(r.score for r in results) / len(results)
        print(f"\n📊 Average Relevance Score: {avg_score:.3f}")
        
        if avg_score > 0.8:
            print("🎉 Excellent search quality!")
        elif avg_score > 0.6:
            print("👍 Good search quality")
        else:
            print("⚠️ Search quality could be improved")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check TAIFA-FIALA vector database status")
    parser.add_argument("--search", type=str, help="Test search with custom query")
    parser.add_argument("--quick-test", action="store_true", help="Run quick search test")
    
    args = parser.parse_args()
    
    if args.search:
        asyncio.run(quick_search_test(args.search))
    elif args.quick_test:
        asyncio.run(quick_search_test())
    else:
        asyncio.run(check_vector_status())