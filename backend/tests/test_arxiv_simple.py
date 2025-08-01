#!/usr/bin/env python3
"""
Simple ArXiv Academic Paper Test
Standalone script to test ArXiv scraping without full backend dependencies
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote

import aiohttp
import feedparser
from loguru import logger


# Configuration
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"
AFRICAN_COUNTRIES = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", 
    "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros", 
    "Congo", "Democratic Republic of Congo", "Djibouti", "Egypt", 
    "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", 
    "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", 
    "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", 
    "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", 
    "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", 
    "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", 
    "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
]

AFRICAN_INSTITUTIONS = [
    "University of Cape Town", "University of the Witwatersrand", "Stellenbosch University",
    "University of Pretoria", "Cairo University", "American University in Cairo",
    "University of Nairobi", "Makerere University", "University of Ghana",
    "Addis Ababa University", "Mohammed V University", "University of Lagos",
    "Obafemi Awolowo University", "Covenant University", "Nelson Mandela University"
]

AI_KEYWORDS = [
    "artificial intelligence africa", "machine learning africa", "AI africa",
    "ML africa", "deep learning africa", "natural language processing africa",
    "computer vision africa", "robotics africa", "data science africa",
    "tech innovation africa", "african AI research", "african machine learning"
]


class SimpleArxivScraper:
    """Simplified ArXiv scraper for testing"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def build_search_query(self, keywords: List[str], max_results: int = 50, days_back: int = 30) -> str:
        """Build ArXiv API search query"""
        # Combine keywords with OR
        keyword_query = " OR ".join([f'all:"{kw}"' for kw in keywords])
        
        # Add African country/institution filters
        african_terms = []
        for country in AFRICAN_COUNTRIES[:10]:  # Limit to avoid URL length issues
            african_terms.append(f'all:"{country}"')
        
        for institution in AFRICAN_INSTITUTIONS[:5]:
            african_terms.append(f'all:"{institution}"')
        
        african_query = " OR ".join(african_terms)
        
        # Combine all terms
        full_query = f"({keyword_query}) AND ({african_query})"
        
        # Build URL parameters
        params = {
            'search_query': full_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'lastUpdatedDate',
            'sortOrder': 'descending'
        }
        
        query_string = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
        return f"{ARXIV_BASE_URL}?{query_string}"
    
    async def fetch_papers(self, query_url: str) -> List[Dict[str, Any]]:
        """Fetch papers from ArXiv API"""
        try:
            logger.info(f"Fetching from: {query_url[:100]}...")
            async with self.session.get(query_url) as response:
                if response.status == 200:
                    content = await response.text()
                    return self.parse_arxiv_response(content)
                else:
                    logger.error(f"ArXiv API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching from ArXiv: {e}")
            return []
    
    def parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse ArXiv XML response"""
        papers = []
        
        try:
            # Use feedparser to parse Atom feed
            feed = feedparser.parse(xml_content)
            logger.info(f"Parsing {len(feed.entries)} entries from ArXiv")
            
            for entry in feed.entries:
                try:
                    paper_data = self.extract_paper_data(entry)
                    if paper_data:
                        papers.append(paper_data)
                except Exception as e:
                    logger.error(f"Error parsing paper entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing ArXiv response: {e}")
            
        return papers
    
    def extract_paper_data(self, entry) -> Optional[Dict[str, Any]]:
        """Extract paper data from ArXiv entry"""
        try:
            # Extract basic information
            title = entry.title.replace('\n', ' ').strip()
            abstract = entry.summary.replace('\n', ' ').strip()
            
            # Extract ArXiv ID from URL
            arxiv_id = entry.id.split('/')[-1]
            
            # Extract authors
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors]
            elif hasattr(entry, 'author'):
                authors = [entry.author]
            
            # Extract dates
            published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
            updated_date = datetime.strptime(entry.updated, '%Y-%m-%dT%H:%M:%SZ')
            
            # Extract categories
            categories = []
            if hasattr(entry, 'tags'):
                categories = [tag.term for tag in entry.tags]
            
            # Calculate relevance scores
            african_score, african_entities = self.calculate_african_relevance(title, abstract, authors)
            ai_score = self.calculate_ai_relevance(title, abstract, categories)
            
            # Extract keywords from title and abstract
            keywords = self.extract_keywords(title, abstract)
            
            return {
                'arxiv_id': arxiv_id,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': entry.id,
                'published_date': published_date,
                'updated_date': updated_date,
                'categories': categories,
                'keywords': keywords,
                'african_relevance_score': african_score,
                'african_entities': african_entities,
                'ai_relevance_score': ai_score
            }
            
        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None
    
    def calculate_african_relevance(self, title: str, abstract: str, authors: List[str]) -> tuple[float, List[str]]:
        """Calculate African relevance score and extract African entities"""
        text = f"{title} {abstract} {' '.join(authors)}".lower()
        
        found_entities = []
        score = 0.0
        
        # Check for African countries
        for country in AFRICAN_COUNTRIES:
            if country.lower() in text:
                found_entities.append(country)
                score += 0.3
        
        # Check for African institutions
        for institution in AFRICAN_INSTITUTIONS:
            if institution.lower() in text:
                found_entities.append(institution)
                score += 0.4
        
        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'sahel', 'maghreb',
            'east africa', 'west africa', 'north africa', 'southern africa'
        ]
        
        for term in african_terms:
            if term in text:
                score += 0.2
                found_entities.append(term.title())
        
        return min(score, 1.0), list(set(found_entities))
    
    def calculate_ai_relevance(self, title: str, abstract: str, categories: List[str]) -> float:
        """Calculate AI relevance score"""
        text = f"{title} {abstract}".lower()
        
        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'nlp', 'ai', 'ml', 'dl', 'cnn', 'rnn', 'lstm', 'transformer',
            'reinforcement learning', 'supervised learning', 'unsupervised learning',
            'classification', 'regression', 'clustering', 'recommendation system',
            'data mining', 'big data', 'predictive analytics', 'automation',
            'robotics', 'expert system', 'knowledge representation'
        ]
        
        score = 0.0
        for term in ai_terms:
            if term in text:
                if term in ['artificial intelligence', 'machine learning', 'deep learning']:
                    score += 0.3  # High-value terms
                elif term in ['ai', 'ml', 'dl']:
                    score += 0.2  # Common abbreviations
                else:
                    score += 0.1  # Other AI terms
        
        # Check categories
        ai_categories = ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.RO', 'stat.ML']
        for cat in categories:
            if cat in ai_categories:
                score += 0.4
        
        return min(score, 1.0)
    
    def extract_keywords(self, title: str, abstract: str) -> List[str]:
        """Extract keywords from title and abstract"""
        text = f"{title} {abstract}".lower()
        
        # Simple keyword extraction based on AI and African terms
        keywords = []
        
        # AI keywords
        ai_keywords = [
            'machine learning', 'deep learning', 'neural network', 'computer vision',
            'natural language processing', 'reinforcement learning', 'classification',
            'regression', 'clustering', 'recommendation', 'automation', 'robotics'
        ]
        
        for keyword in ai_keywords:
            if keyword in text:
                keywords.append(keyword.title())
        
        # Domain-specific keywords
        domain_keywords = [
            'healthcare', 'agriculture', 'finance', 'education', 'transportation',
            'energy', 'environment', 'security', 'governance', 'development'
        ]
        
        for keyword in domain_keywords:
            if keyword in text:
                keywords.append(keyword.title())
        
        return list(set(keywords))
    
    async def scrape_recent_papers(self, days_back: int = 7, max_results: int = 50) -> List[Dict[str, Any]]:
        """Scrape recent papers related to African AI research"""
        logger.info(f"Starting ArXiv scrape for last {days_back} days...")
        
        papers = []
        
        # Search with different keyword combinations
        keyword_groups = [
            AI_KEYWORDS[:3],  # General AI terms
            ['healthcare AI africa', 'medical AI africa'],  # HealthTech
            ['agriculture AI africa', 'farming AI africa'],  # AgriTech
            ['financial AI africa', 'fintech africa'],  # FinTech
        ]
        
        for keywords in keyword_groups:
            try:
                query_url = self.build_search_query(keywords, max_results // len(keyword_groups), days_back)
                paper_data = await self.fetch_papers(query_url)
                
                for data in paper_data:
                    # Filter papers with minimum relevance scores
                    if (data['african_relevance_score'] >= 0.3 and 
                        data['ai_relevance_score'] >= 0.2):
                        papers.append(data)
                
                # Add delay between requests to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in keyword group search: {e}")
                continue
        
        # Remove duplicates based on arxiv_id
        unique_papers = {}
        for paper in papers:
            if paper['arxiv_id'] not in unique_papers:
                unique_papers[paper['arxiv_id']] = paper
        
        result_papers = list(unique_papers.values())
        logger.info(f"Found {len(result_papers)} unique relevant papers")
        
        return result_papers


async def test_arxiv_scraping():
    """Test ArXiv scraping"""
    logger.info("🚀 Starting ArXiv Academic ETL Test...")
    
    async with SimpleArxivScraper() as scraper:
        papers = await scraper.scrape_recent_papers(days_back=30, max_results=100)
        
        logger.info(f"✅ Successfully scraped {len(papers)} papers")
        
        if papers:
            logger.info("\n📄 Sample Papers Found:")
            for i, paper in enumerate(papers[:5], 1):
                logger.info(f"\n{i}. {paper['title']}")
                logger.info(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                logger.info(f"   Published: {paper['published_date'].strftime('%Y-%m-%d')}")
                logger.info(f"   African Score: {paper['african_relevance_score']:.2f}")
                logger.info(f"   AI Score: {paper['ai_relevance_score']:.2f}")
                logger.info(f"   African Entities: {paper['african_entities']}")
                logger.info(f"   Keywords: {paper['keywords']}")
                logger.info(f"   URL: {paper['url']}")
                logger.info(f"   Abstract: {paper['abstract'][:200]}...")
                logger.info("-" * 80)
        
        # Show statistics
        if papers:
            avg_african_score = sum(p['african_relevance_score'] for p in papers) / len(papers)
            avg_ai_score = sum(p['ai_relevance_score'] for p in papers) / len(papers)
            
            logger.info(f"\n📊 Statistics:")
            logger.info(f"   Total Papers: {len(papers)}")
            logger.info(f"   Average African Relevance: {avg_african_score:.3f}")
            logger.info(f"   Average AI Relevance: {avg_ai_score:.3f}")
            
            # Count by categories
            categories = {}
            for paper in papers:
                for cat in paper['categories']:
                    categories[cat] = categories.get(cat, 0) + 1
            
            logger.info(f"   Top Categories: {dict(list(sorted(categories.items(), key=lambda x: x[1], reverse=True))[:5])}")
            
            # Count African entities
            all_entities = []
            for paper in papers:
                all_entities.extend(paper['african_entities'])
            
            entity_count = {}
            for entity in all_entities:
                entity_count[entity] = entity_count.get(entity, 0) + 1
            
            logger.info(f"   Top African Entities: {dict(list(sorted(entity_count.items(), key=lambda x: x[1], reverse=True))[:5])}")
        
        return papers


if __name__ == "__main__":
    logger.info("🔬 TAIFA-FIALA Academic ETL Test Starting...")
    
    papers = asyncio.run(test_arxiv_scraping())
    
    logger.info("🏁 Academic ETL test completed!")
    
    if papers:
        logger.info(f"✨ Success! Found {len(papers)} relevant African AI papers")
        logger.info("📝 Next steps:")
        logger.info("   1. Review the paper data above")
        logger.info("   2. Set up database to store papers")
        logger.info("   3. Run the full ETL pipeline")
        logger.info("   4. Integrate with vector database for semantic search")
    else:
        logger.warning("⚠️  No papers found. This could be due to:")
        logger.warning("   - Network connectivity issues") 
        logger.warning("   - ArXiv API rate limiting")
        logger.warning("   - Search parameters too restrictive")