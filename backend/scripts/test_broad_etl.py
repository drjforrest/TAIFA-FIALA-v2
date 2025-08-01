#!/usr/bin/env python3
"""
Quick ETL Test with Broader Parameters
Let's test with more permissive parameters to see if the ETL system works
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from etl.academic.arxiv_scraper import scrape_arxiv_papers
from loguru import logger


async def test_broad_search():
    """Test with broader search parameters"""
    logger.info("🔍 Testing with broader parameters (90 days, 100 results)...")
    
    try:
        # Test with broader time range and more results
        papers = await scrape_arxiv_papers(days_back=90, max_results=100)
        
        logger.info(f"✅ Found {len(papers)} papers")
        
        if papers:
            logger.info("\n📄 Sample Papers Found:")
            for i, paper in enumerate(papers[:5], 1):
                logger.info(f"\n{i}. {paper.title}")
                logger.info(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
                logger.info(f"   Published: {paper.published_date.strftime('%Y-%m-%d')}")
                logger.info(f"   African Score: {paper.african_relevance_score:.2f}")
                logger.info(f"   AI Score: {paper.ai_relevance_score:.2f}")
                logger.info(f"   URL: {paper.url}")
                logger.info("-" * 60)
        
        return papers
        
    except Exception as e:
        logger.error(f"❌ Broad search failed: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    logger.info("🌍 TAIFA-FIALA Broad ETL Test...")
    papers = asyncio.run(test_broad_search())
    
    if papers:
        logger.info(f"🎉 Success! ETL system is working with {len(papers)} papers found")
    else:
        logger.warning("📡 No papers found with broad search - investigating ArXiv connectivity...")
