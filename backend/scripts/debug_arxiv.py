#!/usr/bin/env python3
"""
Debug ArXiv Query Generation
Let's see what query is actually being sent to ArXiv
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from etl.academic.arxiv_scraper import ArxivScraper
from loguru import logger


async def debug_query():
    """Debug the ArXiv query generation"""
    logger.info("🔍 Debugging ArXiv query generation...")
    
    try:
        async with ArxivScraper() as scraper:
            # Generate query like the real scraper does
            query_url = scraper.build_search_query(
                keywords=scraper.ai_keywords,
                max_results=100,
                days_back=90
            )
            
            logger.info(f"📡 Generated ArXiv Query URL:")
            logger.info(f"   {query_url}")
            
            # Let's also try a very simple query
            simple_query = f"{scraper.base_url}?search_query=all:africa+AND+all:AI&start=0&max_results=20"
            logger.info(f"\n🎯 Simple Test Query:")
            logger.info(f"   {simple_query}")
            
            # Test both queries
            logger.info(f"\n📊 Testing original query...")
            papers1 = await scraper.fetch_papers(query_url)
            logger.info(f"   Original query found: {len(papers1)} papers")
            
            logger.info(f"\n📊 Testing simple query...")
            papers2 = await scraper.fetch_papers(simple_query)
            logger.info(f"   Simple query found: {len(papers2)} papers")
            
            if papers2:
                logger.info(f"\n📄 Sample from simple query:")
                for i, paper in enumerate(papers2[:2]):
                    logger.info(f"   {i+1}. {paper.get('title', 'No title')}")
            
            return len(papers1), len(papers2)
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0


if __name__ == "__main__":
    logger.info("🔬 ArXiv Query Debug...")
    count1, count2 = asyncio.run(debug_query())
    
    if count1 > 0 or count2 > 0:
        logger.info(f"✅ Query generation working! Original: {count1}, Simple: {count2}")
    else:
        logger.warning("⚠️ Both queries returned 0 results - may need to adjust search strategy")
