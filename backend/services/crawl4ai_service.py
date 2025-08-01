"""
Crawl4AI Service for TAIFA-FIALA
Advanced web crawling and content extraction for innovation discovery
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from loguru import logger
from pydantic import BaseModel, HttpUrl

from config.settings import settings


class CrawledInnovation(BaseModel):
    """Extracted innovation data from crawled content"""
    title: str
    description: str
    innovation_type: Optional[str] = None
    organization: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    team_members: List[str] = []
    technology_stack: List[str] = []
    problem_solved: Optional[str] = None
    solution_approach: Optional[str] = None
    impact_metrics: Optional[str] = None
    funding_info: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, str]] = None
    source_url: HttpUrl
    extraction_confidence: float
    metadata: Dict[str, Any] = {}


class CrawlResult(BaseModel):
    """Result of a web crawling operation"""
    url: HttpUrl
    title: str
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    innovations: List[CrawledInnovation] = []
    links: List[str] = []
    images: List[str] = []
    crawl_timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class Crawl4AIService:
    """Service for advanced web crawling using Crawl4AI"""
    
    def __init__(self):
        self.crawler = None
        self.extraction_strategy = None
        self.setup_extraction_strategy()
    
    def setup_extraction_strategy(self):
        """Setup LLM extraction strategy for innovation data"""
        innovation_extraction_prompt = """
        You are an expert at extracting innovation and technology information from web pages.
        
        Please analyze the following web page content and extract information about any African AI/tech innovations mentioned.
        
        For each innovation found, extract:
        1. Title/Name of the innovation
        2. Description (what it does)
        3. Type of innovation (HealthTech, FinTech, AgriTech, EdTech, etc.)
        4. Organization/Company behind it
        5. Location/Country
        6. Team members mentioned
        7. Technology stack used
        8. Problem it solves
        9. Solution approach
        10. Impact metrics or results
        11. Funding information if mentioned
        12. Contact information if available
        
        Return the results as a JSON array where each innovation is an object with these fields:
        {
            "title": "Innovation name",
            "description": "What the innovation does",
            "innovation_type": "HealthTech/FinTech/etc",
            "organization": "Company name",
            "location": "Country/City",
            "team_members": ["Name 1", "Name 2"],
            "technology_stack": ["Python", "ML", "etc"],
            "problem_solved": "Problem description",
            "solution_approach": "How it works",
            "impact_metrics": "Results achieved",
            "funding_info": {"amount": "1M", "currency": "USD", "round": "Seed"},
            "contact_info": {"email": "contact@company.com", "website": "https://..."},
            "extraction_confidence": 0.85
        }
        
        Only extract information that is clearly stated in the content. Do not make assumptions.
        Focus on African innovations or innovations with African connections.
        """
        
        if settings.OPENAI_API_KEY:
            self.extraction_strategy = LLMExtractionStrategy(
                provider="openai",
                api_token=settings.OPENAI_API_KEY,
                instruction=innovation_extraction_prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "innovations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "innovation_type": {"type": "string"},
                                    "organization": {"type": "string"},
                                    "location": {"type": "string"},
                                    "team_members": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "technology_stack": {
                                        "type": "array", 
                                        "items": {"type": "string"}
                                    },
                                    "problem_solved": {"type": "string"},
                                    "solution_approach": {"type": "string"},
                                    "impact_metrics": {"type": "string"},
                                    "funding_info": {"type": "object"},
                                    "contact_info": {"type": "object"},
                                    "extraction_confidence": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.crawler = AsyncWebCrawler(
            verbose=settings.DEBUG,
            max_crawl_depth=2,
            max_concurrent=settings.CRAWL4AI_MAX_CONCURRENT,
            delay_between_requests=1.0,
            user_agent="TAIFA-FIALA Innovation Crawler/1.0 (Research Bot)"
        )
        await self.crawler.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
    
    async def crawl_url(self, url: str, extract_innovations: bool = True) -> CrawlResult:
        """Crawl a single URL and extract innovation data"""
        try:
            logger.info(f"Crawling URL: {url}")
            
            # Basic crawl
            result = await self.crawler.arun(
                url=url,
                word_count_threshold=10,
                extraction_strategy=self.extraction_strategy if extract_innovations else None,
                bypass_cache=False,
                include_links_and_images=True
            )
            
            if not result.success:
                return CrawlResult(
                    url=url,
                    title="",
                    content="",
                    crawl_timestamp=datetime.now(),
                    success=False,
                    error_message=result.error_message
                )
            
            # Parse extracted innovations
            innovations = []
            if extract_innovations and result.extracted_content:
                try:
                    extracted_data = json.loads(result.extracted_content)
                    if "innovations" in extracted_data:
                        for innovation_data in extracted_data["innovations"]:
                            try:
                                innovation = CrawledInnovation(
                                    **innovation_data,
                                    source_url=url
                                )
                                innovations.append(innovation)
                            except Exception as e:
                                logger.warning(f"Error parsing innovation data: {e}")
                                continue
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing extracted JSON: {e}")
            
            # Extract links and images
            links = []
            images = []
            
            if hasattr(result, 'links'):
                links = [urljoin(url, link) for link in result.links.get('internal', [])]
                links.extend([link for link in result.links.get('external', [])])
            
            if hasattr(result, 'images'):
                images = [urljoin(url, img) for img in result.images]
            
            return CrawlResult(
                url=url,
                title=result.metadata.get('title', ''),
                content=result.cleaned_html or result.markdown or '',
                structured_data=result.metadata,
                innovations=innovations,
                links=links[:20],  # Limit links
                images=images[:10],  # Limit images
                crawl_timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return CrawlResult(
                url=url,
                title="",
                content="",
                crawl_timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    async def crawl_innovation_website(self, website_url: str) -> CrawlResult:
        """Specialized crawling for innovation/startup websites"""
        logger.info(f"Crawling innovation website: {website_url}")
        
        # First crawl the main page
        main_result = await self.crawl_url(website_url, extract_innovations=True)
        
        if not main_result.success:
            return main_result
        
        # Look for additional pages that might contain innovation info
        target_pages = []
        for link in main_result.links[:10]:  # Check first 10 links
            link_lower = link.lower()
            if any(keyword in link_lower for keyword in [
                'about', 'product', 'solution', 'innovation', 'technology',
                'team', 'story', 'mission', 'vision'
            ]):
                target_pages.append(link)
        
        # Crawl additional pages and merge results
        additional_innovations = []
        for page_url in target_pages[:3]:  # Limit to 3 additional pages
            try:
                page_result = await self.crawl_url(page_url, extract_innovations=True)
                if page_result.success:
                    additional_innovations.extend(page_result.innovations)
                    # Merge content
                    main_result.content += f"\n\n--- Content from {page_url} ---\n{page_result.content}"
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"Error crawling additional page {page_url}: {e}")
                continue
        
        # Add additional innovations to main result
        main_result.innovations.extend(additional_innovations)
        
        return main_result
    
    async def crawl_innovation_batch(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl multiple innovation websites in batch"""
        logger.info(f"Crawling {len(urls)} websites in batch...")
        
        results = []
        semaphore = asyncio.Semaphore(settings.CRAWL4AI_MAX_CONCURRENT)
        
        async def crawl_with_semaphore(url: str):
            async with semaphore:
                return await self.crawl_innovation_website(url)
        
        # Create tasks for concurrent crawling
        tasks = [crawl_with_semaphore(url) for url in urls]
        
        # Execute with progress tracking
        completed = 0
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
                completed += 1
                
                if completed % 5 == 0:
                    logger.info(f"Completed {completed}/{len(urls)} crawls...")
                    
            except Exception as e:
                logger.error(f"Batch crawl task failed: {e}")
                continue
        
        logger.info(f"Batch crawl completed: {len(results)} results")
        return results
    
    def filter_african_innovations(self, crawl_results: List[CrawlResult]) -> List[CrawledInnovation]:
        """Filter and score innovations for African relevance"""
        african_innovations = []
        
        for result in crawl_results:
            for innovation in result.innovations:
                african_score = self.calculate_african_relevance(innovation)
                
                if african_score >= 0.3:  # Minimum African relevance threshold
                    innovation.metadata['african_relevance_score'] = african_score
                    african_innovations.append(innovation)
        
        # Sort by relevance and confidence
        african_innovations.sort(
            key=lambda x: (
                x.metadata.get('african_relevance_score', 0) * 0.6 + 
                x.extraction_confidence * 0.4
            ),
            reverse=True
        )
        
        return african_innovations
    
    def calculate_african_relevance(self, innovation: CrawledInnovation) -> float:
        """Calculate African relevance score for an innovation"""
        score = 0.0
        
        text_fields = [
            innovation.title,
            innovation.description,
            innovation.organization or "",
            innovation.location or "",
            innovation.problem_solved or "",
            innovation.solution_approach or ""
        ]
        
        full_text = " ".join(text_fields).lower()
        
        # Check for African countries
        african_countries = set(settings.AFRICAN_COUNTRIES)
        for country in african_countries:
            if country.lower() in full_text:
                score += 0.4
        
        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'maghreb', 'sahel',
            'east africa', 'west africa', 'north africa', 'southern africa'
        ]
        
        for term in african_terms:
            if term in full_text:
                score += 0.3
        
        # Check for African institutions
        african_institutions = set(settings.AFRICAN_INSTITUTIONS)
        for institution in african_institutions:
            if institution.lower() in full_text:
                score += 0.2
        
        # Location-based scoring
        if innovation.location:
            location_lower = innovation.location.lower()
            for country in african_countries:
                if country.lower() in location_lower:
                    score += 0.5
                    break
        
        return min(score, 1.0)


async def crawl_innovation_websites(urls: List[str]) -> List[CrawledInnovation]:
    """Main function to crawl innovation websites and extract data"""
    async with Crawl4AIService() as crawler:
        crawl_results = await crawler.crawl_innovation_batch(urls)
        return crawler.filter_african_innovations(crawl_results)


async def crawl_single_website(url: str) -> CrawlResult:
    """Crawl a single website for innovation data"""
    async with Crawl4AIService() as crawler:
        return await crawler.crawl_innovation_website(url)


if __name__ == "__main__":
    # Test the crawler
    async def test_crawler():
        test_urls = [
            "https://www.paystack.com",
            "https://www.flutterwave.com", 
            "https://andela.com"
        ]
        
        innovations = await crawl_innovation_websites(test_urls)
        
        print(f"Found {len(innovations)} innovations:")
        for innovation in innovations[:3]:
            print(f"\nTitle: {innovation.title}")
            print(f"Organization: {innovation.organization}")
            print(f"Type: {innovation.innovation_type}")
            print(f"Location: {innovation.location}")
            print(f"Confidence: {innovation.extraction_confidence:.2f}")
            print(f"African Relevance: {innovation.metadata.get('african_relevance_score', 0):.2f}")
    
    asyncio.run(test_crawler())