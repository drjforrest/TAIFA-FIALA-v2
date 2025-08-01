#!/usr/bin/env python3
"""
Test Academic ETL Pipeline
Standalone script to test ArXiv scraping and data ingestion
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from etl.academic.arxiv_scraper import scrape_arxiv_papers
from loguru import logger


async def test_academic_etl():
    """Test the academic ETL pipeline"""
    logger.info("🚀 Starting Academic ETL Test...")
    
    try:
        # Test with a smaller dataset first
        papers = await scrape_arxiv_papers(days_back=7, max_results=20)
        
        logger.info(f"✅ Successfully scraped {len(papers)} papers")
        
        if papers:
            logger.info("\n📄 Sample Papers Found:")
            for i, paper in enumerate(papers[:3], 1):
                logger.info(f"\n{i}. {paper.title}")
                logger.info(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
                logger.info(f"   Published: {paper.published_date.strftime('%Y-%m-%d')}")
                logger.info(f"   African Score: {paper.african_relevance_score:.2f}")
                logger.info(f"   AI Score: {paper.ai_relevance_score:.2f}")
                logger.info(f"   African Entities: {paper.african_entities}")
                logger.info(f"   Keywords: {paper.keywords}")
                logger.info(f"   URL: {paper.url}")
                logger.info("-" * 80)
        
        # Show statistics
        if papers:
            avg_african_score = sum(p.african_relevance_score for p in papers) / len(papers)
            avg_ai_score = sum(p.ai_relevance_score for p in papers) / len(papers)
            
            logger.info(f"\n📊 Statistics:")
            logger.info(f"   Total Papers: {len(papers)}")
            logger.info(f"   Average African Relevance: {avg_african_score:.3f}")
            logger.info(f"   Average AI Relevance: {avg_ai_score:.3f}")
            
            # Count by categories
            categories = {}
            for paper in papers:
                for cat in paper.categories:
                    categories[cat] = categories.get(cat, 0) + 1
            
            logger.info(f"   Top Categories: {dict(list(sorted(categories.items(), key=lambda x: x[1], reverse=True))[:5])}")
            
            # Count African entities
            all_entities = []
            for paper in papers:
                all_entities.extend(paper.african_entities)
            
            entity_count = {}
            for entity in all_entities:
                entity_count[entity] = entity_count.get(entity, 0) + 1
            
            logger.info(f"   Top African Entities: {dict(list(sorted(entity_count.items(), key=lambda x: x[1], reverse=True))[:5])}")
        
        return papers
        
    except Exception as e:
        logger.error(f"❌ Academic ETL test failed: {e}")
        import traceback
        traceback.print_exc()
        return []


async def test_with_different_parameters():
    """Test with different search parameters"""
    logger.info("\n🔍 Testing with different parameters...")
    
    test_configs = [
        {"days_back": 30, "max_results": 50, "description": "Last 30 days, 50 results"},
        {"days_back": 7, "max_results": 30, "description": "Last 7 days, 30 results"},
        {"days_back": 14, "max_results": 40, "description": "Last 14 days, 40 results"}
    ]
    
    for config in test_configs:
        logger.info(f"\n📋 Testing: {config['description']}")
        try:
            papers = await scrape_arxiv_papers(
                days_back=config['days_back'], 
                max_results=config['max_results']
            )
            logger.info(f"   Found {len(papers)} papers")
            
            if papers:
                high_relevance = [p for p in papers if p.african_relevance_score >= 0.5 and p.ai_relevance_score >= 0.3]
                logger.info(f"   High relevance papers: {len(high_relevance)}")
            
        except Exception as e:
            logger.error(f"   ❌ Failed: {e}")


def show_usage():
    """Show usage instructions"""
    logger.info("""
🎯 TAIFA-FIALA Academic ETL Test

This script tests the ArXiv academic paper scraping pipeline.

Usage:
    python scripts/test_academic_etl.py [--full-test]

Options:
    --full-test    Run comprehensive tests with different parameters

What this script does:
1. Searches ArXiv for African AI research papers
2. Calculates relevance scores for African context and AI content
3. Extracts metadata, authors, and keywords
4. Shows statistics and sample results

Environment Variables (optional):
- Set ARXIV_BASE_URL if you want to use a different ArXiv API endpoint
- Logging level can be controlled via LOG_LEVEL environment variable
    """)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Academic ETL Pipeline")
    parser.add_argument("--full-test", action="store_true", help="Run comprehensive tests")
    parser.add_argument("--help-usage", action="store_true", help="Show detailed usage")
    
    args = parser.parse_args()
    
    if args.help_usage:
        show_usage()
        sys.exit(0)
    
    logger.info("🔬 TAIFA-FIALA Academic ETL Test Starting...")
    
    # Run basic test
    papers = asyncio.run(test_academic_etl())
    
    # Run full test if requested
    if args.full_test and papers:
        asyncio.run(test_with_different_parameters())
    
    logger.info("🏁 Academic ETL test completed!")
    
    if papers:
        logger.info(f"✨ Success! Found {len(papers)} relevant African AI papers")
        logger.info("📝 Next steps:")
        logger.info("   1. Review the paper data above")
        logger.info("   2. Set up your database (.env file)")
        logger.info("   3. Run the full ETL pipeline to store papers")
        logger.info("   4. Integrate with vector database for semantic search")
    else:
        logger.warning("⚠️  No papers found. This could be due to:")
        logger.warning("   - Network connectivity issues")
        logger.warning("   - ArXiv API rate limiting")
        logger.warning("   - Search parameters too restrictive")
        logger.warning("   - Temporary ArXiv service issues")