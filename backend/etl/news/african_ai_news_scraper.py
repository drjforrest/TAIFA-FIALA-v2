"""
African AI News Scraper using Serper.dev for TAIFA-FIALA
News discovery and collection about African AI innovations and developments
with advanced AI-powered relationship analysis and deduplication
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, HttpUrl

from config.settings import settings
from services.serper_service import SerperService
from services.database_service import DatabaseService
from services.deduplication_service import DeduplicationService
from services.advanced_ai_deduplication_service import analyze_articles_with_complex_relationships


class NewsArticle(BaseModel):
    """Pydantic model for news article data"""
    title: str
    url: HttpUrl
    snippet: str
    source: str
    published_date: Optional[datetime] = None
    date_str: Optional[str] = None
    position: int
    african_relevance_score: float = 0.0
    ai_relevance_score: float = 0.0
    innovation_relevance_score: float = 0.0
    african_entities: List[str] = []
    innovation_keywords: List[str] = []


class AfricanAINewsScraper:
    """News scraper for African AI innovations and developments"""
    
    def __init__(self):
        self.serper = SerperService()
        self.db_service = DatabaseService()
        self.dedup_service = DeduplicationService()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def scrape_african_ai_news(self, 
                                   days_back: int = 7,
                                   max_results: int = 50) -> List[NewsArticle]:
        """Scrape recent African AI news articles with advanced relationship analysis"""
        
        logger.info(f"🗞️ Starting African AI news scraping for last {days_back} days...")
        
        # Build comprehensive news search queries
        news_queries = [
            # African AI general news
            "artificial intelligence Africa startup funding",
            "machine learning Africa innovation news",
            "AI Africa technology breakthrough",
            "African artificial intelligence research news",
            
            # Country-specific AI news
            "Nigeria AI startup funding artificial intelligence",
            "Kenya machine learning innovation technology",
            "South Africa AI artificial intelligence startup",
            "Ghana AI technology innovation news",
            "Egypt artificial intelligence startup funding",
            "Morocco AI machine learning innovation",
            
            # Sector-specific African AI news
            "Africa fintech AI artificial intelligence",
            "African healthtech machine learning innovation",
            "Africa agritech AI farming technology",
            "African edtech education AI technology",
            
            # Funding and investment news
            "African AI startup raises funding million",
            "Africa artificial intelligence investment venture capital",
            "African tech startup AI funding round",
            
            # Innovation and breakthrough news
            "African AI innovation breakthrough technology",
            "Africa machine learning research discovery",
            "African artificial intelligence award recognition"
        ]
        
        all_articles = []
        results_per_query = max(3, max_results // len(news_queries))
        
        async with self.serper as serper:
            for i, query in enumerate(news_queries):
                try:
                    logger.info(f"📰 Searching news query {i+1}/{len(news_queries)}: {query[:50]}...")
                    
                    # Search news with date filter
                    search_response = await serper.search_news(
                        query=query,
                        num_results=results_per_query,
                        days_back=days_back
                    )
                    
                    # Convert to NewsArticle objects
                    articles = self._convert_to_news_articles(search_response.results)
                    all_articles.extend(articles)
                    
                    logger.info(f"✅ Found {len(articles)} articles for query {i+1}")
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error with news query '{query}': {e}")
                    continue
        
        # Remove duplicates and score articles
        unique_articles = self._deduplicate_articles(all_articles)
        scored_articles = self._score_and_filter_articles(unique_articles)
        
        # Sort by combined relevance score
        sorted_articles = sorted(
            scored_articles,
            key=lambda a: a.african_relevance_score + a.ai_relevance_score + a.innovation_relevance_score,
            reverse=True
        )
        
        logger.info(f"🎯 Filtered to {len(sorted_articles)} highly relevant articles")
        
        # Apply Advanced AI-powered relationship analysis and deduplication
        if len(sorted_articles) > 1:
            logger.info("🧠 Applying advanced AI relationship analysis and deduplication...")
            
            # Convert NewsArticle objects to dict format for AI analysis
            article_dicts = []
            for article in sorted_articles:
                article_dict = {
                    'title': article.title,
                    'snippet': article.snippet,
                    'source': article.source,
                    'url': str(article.url),
                    'date_str': article.date_str,
                    'published_date': article.published_date.isoformat() if article.published_date else None,
                    'african_relevance_score': article.african_relevance_score,
                    'ai_relevance_score': article.ai_relevance_score,
                    'innovation_relevance_score': article.innovation_relevance_score,
                    'african_entities': article.african_entities,
                    'innovation_keywords': article.innovation_keywords
                }
                article_dicts.append(article_dict)
            
            # Use advanced AI to analyze relationships and cluster
            canonical_articles, relationship_metadata = await analyze_articles_with_complex_relationships(article_dicts)
            
            # Convert back to NewsArticle objects and add relationship metadata
            final_articles = []
            for article_dict in canonical_articles:
                # Find original NewsArticle object
                for orig_article in sorted_articles:
                    if str(orig_article.url) == article_dict['url']:
                        # Add relationship metadata
                        if 'cluster_info' in article_dict:
                            cluster_info = article_dict['cluster_info']
                            orig_article.cluster_info = cluster_info
                            orig_article.cluster_size = cluster_info.get('cluster_size', 1)
                            orig_article.cluster_type = cluster_info.get('cluster_type')
                            orig_article.relationship_summary = cluster_info.get('relationship_summary')
                            orig_article.related_articles = cluster_info.get('related_articles', 0)
                        else:
                            orig_article.cluster_size = 1
                            orig_article.cluster_type = 'standalone'
                            
                        final_articles.append(orig_article)
                        break
            
            # Log relationship insights
            clusters_found = len(relationship_metadata.get('clusters', []))
            standalone_events = relationship_metadata.get('standalone_events', 0)
            total_relationships = relationship_metadata.get('total_relationships', 0)
            
            logger.info(f"🧠 Advanced AI analysis: {len(sorted_articles)} → {len(final_articles)} unique events")
            logger.info(f"🔗 Relationships found: {clusters_found} clusters, {standalone_events} standalone, {total_relationships} total relationships")
            
            # Log cluster details
            for cluster in relationship_metadata.get('clusters', []):
                logger.info(f"📦 {cluster['type'].title()}: {cluster['primary_entity']} ({cluster['event_count']} events) - {cluster['summary']}")
                
        else:
            final_articles = sorted_articles
            logger.info("🧠 Only one article found, skipping relationship analysis")
        
        return final_articles[:max_results]

    def _convert_to_news_articles(self, search_results) -> List[NewsArticle]:
        """Convert Serper search results to NewsArticle objects"""
        articles = []
        
        for result in search_results:
            try:
                # Parse date if available
                published_date = None
                date_str = result.date if hasattr(result, 'date') else None
                
                if date_str:
                    published_date = self._parse_date_string(date_str)
                
                article = NewsArticle(
                    title=result.title,
                    url=result.link,
                    snippet=result.snippet,
                    source=result.source or self._extract_source_from_url(str(result.link)),
                    published_date=published_date,
                    date_str=date_str,
                    position=result.position
                )
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"⚠️ Error converting search result to NewsArticle: {e}")
                continue
                
        return articles

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats from news sources"""
        if not date_str:
            return None
            
        try:
            # Common date patterns
            patterns = [
                r"(\d{1,2}) hours? ago",
                r"(\d{1,2}) days? ago", 
                r"(\d{1,2}) weeks? ago",
                r"(\d{1,2}) months? ago"
            ]
            
            date_str_lower = date_str.lower()
            
            for pattern in patterns:
                match = re.search(pattern, date_str_lower)
                if match:
                    num = int(match.group(1))
                    if "hour" in date_str_lower:
                        return datetime.now() - timedelta(hours=num)
                    elif "day" in date_str_lower:
                        return datetime.now() - timedelta(days=num)
                    elif "week" in date_str_lower:
                        return datetime.now() - timedelta(weeks=num)
                    elif "month" in date_str_lower:
                        return datetime.now() - timedelta(days=num * 30)
            
            # If no relative date found, assume recent
            return datetime.now() - timedelta(days=1)
            
        except Exception:
            return datetime.now() - timedelta(days=1)

    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
                
            # Map known sources
            source_map = {
                'techcrunch.com': 'TechCrunch',
                'venturebeat.com': 'VentureBeat',
                'techpoint.africa': 'Techpoint Africa',
                'disrupt-africa.com': 'Disrupt Africa',
                'techcabal.com': 'TechCabal',
                'ventureburn.com': 'Ventureburn',
                'itnewsafrica.com': 'IT News Africa',
                'bbc.com': 'BBC',
                'reuters.com': 'Reuters',
                'bloomberg.com': 'Bloomberg'
            }
            
            return source_map.get(domain, domain.split('.')[0].title())
            
        except Exception:
            return "Unknown"

    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on URL and title similarity"""
        unique_articles = []
        seen_urls = set()
        seen_titles = set()
        
        for article in articles:
            url = str(article.url).lower()
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower()).strip()
            
            if url not in seen_urls and normalized_title not in seen_titles and len(normalized_title) > 10:
                seen_urls.add(url)
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        logger.info(f"📊 Deduplicated {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles

    def _score_and_filter_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Score articles for African, AI, and innovation relevance"""
        scored_articles = []
        
        for article in articles:
            # Calculate relevance scores
            article.african_relevance_score = self._calculate_african_relevance(article)
            article.ai_relevance_score = self._calculate_ai_relevance(article)
            article.innovation_relevance_score = self._calculate_innovation_relevance(article)
            article.african_entities = self._extract_african_entities(article)
            article.innovation_keywords = self._extract_innovation_keywords(article)
            
            # Filter based on relevance thresholds
            if (article.african_relevance_score >= 0.3 and 
                article.ai_relevance_score >= 0.2 and
                article.innovation_relevance_score >= 0.2):
                scored_articles.append(article)
        
        logger.info(f"🎯 Filtered {len(articles)} -> {len(scored_articles)} relevant articles")
        return scored_articles

    def _calculate_african_relevance(self, article: NewsArticle) -> float:
        """Calculate African relevance score for article"""
        text = f"{article.title} {article.snippet}".lower()
        score = 0.0
        
        # African countries (higher weight)
        for country in settings.AFRICAN_COUNTRIES:
            if country.lower() in text:
                score += 0.4
        
        # African terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'maghreb', 'sahel',
            'east africa', 'west africa', 'north africa', 'southern africa',
            'sub saharan', 'african union', 'afcon', 'african development'
        ]
        
        for term in african_terms:
            if term in text:
                score += 0.3
                
        # African news sources (bonus)
        african_sources = [
            'techpoint africa', 'disrupt africa', 'techcabal', 'ventureburn',
            'it news africa', 'african', 'afrik'
        ]
        
        for source in african_sources:
            if source in article.source.lower():
                score += 0.2
                break
                
        return min(score, 1.0)

    def _calculate_ai_relevance(self, article: NewsArticle) -> float:
        """Calculate AI relevance score for article"""
        text = f"{article.title} {article.snippet}".lower()
        score = 0.0
        
        # High-value AI terms
        high_value_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'ai technology', 'ai-powered'
        ]
        
        for term in high_value_terms:
            if term in text:
                score += 0.4
        
        # Medium-value AI terms
        medium_value_terms = [
            'ai', 'ml', 'algorithm', 'automation', 'chatbot',
            'computer vision', 'nlp', 'data science'
        ]
        
        for term in medium_value_terms:
            if term in text:
                score += 0.2
                
        return min(score, 1.0)

    def _calculate_innovation_relevance(self, article: NewsArticle) -> float:
        """Calculate innovation/startup relevance score"""
        text = f"{article.title} {article.snippet}".lower()
        score = 0.0
        
        # Innovation/startup terms
        innovation_terms = [
            'startup', 'innovation', 'funding', 'raised', 'investment',
            'venture capital', 'series a', 'series b', 'seed funding',
            'breakthrough', 'launch', 'partnership', 'acquisition'
        ]
        
        for term in innovation_terms:
            if term in text:
                if term in ['funding', 'raised', 'investment', 'venture capital']:
                    score += 0.3  # Higher weight for funding news
                else:
                    score += 0.2
                    
        # Tech sector terms
        sector_terms = [
            'fintech', 'healthtech', 'agritech', 'edtech', 'insurtech',
            'logistics', 'e-commerce', 'mobile', 'platform', 'app'
        ]
        
        for term in sector_terms:
            if term in text:
                score += 0.1
                
        return min(score, 1.0)

    def _extract_african_entities(self, article: NewsArticle) -> List[str]:
        """Extract African entities from article text"""
        text = f"{article.title} {article.snippet}".lower()
        found_entities = []
        
        # Check for African countries
        for country in settings.AFRICAN_COUNTRIES:
            if country.lower() in text:
                found_entities.append(country)
        
        # Check for African regions
        african_regions = [
            "Sub-Saharan Africa", "West Africa", "East Africa", 
            "North Africa", "Southern Africa", "Central Africa"
        ]
        
        for region in african_regions:
            if region.lower() in text:
                found_entities.append(region)
        
        return list(set(found_entities))

    def _extract_innovation_keywords(self, article: NewsArticle) -> List[str]:
        """Extract innovation-related keywords from article"""
        text = f"{article.title} {article.snippet}".lower()
        keywords = []
        
        keyword_categories = {
            'funding': ['funding', 'investment', 'raised', 'million', 'venture capital', 'seed', 'series a'],
            'tech': ['ai', 'artificial intelligence', 'machine learning', 'fintech', 'healthtech'],
            'business': ['startup', 'company', 'partnership', 'launch', 'acquisition'],
            'innovation': ['breakthrough', 'innovation', 'technology', 'platform', 'solution']
        }
        
        for category, terms in keyword_categories.items():
            for term in terms:
                if term in text:
                    keywords.append(term.title())
        
        return list(set(keywords))


# Main scraping function
async def scrape_african_ai_news(days_back: int = 7, max_results: int = 50) -> List[NewsArticle]:
    """Main function to scrape African AI news with advanced relationship analysis"""
    async with AfricanAINewsScraper() as scraper:
        articles = await scraper.scrape_african_ai_news(days_back, max_results)
        
        logger.info(f"🎯 Advanced African AI news scraping complete: {len(articles)} unique events found")
        
        # Log relationship insights
        for article in articles:
            if hasattr(article, 'cluster_info'):
                cluster_info = article.cluster_info
                logger.info(f"📰 {article.title[:50]}... - {cluster_info['cluster_type']} cluster (size: {cluster_info['cluster_size']})")
            else:
                logger.info(f"📰 {article.title[:50]}... - standalone event")
        
    return articles


if __name__ == "__main__":
    # Test the enhanced news scraper
    async def test_scraper():
        articles = await scrape_african_ai_news(
            days_back=14,
            max_results=20
        )
        
        print(f"\n🎯 Found {len(articles)} African AI news articles with relationship analysis:")
        print("=" * 80)
        
        for i, article in enumerate(articles[:10], 1):
            print(f"\n{i}. {article.title}")
            print(f"   Source: {article.source}")
            print(f"   Date: {article.date_str}")
            print(f"   Scores - African: {article.african_relevance_score:.2f} | AI: {article.ai_relevance_score:.2f} | Innovation: {article.innovation_relevance_score:.2f}")
            print(f"   Entities: {article.african_entities}")
            print(f"   Keywords: {article.innovation_keywords}")
            
            # Show relationship info if available
            if hasattr(article, 'cluster_info'):
                cluster_info = article.cluster_info
                print(f"   🔗 Cluster: {cluster_info['cluster_type']} (size: {cluster_info['cluster_size']}) - {cluster_info['relationship_summary']}")
                print(f"   📈 Impact: {len(cluster_info.get('total_impact', {}).get('companies_involved', []))} companies involved")
            else:
                print(f"   🔗 Standalone event")
                
            print(f"   URL: {article.url}")
            print("-" * 80)

    asyncio.run(test_scraper())
