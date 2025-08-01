"""
RSS Article Monitor for TAIFA-FIALA
Community monitoring pipeline for African tech news and innovation stories
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from loguru import logger
from pydantic import BaseModel, HttpUrl

from config.settings import settings


class NewsArticle(BaseModel):
    """Pydantic model for news article data"""
    title: str
    content: Optional[str] = None
    url: HttpUrl
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    source: str
    summary: Optional[str] = None
    tags: List[str] = []
    
    # AI Analysis Results
    innovation_mentions: List[Dict[str, Any]] = []
    ai_relevance_score: float = 0.0
    african_relevance_score: float = 0.0
    innovation_type: Optional[str] = None
    mentioned_companies: List[str] = []
    mentioned_countries: List[str] = []
    funding_mentions: List[Dict[str, Any]] = []


class RSSMonitor:
    """RSS feed monitor for African tech news"""
    
    def __init__(self):
        self.rss_feeds = settings.rss_feeds
        self.session = None
        self.african_countries = set(settings.AFRICAN_COUNTRIES)
        self.innovation_types = {
            'healthtech', 'agritech', 'fintech', 'edtech', 'cleantech',
            'logistics', 'e-government', 'media', 'security', 'ai', 'ml'
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.CRAWL4AI_TIMEOUT),
            headers={
                'User-Agent': 'TAIFA-FIALA RSS Monitor/1.0 (Research Bot)'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_rss_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        try:
            async with self.session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    return self.parse_rss_feed(content, feed_url)
                else:
                    logger.error(f"RSS fetch error for {feed_url}: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []
    
    def parse_rss_feed(self, xml_content: str, feed_url: str) -> List[Dict[str, Any]]:
        """Parse RSS feed XML content"""
        articles = []
        
        try:
            feed = feedparser.parse(xml_content)
            source_name = self.extract_source_name(feed_url)
            
            logger.info(f"Parsing {len(feed.entries)} entries from {source_name}")
            
            for entry in feed.entries:
                try:
                    article_data = self.extract_article_data(entry, source_name)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    logger.error(f"Error parsing article entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
            
        return articles
    
    def extract_source_name(self, feed_url: str) -> str:
        """Extract source name from feed URL"""
        domain = urlparse(feed_url).netloc
        if 'techcabal' in domain:
            return 'TechCabal'
        elif 'ventureburn' in domain:
            return 'Ventureburn'
        elif 'disrupt-africa' in domain:
            return 'Disrupt Africa'
        elif 'africanbusinesscentral' in domain:
            return 'African Business Central'
        elif 'itnewsafrica' in domain:
            return 'IT News Africa'
        else:
            return domain.replace('www.', '').title()
    
    def extract_article_data(self, entry, source_name: str) -> Optional[Dict[str, Any]]:
        """Extract article data from RSS entry"""
        try:
            title = entry.title.strip()
            url = entry.link
            
            # Extract published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6])
            
            # Extract author
            author = None
            if hasattr(entry, 'author'):
                author = entry.author
            elif hasattr(entry, 'authors') and entry.authors:
                author = entry.authors[0].get('name', '')
            
            # Extract summary/description
            summary = None
            if hasattr(entry, 'summary'):
                summary = self.clean_html(entry.summary)
            elif hasattr(entry, 'description'):
                summary = self.clean_html(entry.description)
            
            # Extract tags
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags]
            
            return {
                'title': title,
                'url': url,
                'published_date': published_date,
                'author': author,
                'source': source_name,
                'summary': summary,
                'tags': tags
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None
    
    def clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def fetch_full_article_content(self, article_url: str) -> Optional[str]:
        """Fetch full article content from URL using Crawl4AI approach"""
        try:
            async with self.session.get(article_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self.extract_article_content(html_content)
                else:
                    logger.warning(f"Failed to fetch article content from {article_url}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching article content from {article_url}: {e}")
            return None
    
    def extract_article_content(self, html_content: str) -> str:
        """Extract main article content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to find main content using common selectors
        content_selectors = [
            'article',
            '.entry-content',
            '.post-content',
            '.article-content',
            '.content',
            '#content',
            '.post-body',
            '.article-body',
            'main'
        ]
        
        content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted elements
                for unwanted in element.find_all(['script', 'style', 'nav', 'header', 'footer', '.sidebar']):
                    unwanted.decompose()
                
                content = self.clean_html(str(element))
                if len(content) > 200:  # Ensure we have substantial content
                    break
        
        # Fallback to body if no content found
        if not content or len(content) < 100:
            body = soup.find('body')
            if body:
                content = self.clean_html(str(body))
        
        return content
    
    def analyze_article_relevance(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze article for AI/innovation relevance and African context"""
        title = article_data.get('title', '').lower()
        summary = article_data.get('summary', '').lower()
        content = article_data.get('content', '').lower()
        
        full_text = f"{title} {summary} {content}"
        
        # Calculate AI relevance score
        ai_score = self.calculate_ai_relevance(full_text)
        
        # Calculate African relevance score
        african_score = self.calculate_african_relevance(full_text)
        
        # Extract innovation mentions
        innovation_mentions = self.extract_innovation_mentions(full_text)
        
        # Determine innovation type
        innovation_type = self.determine_innovation_type(full_text)
        
        # Extract company mentions
        companies = self.extract_company_mentions(full_text)
        
        # Extract country mentions
        countries = self.extract_country_mentions(full_text)
        
        # Extract funding mentions  
        funding_mentions = self.extract_funding_mentions(full_text)
        
        return {
            'ai_relevance_score': ai_score,
            'african_relevance_score': african_score,
            'innovation_mentions': innovation_mentions,
            'innovation_type': innovation_type,
            'mentioned_companies': companies,
            'mentioned_countries': countries,
            'funding_mentions': funding_mentions
        }
    
    def calculate_ai_relevance(self, text: str) -> float:
        """Calculate AI/tech relevance score"""
        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'ai', 'ml', 'algorithm', 'automation', 'robotics', 'chatbot',
            'neural network', 'computer vision', 'natural language processing',
            'data science', 'big data', 'analytics', 'blockchain', 'fintech',
            'healthtech', 'agritech', 'edtech', 'cleantech', 'innovation',
            'startup', 'technology', 'digital', 'platform', 'app', 'software',
            'tech', 'iot', 'internet of things', 'cloud computing', 'api'
        ]
        
        score = 0.0
        word_count = len(text.split())
        
        for term in ai_terms:
            count = text.count(term)
            if count > 0:
                if term in ['artificial intelligence', 'machine learning', 'blockchain']:
                    score += count * 0.3
                elif term in ['ai', 'ml', 'fintech', 'healthtech', 'innovation']:
                    score += count * 0.2
                else:
                    score += count * 0.1
        
        # Normalize by text length
        if word_count > 0:
            score = score / (word_count / 100)  # per 100 words
        
        return min(score, 1.0)
    
    def calculate_african_relevance(self, text: str) -> float:
        """Calculate African relevance score"""
        score = 0.0
        
        # Check for African countries
        for country in self.african_countries:
            if country.lower() in text:
                score += 0.2
        
        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'maghreb', 'sahel',
            'east africa', 'west africa', 'north africa', 'southern africa'
        ]
        
        for term in african_terms:
            if term in text:
                score += 0.3
        
        return min(score, 1.0)
    
    def extract_innovation_mentions(self, text: str) -> List[Dict[str, Any]]:
        """Extract specific innovation mentions from text"""
        innovations = []
        
        # Pattern to find innovation descriptions
        patterns = [
            r'(\w+(?:\s+\w+){0,3})\s+(?:startup|company|platform|app|solution|innovation)',
            r'(?:launched|announced|developed|created)\s+(\w+(?:\s+\w+){0,3})',
            r'(\w+(?:\s+\w+){0,3})\s+(?:uses|leverages|employs)\s+(?:ai|ml|artificial intelligence)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                innovation_name = match.group(1).strip()
                if len(innovation_name) > 2 and innovation_name.lower() not in ['the', 'and', 'for']:
                    innovations.append({
                        'name': innovation_name,
                        'context': match.group(0)
                    })
        
        return innovations[:5]  # Limit to top 5
    
    def determine_innovation_type(self, text: str) -> Optional[str]:
        """Determine the type of innovation mentioned"""
        type_keywords = {
            'healthtech': ['health', 'medical', 'hospital', 'doctor', 'patient', 'diagnosis'],
            'fintech': ['financial', 'banking', 'payment', 'money', 'loan', 'credit'],
            'agritech': ['agriculture', 'farming', 'crop', 'farmer', 'agricultural'],
            'edtech': ['education', 'learning', 'school', 'student', 'educational'],
            'cleantech': ['energy', 'solar', 'renewable', 'environmental', 'clean'],
            'logistics': ['transport', 'delivery', 'logistics', 'shipping', 'supply chain'],
            'ecommerce': ['ecommerce', 'online shopping', 'marketplace', 'retail']
        }
        
        scores = {}
        for innovation_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[innovation_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def extract_company_mentions(self, text: str) -> List[str]:
        """Extract company/startup mentions"""
        # Simple pattern matching for company names
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:startup|company|corp|inc|ltd)',
            r'(?:startup|company)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        companies = set()
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                company = match.group(1).strip()
                if len(company) > 2:
                    companies.add(company)
        
        return list(companies)[:10]
    
    def extract_country_mentions(self, text: str) -> List[str]:
        """Extract African country mentions"""
        mentioned_countries = []
        for country in self.african_countries:
            if country.lower() in text:
                mentioned_countries.append(country)
        
        return mentioned_countries
    
    def extract_funding_mentions(self, text: str) -> List[Dict[str, Any]]:
        """Extract funding/investment mentions"""
        funding_patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(million|billion|k|thousand)',
            r'(\d+(?:\.\d+)?)\s*(million|billion)\s*(?:dollars|usd|\$)',
            r'raised\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|thousand|k)',
            r'funding\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|thousand|k)',
            r'investment\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|thousand|k)'
        ]
        
        funding_mentions = []
        for pattern in funding_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.group(1))
                    unit = match.group(2).lower()
                    
                    # Convert to standard format
                    if unit in ['billion', 'b']:
                        amount *= 1000000000
                    elif unit in ['million', 'm']:
                        amount *= 1000000
                    elif unit in ['thousand', 'k']:
                        amount *= 1000
                    
                    funding_mentions.append({
                        'amount': amount,
                        'formatted_amount': match.group(0),
                        'context': text[max(0, match.start()-50):match.end()+50]
                    })
                except (ValueError, IndexError):
                    continue
        
        return funding_mentions[:5]
    
    async def monitor_feeds(self, hours_back: int = 24) -> List[NewsArticle]:
        """Monitor all RSS feeds for new articles"""
        logger.info(f"Starting RSS monitoring for last {hours_back} hours...")
        
        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Processing feed: {feed_url}")
                articles_data = await self.fetch_rss_feed(feed_url)
                
                for article_data in articles_data:
                    # Filter by date
                    pub_date = article_data.get('published_date')
                    if pub_date and pub_date < cutoff_time:
                        continue
                    
                    # Fetch full content
                    full_content = await self.fetch_full_article_content(article_data['url'])
                    if full_content:
                        article_data['content'] = full_content
                    
                    # Analyze relevance
                    analysis = self.analyze_article_relevance(article_data)
                    article_data.update(analysis)
                    
                    # Filter by relevance scores
                    if (analysis['ai_relevance_score'] >= 0.3 and 
                        analysis['african_relevance_score'] >= 0.2):
                        
                        try:
                            article = NewsArticle(**article_data)
                            all_articles.append(article)
                        except Exception as e:
                            logger.error(f"Error creating NewsArticle model: {e}")
                            continue
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}")
                continue
        
        logger.info(f"Found {len(all_articles)} relevant articles")
        return all_articles


async def monitor_rss_feeds(hours_back: int = 24) -> List[NewsArticle]:
    """Main function to monitor RSS feeds"""
    async with RSSMonitor() as monitor:
        return await monitor.monitor_feeds(hours_back)


if __name__ == "__main__":
    # Test the RSS monitor
    async def test_monitor():
        articles = await monitor_rss_feeds(hours_back=48)
        
        print(f"Found {len(articles)} articles:")
        for article in articles[:5]:  # Show first 5
            print(f"\nTitle: {article.title}")
            print(f"Source: {article.source}")
            print(f"AI Score: {article.ai_relevance_score:.2f}")
            print(f"African Score: {article.african_relevance_score:.2f}")
            print(f"Innovation Type: {article.innovation_type}")
            print(f"Companies: {article.mentioned_companies}")
            print(f"Countries: {article.mentioned_countries}")
    
    asyncio.run(test_monitor())