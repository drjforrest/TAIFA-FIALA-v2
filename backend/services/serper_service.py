"""
Serper.dev Search Service for TAIFA-FIALA
Precision search service for discovering African AI innovations and research
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote

import aiohttp
from loguru import logger
from pydantic import BaseModel, HttpUrl

from config.settings import settings
from services.unified_cache import (
    cache_api_response, get_cached_response, cache_null_response, 
    is_null_cached, DataSource
)


class SearchResult(BaseModel):
    """Individual search result from Serper"""
    title: str
    link: HttpUrl
    snippet: str
    date: Optional[str] = None
    source: Optional[str] = None
    position: int
    type: str = "organic"  # organic, news, academic


class SerperSearchResponse(BaseModel):
    """Response from Serper search API"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    timestamp: datetime
    search_type: str  # web, news, scholar


class SerperService:
    """Service for precision searches using Serper.dev API"""
    
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_web(self, query: str, num_results: int = 20, 
                        country: Optional[str] = None, 
                        date_range: Optional[str] = None) -> SerperSearchResponse:
        """Perform web search using Serper (with caching)"""
        
        # Create cache parameters
        cache_params = {
            'query': query,
            'num_results': num_results,
            'country': country,
            'date_range': date_range,
            'search_type': 'web'
        }
        
        # Check cache first
        try:
            cached_response = await get_cached_response(DataSource.SERPER, cache_params)
            if cached_response:
                logger.info(f"Using cached Serper web search for: {query}")
                return SerperSearchResponse(**cached_response)
        except Exception as e:
            logger.warning(f"Error checking Serper cache: {e}")
        
        # Check if null cached
        try:
            if await is_null_cached(DataSource.SERPER, cache_params):
                logger.info(f"Serper web search cached as null: {query}")
                return SerperSearchResponse(
                    query=query,
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    timestamp=datetime.now(),
                    search_type="web"
                )
        except Exception as e:
            logger.warning(f"Error checking null cache: {e}")
        
        try:
            payload = {
                "q": query,
                "num": min(num_results, 100),  # Serper max is 100
            }
            
            if country:
                payload["gl"] = country.lower()
            
            if date_range:
                payload["tbs"] = f"qdr:{date_range}"  # y=year, m=month, w=week, d=day
            
            async with self.session.post(f"{self.base_url}/search", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    search_response = self.parse_web_results(query, data)
                    
                    # Cache successful response
                    if search_response.results:
                        # Cache for 12 hours if we have results
                        # Convert HttpUrl to string for JSON serialization
                        response_dict = search_response.dict()
                        for result in response_dict['results']:
                            if 'link' in result and hasattr(result['link'], '__str__'):
                                result['link'] = str(result['link'])
                        await cache_api_response(DataSource.SERPER, cache_params, 
                                               response_dict, 12.0)
                        logger.info(f"Cached Serper web search with {len(search_response.results)} results")
                    else:
                        # Cache null result for 6 hours if no results
                        await cache_null_response(DataSource.SERPER, cache_params, 
                                                "no_results", 6.0)
                        logger.info(f"Cached null Serper result for query: {query}")
                    
                    return search_response
                elif response.status == 429:
                    # Rate limited - cache for shorter period
                    await cache_null_response(DataSource.SERPER, cache_params, 
                                            "rate_limited", 0.5)  # 30 minutes
                    logger.error(f"Serper web search rate limited: {response.status}")
                else:
                    # Other API errors - cache for short period
                    await cache_null_response(DataSource.SERPER, cache_params, 
                                            "api_error", 1.0)  # 1 hour
                    logger.error(f"Serper web search error: {response.status}")
                
                return SerperSearchResponse(
                    query=query,
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    timestamp=datetime.now(),
                    search_type="web"
                )
                    
        except aiohttp.ClientError as e:
            # Network errors - cache for short period
            await cache_null_response(DataSource.SERPER, cache_params, 
                                    "network_error", 0.5)  # 30 minutes
            logger.error(f"Serper network error: {e}")
        except Exception as e:
            logger.error(f"Error in web search: {e}")
        
        # Return empty response
        return SerperSearchResponse(
            query=query,
            results=[],
            total_results=0,
            search_time=0.0,
            timestamp=datetime.now(),
            search_type="web"
        )
    
    async def search_news(self, query: str, num_results: int = 20,
                         days_back: int = 30) -> SerperSearchResponse:
        """Perform news search using Serper"""
        try:
            payload = {
                "q": query,
                "num": min(num_results, 100),
                "tbs": f"qdr:d{days_back}"  # Last N days
            }
            
            async with self.session.post(f"{self.base_url}/news", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_news_results(query, data)
                else:
                    logger.error(f"Serper news search error: {response.status}")
                    return SerperSearchResponse(
                        query=query,
                        results=[],
                        total_results=0,
                        search_time=0.0,
                        timestamp=datetime.now(),
                        search_type="news"
                    )
                    
        except Exception as e:
            logger.error(f"Error in news search: {e}")
            return SerperSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                timestamp=datetime.now(),
                search_type="news"
            )
    
    async def search_scholar(self, query: str, num_results: int = 20,
                           year_from: Optional[int] = None) -> SerperSearchResponse:
        """Perform academic search using Serper (Google Scholar)"""
        try:
            payload = {
                "q": query,
                "num": min(num_results, 100)
            }
            
            if year_from:
                payload["as_ylo"] = year_from
            
            async with self.session.post(f"{self.base_url}/scholar", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_scholar_results(query, data)
                else:
                    logger.error(f"Serper scholar search error: {response.status}")
                    return SerperSearchResponse(
                        query=query,
                        results=[],
                        total_results=0,
                        search_time=0.0,
                        timestamp=datetime.now(),
                        search_type="scholar"
                    )
                    
        except Exception as e:
            logger.error(f"Error in scholar search: {e}")
            return SerperSearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                timestamp=datetime.now(),
                search_type="scholar"
            )
    
    def parse_web_results(self, query: str, data: Dict[str, Any]) -> SerperSearchResponse:
        """Parse web search results from Serper response"""
        results = []
        
        if "organic" in data:
            for i, result in enumerate(data["organic"]):
                try:
                    search_result = SearchResult(
                        title=result.get("title", ""),
                        link=result.get("link", ""),
                        snippet=result.get("snippet", ""),
                        date=result.get("date"),
                        source=result.get("source"),
                        position=i + 1,
                        type="organic"
                    )
                    results.append(search_result)
                except Exception as e:
                    logger.warning(f"Error parsing web result: {e}")
                    continue
        
        return SerperSearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time=data.get("searchInformation", {}).get("formattedSearchTime", 0.0),
            timestamp=datetime.now(),
            search_type="web"
        )
    
    def parse_news_results(self, query: str, data: Dict[str, Any]) -> SerperSearchResponse:
        """Parse news search results from Serper response"""
        results = []
        
        if "news" in data:
            for i, result in enumerate(data["news"]):
                try:
                    search_result = SearchResult(
                        title=result.get("title", ""),
                        link=result.get("link", ""),
                        snippet=result.get("snippet", ""),
                        date=result.get("date"),
                        source=result.get("source"),
                        position=i + 1,
                        type="news"
                    )
                    results.append(search_result)
                except Exception as e:
                    logger.warning(f"Error parsing news result: {e}")
                    continue
        
        return SerperSearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time=data.get("searchInformation", {}).get("formattedSearchTime", 0.0),
            timestamp=datetime.now(),
            search_type="news"
        )
    
    def parse_scholar_results(self, query: str, data: Dict[str, Any]) -> SerperSearchResponse:
        """Parse academic search results from Serper response"""
        results = []
        
        if "organic" in data:
            for i, result in enumerate(data["organic"]):
                try:
                    search_result = SearchResult(
                        title=result.get("title", ""),
                        link=result.get("link", ""),
                        snippet=result.get("snippet", ""),
                        date=result.get("publicationInfo", {}).get("summary"),
                        source="Google Scholar",
                        position=i + 1,
                        type="academic"
                    )
                    results.append(search_result)
                except Exception as e:
                    logger.warning(f"Error parsing scholar result: {e}")
                    continue
        
        return SerperSearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time=data.get("searchInformation", {}).get("formattedSearchTime", 0.0),
            timestamp=datetime.now(),
            search_type="scholar"
        )
    
    async def search_african_ai_innovations(self, innovation_type: Optional[str] = None,
                                          country: Optional[str] = None,
                                          num_results: int = 50) -> List[SearchResult]:
        """Search for African AI innovations using targeted queries"""
        logger.info(f"Searching for African AI innovations: type={innovation_type}, country={country}")
        
        # Build search queries
        base_queries = [
            "African AI startups innovations",
            "Africa artificial intelligence companies",
            "machine learning startups Africa",
            "AI innovation Africa technology"
        ]
        
        # Add innovation type specific queries
        if innovation_type:
            type_queries = [
                f"African {innovation_type} AI startups",
                f"{innovation_type} innovations Africa artificial intelligence",
                f"Africa {innovation_type} machine learning companies"
            ]
            base_queries.extend(type_queries)
        
        # Add country specific queries
        if country:
            country_queries = [
                f"{country} AI startups innovations",
                f"artificial intelligence companies {country}",
                f"{country} machine learning technology startups"
            ]
            base_queries.extend(country_queries)
        
        all_results = []
        results_per_query = max(10, num_results // len(base_queries))
        
        for query in base_queries:
            try:
                # Search both web and news
                web_results = await self.search_web(query, results_per_query)
                news_results = await self.search_news(query, results_per_query // 2, days_back=180)
                
                all_results.extend(web_results.results)
                all_results.extend(news_results.results)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error searching for query '{query}': {e}")
                continue
        
        # Remove duplicates and filter results
        unique_results = self.deduplicate_results(all_results)
        filtered_results = self.filter_african_innovation_results(unique_results)
        
        # Sort by relevance
        sorted_results = sorted(filtered_results, key=self.calculate_relevance_score, reverse=True)
        
        return sorted_results[:num_results]
    
    async def search_innovation_funding(self, days_back: int = 30,
                                      min_amount: Optional[float] = None) -> List[SearchResult]:
        """Search for recent African innovation funding announcements"""
        logger.info(f"Searching for innovation funding in last {days_back} days")
        
        funding_queries = [
            "African startups funding raised million",
            "Africa AI startup investment funding",
            "African tech companies funding round",
            "venture capital Africa startups funding",
            "African innovation funding investment news"
        ]
        
        all_results = []
        
        for query in funding_queries:
            try:
                news_results = await self.search_news(query, 20, days_back)
                all_results.extend(news_results.results)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error searching funding query '{query}': {e}")
                continue
        
        # Filter for funding mentions
        funding_results = []
        for result in all_results:
            if self.contains_funding_keywords(result.title + " " + result.snippet):
                funding_results.append(result)
        
        return self.deduplicate_results(funding_results)
    
    async def search_research_papers(self, keywords: List[str], 
                                   year_from: int = 2020) -> List[SearchResult]:
        """Search for African AI research papers"""
        logger.info(f"Searching for research papers with keywords: {keywords}")
        
        all_results = []
        
        for keyword in keywords:
            try:
                # Build academic query
                academic_query = f"{keyword} Africa OR African"
                
                scholar_results = await self.search_scholar(academic_query, 25, year_from)
                all_results.extend(scholar_results.results)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error searching papers for '{keyword}': {e}")
                continue
        
        # Filter for African relevance
        african_papers = []
        for result in all_results:
            if self.has_african_relevance(result.title + " " + result.snippet):
                african_papers.append(result)
        
        return self.deduplicate_results(african_papers)
    
    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if str(result.link) not in seen_urls:
                seen_urls.add(str(result.link))
                unique_results.append(result)
        
        return unique_results
    
    def filter_african_innovation_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter results for African innovation relevance"""
        filtered = []
        
        for result in results:
            text = f"{result.title} {result.snippet}".lower()
            
            # Check for African relevance
            african_score = self.calculate_african_relevance_score(text)
            
            # Check for innovation/tech relevance
            innovation_score = self.calculate_innovation_relevance_score(text)
            
            # Combined relevance threshold
            if african_score >= 0.3 and innovation_score >= 0.2:
                filtered.append(result)
        
        return filtered
    
    def calculate_african_relevance_score(self, text: str) -> float:
        """Calculate African relevance score for text"""
        score = 0.0
        
        # African countries
        for country in settings.AFRICAN_COUNTRIES:
            if country.lower() in text:
                score += 0.4
        
        # African terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'maghreb', 'sahel',
            'east africa', 'west africa', 'north africa', 'southern africa'
        ]
        
        for term in african_terms:
            if term in text:
                score += 0.3
        
        return min(score, 1.0)
    
    def calculate_innovation_relevance_score(self, text: str) -> float:
        """Calculate innovation/tech relevance score for text"""
        score = 0.0
        
        innovation_terms = [
            'startup', 'innovation', 'technology', 'ai', 'artificial intelligence',
            'machine learning', 'fintech', 'healthtech', 'agritech', 'edtech',
            'tech company', 'digital', 'platform', 'app', 'software', 'solution'
        ]
        
        for term in innovation_terms:
            if term in text:
                if term in ['ai', 'artificial intelligence', 'machine learning']:
                    score += 0.3
                elif term in ['startup', 'innovation', 'fintech', 'healthtech']:
                    score += 0.2
                else:
                    score += 0.1
        
        return min(score, 1.0)
    
    def calculate_relevance_score(self, result: SearchResult) -> float:
        """Calculate overall relevance score for ranking"""
        text = f"{result.title} {result.snippet}".lower()
        
        african_score = self.calculate_african_relevance_score(text)
        innovation_score = self.calculate_innovation_relevance_score(text)
        
        # Position penalty (higher position = lower relevance)
        position_factor = max(0.1, 1.0 - (result.position - 1) * 0.05)
        
        return (african_score * 0.4 + innovation_score * 0.4 + position_factor * 0.2)
    
    def contains_funding_keywords(self, text: str) -> bool:
        """Check if text contains funding-related keywords"""
        funding_keywords = [
            'raised', 'funding', 'investment', 'million', 'billion',
            'round', 'series', 'seed', 'venture capital', 'vc',
            'investor', 'invested', 'capital', 'financing'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in funding_keywords)
    
    def has_african_relevance(self, text: str) -> bool:
        """Check if text has African relevance"""
        return self.calculate_african_relevance_score(text.lower()) >= 0.2


async def search_african_innovations(innovation_type: Optional[str] = None,
                                   country: Optional[str] = None,
                                   num_results: int = 50) -> List[SearchResult]:
    """Main function to search for African AI innovations"""
    async with SerperService() as serper:
        return await serper.search_african_ai_innovations(innovation_type, country, num_results)


async def search_funding_news(days_back: int = 30) -> List[SearchResult]:
    """Search for recent funding news"""
    async with SerperService() as serper:
        return await serper.search_innovation_funding(days_back)


async def search_academic_papers(keywords: List[str], year_from: int = 2020) -> List[SearchResult]:
    """Search for academic papers"""
    async with SerperService() as serper:
        return await serper.search_research_papers(keywords, year_from)


if __name__ == "__main__":
    # Test the service
    async def test_serper():
        print("Testing Serper service...")
        
        # Test innovation search
        innovations = await search_african_innovations(
            innovation_type="FinTech",
            country="Nigeria",
            num_results=10
        )
        
        print(f"\nFound {len(innovations)} innovation results:")
        for result in innovations[:3]:
            print(f"- {result.title}")
            print(f"  URL: {result.link}")
            print(f"  Snippet: {result.snippet[:100]}...")
        
        # Test funding search
        funding = await search_funding_news(days_back=60)
        
        print(f"\nFound {len(funding)} funding results:")
        for result in funding[:3]:
            print(f"- {result.title}")
            print(f"  Source: {result.source}")
    
    asyncio.run(test_serper())