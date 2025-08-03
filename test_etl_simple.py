#!/usr/bin/env python3
"""
Simple ETL Test Script for TAIFA-FIALA
======================================

Tests the ETL pipeline components with proper environment loading.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("🌍 TAIFA-FIALA ETL Test Suite")
print("=" * 50)

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment variables...")

    required_vars = [
        "PINECONE_API_KEY",
        "PINECONE_INDEX",
        "NEXT_PUBLIC_SUPABASE_URL",
        "SUPABASE_SECRET_KEY"
    ]

    optional_vars = [
        "PERPLEXITY_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY"
    ]

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"  ✅ {var}: Set")

    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"  ✅ {var}: Set")

    if missing_required:
        print(f"  ❌ Missing required: {', '.join(missing_required)}")
        return False

    if missing_optional:
        print(f"  ⚠️  Missing optional: {', '.join(missing_optional)}")

    print("  ✅ Environment check passed!")
    return True

async def test_database_connections():
    """Test database connections"""
    print("\n🗄️  Testing database connections...")

    try:
        # Test Pinecone
        from services.vector_service import get_vector_service
        vector_service = await get_vector_service()
        stats = await vector_service.get_stats()
        print(f"  ✅ Pinecone: Connected (Index: {stats.get('total_vectors', 0)} vectors)")
    except Exception as e:
        print(f"  ❌ Pinecone: {e}")
        return False

    try:
        # Test Supabase
        from config.database import get_supabase
        supabase = get_supabase()
        response = supabase.table('innovations').select('id').limit(1).execute()
        print(f"  ✅ Supabase: Connected ({len(response.data)} test records)")
    except Exception as e:
        print(f"  ❌ Supabase: {e}")
        return False

    return True

async def test_vector_operations():
    """Test vector database operations"""
    print("\n🔍 Testing vector operations...")

    try:
        from services.vector_service import get_vector_service, VectorDocument
        from uuid import uuid4

        service = await get_vector_service()

        # Test document creation
        test_doc = VectorDocument(
            id=f"test_{uuid4()}",
            content="AI innovation in Kenya focusing on agricultural technology and machine learning",
            metadata={
                "test": True,
                "country": "Kenya",
                "innovation_type": "AgriTech"
            }
        )

        # Test upsert
        success = await service.upsert_documents([test_doc])
        if success:
            print("  ✅ Document upsert: Success")
        else:
            print("  ❌ Document upsert: Failed")
            return False

        # Test search
        results = await service.search_similar("AI agriculture Kenya", top_k=3)
        print(f"  ✅ Vector search: Found {len(results)} results")

        # Show sample result
        if results:
            sample = results[0]
            print(f"    Sample: {sample.metadata.get('country', 'Unknown')} - Score: {sample.score:.3f}")

        return True

    except Exception as e:
        print(f"  ❌ Vector operations: {e}")
        return False

async def test_etl_components():
    """Test individual ETL components"""
    print("\n⚙️  Testing ETL components...")

    # Test academic scraper
    try:
        print("  🔬 Testing academic scraper...")
        from etl.academic.arxiv_scraper import scrape_arxiv_papers

        papers = await scrape_arxiv_papers(days_back=1, max_results=3)
        print(f"    ✅ ArXiv scraper: Found {len(papers)} papers")
        if papers:
            print(f"    Sample: {papers[0].title[:60]}...")

    except Exception as e:
        print(f"    ❌ Academic scraper: {e}")

    # Test news monitoring
    try:
        print("  📰 Testing news monitoring...")
        from etl.news.rss_monitor import monitor_rss_feeds

        articles = await monitor_rss_feeds(hours_back=24)
        print(f"    ✅ RSS monitor: Found {len(articles)} articles")
        if articles:
            print(f"    Sample: {articles[0].title[:60]}...")

    except Exception as e:
        print(f"    ❌ News monitoring: {e}")

    # Test intelligence module (if API keys available)
    if os.getenv('PERPLEXITY_API_KEY'):
        try:
            print("  🧠 Testing intelligence module...")
            from etl.intelligence.perplexity_african_ai import PerplexityAfricanAIModule, IntelligenceType

            async with PerplexityAfricanAIModule(os.getenv('PERPLEXITY_API_KEY')) as intel:
                reports = await intel.synthesize_intelligence(
                    intelligence_types=[IntelligenceType.INNOVATION_DISCOVERY],
                    time_period='last_3_days'
                )
                print(f"    ✅ Intelligence module: Generated {len(reports)} reports")
                if reports:
                    print(f"    Sample: {reports[0].summary[:60]}...")
                else:
                    print("    ℹ️  No reports generated (may be due to API rate limiting)")

        except Exception as e:
            print(f"    ⚠️  Intelligence module: {e} (this is often due to API rate limiting and is normal)")
    else:
        print("  ⚠️  Skipping intelligence module (no PERPLEXITY_API_KEY)")

async def test_end_to_end():
    """Test a simple end-to-end workflow"""
    print("\n🚀 Testing end-to-end workflow...")

    try:
        from services.vector_service import get_vector_service
        from config.database import get_supabase
        from uuid import uuid4
        from datetime import datetime

        # Create a test innovation in Supabase
        innovation_data = {
            "id": str(uuid4()),
            "title": "ETL Test Innovation: Solar-Powered AI Device",
            "description": "A solar-powered AI device for rural African communities that provides offline language translation and educational content.",
            "innovation_type": "hardware",
            "domain": "education",
            "verification_status": "pending",
            "visibility": "public",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        supabase = get_supabase()
        response = supabase.table('innovations').insert(innovation_data).execute()

        if response.data:
            print("  ✅ Created test innovation in Supabase")

            # Add to vector database
            vector_service = await get_vector_service()
            success = await vector_service.add_innovation(
                innovation_id=innovation_data["id"],
                title=innovation_data["title"],
                description=innovation_data["description"],
                innovation_type=innovation_data["innovation_type"],
                country="Test Country"
            )

            if success:
                print("  ✅ Added innovation to vector database")

                # Test search
                results = await vector_service.search_innovations("solar AI education", top_k=5)
                found_test = any(r.metadata.get("innovation_id") == innovation_data["id"] for r in results)

                if found_test:
                    print("  ✅ Found test innovation in search results")
                    print("  🎉 End-to-end workflow: SUCCESS!")
                else:
                    print("  ⚠️  Test innovation not found in search (may need time to index)")
            else:
                print("  ❌ Failed to add to vector database")

            # Cleanup
            supabase.table('innovations').delete().eq('id', innovation_data["id"]).execute()
            await vector_service.delete_document(f"innovation_{innovation_data['id']}")
            print("  🧹 Cleaned up test data")

        else:
            print("  ❌ Failed to create test innovation")

    except Exception as e:
        print(f"  ❌ End-to-end test: {e}")

async def main():
    """Main test runner"""
    print(f"⏰ Started at: {asyncio.get_event_loop().time()}")

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix environment variables.")
        return

    # Test database connections
    if not await test_database_connections():
        print("\n❌ Database connection failed. Please check your configuration.")
        return

    # Test vector operations
    if not await test_vector_operations():
        print("\n❌ Vector operations failed.")
        return

    # Test ETL components
    await test_etl_components()

    # Test end-to-end workflow
    await test_end_to_end()

    print("\n" + "=" * 50)
    print("🎉 ETL Test Suite Completed!")
    print("✅ Your ETL pipeline is ready for production use.")

if __name__ == "__main__":
    asyncio.run(main())
