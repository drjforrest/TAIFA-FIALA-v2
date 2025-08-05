"""
Snowball Sampling Service
========================

Processes citations extracted from Perplexity responses to discover new
publications and innovations through iterative discovery.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

import aiohttp
from loguru import logger

from services.citation_extractor import CitationExtractor
from database.connection import get_db_connection
from services.null_result_cache import (
    check_web_scraping_cache, cache_null_web_scraping, CacheReason, DataSource
)


class SamplingStrategy(Enum):
    """Different snowball sampling strategies"""
    BREADTH_FIRST = "breadth_first"  # Process all current citations before going deeper
    DEPTH_FIRST = "depth_first"      # Follow citation chains deeply
    PRIORITY_BASED = "priority_based"  # Process high-confidence citations first
    BALANCED = "balanced"            # Mix of breadth and depth


@dataclass
class SamplingConfig:
    """Configuration for snowball sampling"""
    max_depth: int = 3
    max_citations_per_batch: int = 20
    min_confidence_threshold: float = 0.7
    strategy: SamplingStrategy = SamplingStrategy.PRIORITY_BASED
    
    # Rate limiting
    delay_between_requests: float = 2.0
    max_requests_per_minute: int = 25
    
    # Quality filters
    require_african_relevance: bool = True
    require_ai_relevance: bool = True
    min_african_indicators: int = 1
    min_ai_indicators: int = 1


class SnowballSampler:
    """Implements snowball sampling for citation discovery"""
    
    def __init__(self, config: SamplingConfig = None):
        self.config = config or SamplingConfig()
        self.db = get_db_connection()
        self.citation_extractor = CitationExtractor(self.db)
        self.processed_urls: Set[str] = set()
        self.sampling_session_id = f"snowball_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def run_sampling_session(self) -> Dict[str, Any]:
        """Run a complete snowball sampling session"""
        
        logger.info(f"Starting snowball sampling session: {self.sampling_session_id}")
        
        session_stats = {
            'session_id': self.sampling_session_id,
            'start_time': datetime.now(),
            'citations_processed': 0,
            'new_discoveries': 0,
            'failed_extractions': 0,
            'depth_reached': 0,
            'discoveries_by_depth': {},
            'quality_scores': []
        }
        
        try:
            # Get initial citation queue
            discovery_queue = await self.citation_extractor.create_snowball_discovery_queue()
            
            if not discovery_queue:
                logger.info("No citations available for snowball sampling")
                return session_stats
            
            logger.info(f"Initial queue size: {len(discovery_queue)} citations")
            
            # Process citations by depth
            current_depth = 0
            current_queue = discovery_queue
            
            while current_queue and current_depth < self.config.max_depth:
                logger.info(f"Processing depth {current_depth} with {len(current_queue)} citations")
                
                depth_results = await self._process_depth_level(current_queue, current_depth)
                
                # Update session stats
                session_stats['citations_processed'] += depth_results['processed_count']
                session_stats['new_discoveries'] += depth_results['discoveries_count']
                session_stats['failed_extractions'] += depth_results['failed_count']
                session_stats['discoveries_by_depth'][current_depth] = depth_results['discoveries_count']
                session_stats['quality_scores'].extend(depth_results['quality_scores'])
                
                # Prepare next depth queue
                current_queue = depth_results['next_depth_queue']
                current_depth += 1
                session_stats['depth_reached'] = current_depth
                
                # Rate limiting between depths
                if current_queue:
                    await asyncio.sleep(self.config.delay_between_requests * 2)
            
            session_stats['end_time'] = datetime.now()
            session_stats['duration'] = (session_stats['end_time'] - session_stats['start_time']).total_seconds()
            session_stats['average_quality'] = sum(session_stats['quality_scores']) / len(session_stats['quality_scores']) if session_stats['quality_scores'] else 0
            
            logger.info(f"Snowball sampling completed: {session_stats['new_discoveries']} new discoveries")
            
            # Store session results
            await self._store_session_results(session_stats)
            
        except Exception as e:
            logger.error(f"Snowball sampling session failed: {e}")
            session_stats['error'] = str(e)
            session_stats['end_time'] = datetime.now()
        
        return session_stats
    
    async def _process_depth_level(self, queue: List[Dict[str, Any]], depth: int) -> Dict[str, Any]:
        """Process all citations at a specific depth level"""
        
        results = {
            'processed_count': 0,
            'discoveries_count': 0,
            'failed_count': 0,
            'quality_scores': [],
            'next_depth_queue': []
        }
        
        # Limit batch size
        batch = queue[:self.config.max_citations_per_batch]
        
        for citation_item in batch:
            try:
                # Process individual citation
                citation_results = await self._process_single_citation(citation_item, depth)
                
                results['processed_count'] += 1
                
                if citation_results['success']:
                    results['discoveries_count'] += citation_results['discoveries_count']
                    results['quality_scores'].append(citation_results['average_quality'])
                    
                    # Add new citations to next depth queue
                    for new_citation in citation_results['new_citations']:
                        if self._should_include_in_next_depth(new_citation):
                            results['next_depth_queue'].append(new_citation)
                else:
                    results['failed_count'] += 1
                
                # Rate limiting
                await asyncio.sleep(self.config.delay_between_requests)
                
            except Exception as e:
                logger.error(f"Failed to process citation {citation_item.get('citation_id')}: {e}")
                results['failed_count'] += 1
        
        return results
    
    async def _process_single_citation(self, citation_item: Dict[str, Any], depth: int) -> Dict[str, Any]:
        """Process a single citation for snowball sampling"""
        
        result = {
            'success': False,
            'discoveries_count': 0,
            'average_quality': 0.0,
            'new_citations': []
        }
        
        citation_url = citation_item.get('url')
        citation_id = citation_item.get('citation_id')
        
        # Skip if already processed
        if citation_url in self.processed_urls:
            logger.debug(f"Skipping already processed URL: {citation_url}")
            return result
        
        # Skip if no URL
        if not citation_url:
            logger.debug(f"Skipping citation without URL: {citation_id}")
            return result
        
        try:
            # Mark as processed
            self.processed_urls.add(citation_url)
            await self.citation_extractor.mark_citation_processed(citation_id)
            
            # Attempt to extract content and find new citations
            content = await self._fetch_citation_content(citation_url)
            
            if content:
                # Extract new citations from this source
                new_citations = await self.citation_extractor.extract_citations_from_response(
                    content, f"snowball_{citation_id}_{depth}"
                )
                
                # Filter by quality
                high_quality_citations = [
                    cit for cit in new_citations 
                    if cit.confidence_score >= self.config.min_confidence_threshold
                    and self._meets_relevance_criteria(cit)
                ]
                
                if high_quality_citations:
                    # Store new citations
                    await self.citation_extractor.store_citations(high_quality_citations)
                    
                    result['success'] = True
                    result['discoveries_count'] = len(high_quality_citations)
                    result['average_quality'] = sum(c.confidence_score for c in high_quality_citations) / len(high_quality_citations)
                    result['new_citations'] = [
                        {
                            'citation_id': cit.id,
                            'title': cit.title,
                            'url': cit.url,
                            'priority_score': cit.confidence_score,
                            'citation_type': cit.citation_type.value,
                            'discovery_method': f'snowball_depth_{depth}'
                        }
                        for cit in high_quality_citations
                    ]
                    
                    logger.info(f"Discovered {len(high_quality_citations)} new citations from {citation_url}")
            
        except Exception as e:
            logger.error(f"Error processing citation {citation_id}: {e}")
        
        return result
    
    async def _fetch_citation_content(self, url: str) -> Optional[str]:
        """Fetch content from citation URL (with cache checking)"""
        
        # First check if this URL is cached as null
        try:
            is_cached, cache_entry = await check_web_scraping_cache(url)
            if is_cached:
                logger.debug(f"URL {url} is cached as null ({cache_entry.reason.value}), skipping fetch")
                return None
        except Exception as e:
            logger.warning(f"Error checking web scraping cache for {url}: {e}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check if content is actually useful
                        if len(content.strip()) < 100:
                            # Cache as null if content is too short
                            await cache_null_web_scraping(url, CacheReason.NO_CONTENT_FOUND,
                                                       {'content_length': len(content)})
                            return None
                            
                        return content[:10000]  # Limit content size
                    elif response.status == 403:
                        # Access denied - cache for longer period
                        await cache_null_web_scraping(url, CacheReason.ACCESS_DENIED,
                                                   {'http_status': response.status})
                        logger.warning(f"Access denied for URL: {url}")
                        return None
                    elif response.status == 429:
                        # Rate limited - cache for shorter period
                        await cache_null_web_scraping(url, CacheReason.RATE_LIMITED,
                                                   {'http_status': response.status})
                        logger.warning(f"Rate limited for URL: {url}")
                        return None
                    else:
                        # Other HTTP errors
                        await cache_null_web_scraping(url, CacheReason.API_ERROR,
                                                   {'http_status': response.status})
                        logger.warning(f"HTTP {response.status} for URL: {url}")
                        return None
                        
        except asyncio.TimeoutError:
            # Cache timeout errors
            await cache_null_web_scraping(url, CacheReason.TIMEOUT,
                                       {'error': 'request_timeout'})
            logger.warning(f"Timeout fetching content from {url}")
            return None
        except Exception as e:
            # Cache other errors
            await cache_null_web_scraping(url, CacheReason.API_ERROR,
                                       {'error': str(e)})
            logger.warning(f"Failed to fetch content from {url}: {e}")
            return None
    
    def _meets_relevance_criteria(self, citation) -> bool:
        """Check if citation meets relevance criteria"""
        
        # Check African relevance
        if self.config.require_african_relevance:
            african_count = len(citation.african_relevance_indicators or [])
            if african_count < self.config.min_african_indicators:
                return False
        
        # Check AI relevance
        if self.config.require_ai_relevance:
            ai_count = len(citation.ai_relevance_indicators or [])
            if ai_count < self.config.min_ai_indicators:
                return False
        
        return True
    
    def _should_include_in_next_depth(self, citation_item: Dict[str, Any]) -> bool:
        """Determine if citation should be included in next depth iteration"""
        
        # Only process high-priority citations in deeper levels
        return citation_item.get('priority_score', 0) >= 0.8
    
    async def _store_session_results(self, session_stats: Dict[str, Any]) -> None:
        """Store snowball sampling session results"""
        
        try:
            query = """
            INSERT INTO snowball_sessions 
            (session_id, start_time, end_time, duration, citations_processed, 
             new_discoveries, failed_extractions, depth_reached, session_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.db.execute(query, (
                session_stats['session_id'],
                session_stats['start_time'],
                session_stats.get('end_time'),
                session_stats.get('duration', 0),
                session_stats['citations_processed'],
                session_stats['new_discoveries'],
                session_stats['failed_extractions'],
                session_stats['depth_reached'],
                json.dumps(session_stats, default=str)
            ))
            
        except Exception as e:
            logger.error(f"Failed to store session results: {e}")


class SnowballScheduler:
    """Scheduler for running snowball sampling at regular intervals"""
    
    def __init__(self, config: SamplingConfig = None):
        self.config = config or SamplingConfig()
        self.is_running = False
    
    async def start_scheduler(self, interval_minutes: int = 60):
        """Start the snowball sampling scheduler"""
        
        logger.info(f"Starting snowball scheduler with {interval_minutes} minute intervals")
        self.is_running = True
        
        while self.is_running:
            try:
                sampler = SnowballSampler(self.config)
                results = await sampler.run_sampling_session()
                
                logger.info(f"Scheduled sampling completed: {results.get('new_discoveries', 0)} discoveries")
                
            except Exception as e:
                logger.error(f"Scheduled sampling failed: {e}")
            
            # Wait for next interval
            await asyncio.sleep(interval_minutes * 60)
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("Snowball scheduler stopped")


# Convenience function for one-off sampling
async def run_snowball_sampling(max_depth: int = 2, 
                               max_citations: int = 10) -> Dict[str, Any]:
    """Run a one-off snowball sampling session"""
    
    config = SamplingConfig(
        max_depth=max_depth,
        max_citations_per_batch=max_citations,
        min_confidence_threshold=0.7
    )
    
    sampler = SnowballSampler(config)
    return await sampler.run_sampling_session()


if __name__ == "__main__":
    # Test snowball sampling
    async def test_snowball():
        print("🔍 Testing snowball sampling...")
        results = await run_snowball_sampling(max_depth=1, max_citations=5)
        print(f"✅ Completed: {results.get('new_discoveries', 0)} new discoveries")
        print(f"   Processed: {results.get('citations_processed', 0)} citations")
        print(f"   Duration: {results.get('duration', 0):.1f} seconds")
    
    asyncio.run(test_snowball())