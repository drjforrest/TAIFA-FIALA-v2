#!/usr/bin/env python3
"""
Extended ArXiv Academic Paper Test
More comprehensive search with relaxed parameters to find more African AI papers
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


class ExtendedArxivScraper:
    """Extended ArXiv scraper with broader search parameters"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def build_search_queries(self, max_results: int = 200, days_back: int = 365) -> List[str]:
        """Build multiple search queries to maximize paper discovery"""
        queries = []
        
        # Strategy 1: AI terms + Africa
        ai_terms = [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "computer vision", "natural language processing",
            "data science", "robotics", "automation"
        ]
        
        for ai_term in ai_terms[:4]:  # Limit to avoid too many requests
            query = f'all:"{ai_term}" AND (all:"Africa" OR all:"African")'
            url = f"{ARXIV_BASE_URL}?search_query={quote(query)}&start=0&max_results={max_results//4}&sortBy=lastUpdatedDate&sortOrder=descending"
            queries.append(url)
        
        # Strategy 2: Major African countries + tech terms
        major_countries = ["South Africa", "Nigeria", "Kenya", "Egypt", "Ghana", "Morocco"]
        tech_terms = ["AI", "machine learning", "technology", "innovation"]
        
        for country in major_countries[:3]:
            for tech_term in tech_terms[:2]:
                query = f'all:"{country}" AND all:"{tech_term}"'
                url = f"{ARXIV_BASE_URL}?search_query={quote(query)}&start=0&max_results=25&sortBy=lastUpdatedDate&sortOrder=descending"
                queries.append(url)
        
        # Strategy 3: African universities + CS categories
        universities = ["University of Cape Town", "University of Witwatersrand", "Cairo University"]
        for university in universities:
            query = f'all:"{university}" AND (cat:cs.AI OR cat:cs.LG OR cat:cs.CV OR cat:cs.CL)'
            url = f"{ARXIV_BASE_URL}?search_query={quote(query)}&start=0&max_results=30&sortBy=lastUpdatedDate&sortOrder=descending"
            queries.append(url)
        
        # Strategy 4: Development + AI
        development_terms = [
            "development AND artificial intelligence",
            "healthcare AND machine learning AND Africa", 
            "agriculture AND AI AND developing"
        ]
        
        for dev_term in development_terms:
            query = f'all:"{dev_term}"'
            url = f"{ARXIV_BASE_URL}?search_query={quote(query)}&start=0&max_results=40&sortBy=lastUpdatedDate&sortOrder=descending"
            queries.append(url)
        
        return queries
    
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
            
            # Calculate relevance scores (more lenient)
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
        """Calculate African relevance score (more lenient)"""
        text = f"{title} {abstract} {' '.join(authors)}".lower()
        
        found_entities = []
        score = 0.0
        
        # Check for African countries
        for country in AFRICAN_COUNTRIES:
            if country.lower() in text:
                found_entities.append(country)
                score += 0.2  # Reduced from 0.3
        
        # Check for African institutions
        for institution in AFRICAN_INSTITUTIONS:
            if institution.lower() in text:
                found_entities.append(institution)
                score += 0.3  # Reduced from 0.4
        
        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'sahel', 'maghreb',
            'east africa', 'west africa', 'north africa', 'southern africa',
            'developing country', 'developing countries', 'low resource',
            'resource constrained', 'global south'
        ]
        
        for term in african_terms:
            if term in text:
                score += 0.15  # Reduced from 0.2
                found_entities.append(term.title())
        
        # Check author affiliations more broadly
        for author in authors:
            author_lower = author.lower()
            # Look for African patterns in names or affiliations
            african_name_patterns = ['africa', 'cairo', 'lagos', 'nairobi', 'cape town', 'johannesburg']
            for pattern in african_name_patterns:
                if pattern in author_lower:
                    score += 0.25
                    found_entities.append(f"Author: {pattern.title()}")
        
        return min(score, 1.0), list(set(found_entities))
    
    def calculate_ai_relevance(self, title: str, abstract: str, categories: List[str]) -> float:
        """Calculate AI relevance score (more lenient)"""
        text = f"{title} {abstract}".lower()
        
        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'nlp', 'ai', 'ml', 'dl', 'cnn', 'rnn', 'lstm', 'transformer',
            'reinforcement learning', 'supervised learning', 'unsupervised learning',
            'classification', 'regression', 'clustering', 'recommendation system',
            'data mining', 'big data', 'predictive analytics', 'automation',
            'robotics', 'expert system', 'knowledge representation',
            'algorithm', 'computational', 'statistical', 'predictive',
            'intelligent', 'smart', 'automated', 'learning', 'training',
            'model', 'prediction', 'optimization', 'detection'
        ]
        
        score = 0.0
        for term in ai_terms:
            if term in text:
                if term in ['artificial intelligence', 'machine learning', 'deep learning']:
                    score += 0.25  # Reduced from 0.3
                elif term in ['ai', 'ml', 'dl']:
                    score += 0.15  # Reduced from 0.2
                else:
                    score += 0.05  # Reduced from 0.1
        
        # Check categories (more lenient)
        ai_categories = ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.RO', 'stat.ML', 'cs.IR', 'cs.HC', 'cs.CY']
        for cat in categories:
            if cat in ai_categories:
                score += 0.3
        
        return min(score, 1.0)
    
    def extract_keywords(self, title: str, abstract: str) -> List[str]:
        """Extract keywords from title and abstract"""
        text = f"{title} {abstract}".lower()
        
        keywords = []
        
        # AI keywords
        ai_keywords = [
            'machine learning', 'deep learning', 'neural network', 'computer vision',
            'natural language processing', 'reinforcement learning', 'classification',
            'regression', 'clustering', 'recommendation', 'automation', 'robotics',
            'algorithm', 'prediction', 'optimization', 'detection'
        ]
        
        for keyword in ai_keywords:
            if keyword in text:
                keywords.append(keyword.title())
        
        # Domain-specific keywords
        domain_keywords = [
            'healthcare', 'agriculture', 'finance', 'education', 'transportation',
            'energy', 'environment', 'security', 'governance', 'development',
            'mobile', 'internet', 'social', 'economic', 'public health'
        ]
        
        for keyword in domain_keywords:
            if keyword in text:
                keywords.append(keyword.title())
        
        return list(set(keywords))
    
    async def scrape_papers_extended(self, max_results: int = 300) -> List[Dict[str, Any]]:
        """Extended paper scraping with multiple strategies"""
        logger.info(f"Starting extended ArXiv scrape...")
        
        all_papers = []
        queries = self.build_search_queries(max_results)
        
        logger.info(f"Running {len(queries)} different search queries...")
        
        for i, query_url in enumerate(queries, 1):
            try:
                logger.info(f"Query {i}/{len(queries)}: Searching...")
                papers = await self.fetch_papers(query_url)
                
                # Filter with more lenient criteria
                relevant_papers = []
                for paper in papers:
                    african_score = paper['african_relevance_score']
                    ai_score = paper['ai_relevance_score']
                    
                    # More lenient filtering
                    if (african_score >= 0.15 and ai_score >= 0.1) or \
                       (african_score >= 0.3) or \
                       (ai_score >= 0.4 and african_score >= 0.05):
                        relevant_papers.append(paper)
                
                all_papers.extend(relevant_papers)
                logger.info(f"   Found {len(relevant_papers)} relevant papers")
                
                # Rate limiting
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error in query {i}: {e}")
                continue
        
        # Remove duplicates
        unique_papers = {}
        for paper in all_papers:
            if paper['arxiv_id'] not in unique_papers:
                unique_papers[paper['arxiv_id']] = paper
        
        result_papers = list(unique_papers.values())
        
        # Sort by relevance score
        result_papers.sort(
            key=lambda p: p['african_relevance_score'] * 0.6 + p['ai_relevance_score'] * 0.4,
            reverse=True
        )
        
        logger.info(f"Found {len(result_papers)} unique relevant papers")
        return result_papers


async def test_extended_arxiv():
    """Test extended ArXiv scraping"""
    logger.info("🚀 Starting Extended ArXiv Academic ETL Test...")
    
    async with ExtendedArxivScraper() as scraper:
        papers = await scraper.scrape_papers_extended(max_results=500)
        
        logger.info(f"✅ Successfully scraped {len(papers)} papers")
        
        if papers:
            # Show top papers
            logger.info("\n📄 Top African AI Papers Found:")
            for i, paper in enumerate(papers[:10], 1):
                logger.info(f"\n{i}. {paper['title']}")
                logger.info(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                logger.info(f"   Published: {paper['published_date'].strftime('%Y-%m-%d')}")
                logger.info(f"   African Score: {paper['african_relevance_score']:.2f}")
                logger.info(f"   AI Score: {paper['ai_relevance_score']:.2f}")
                logger.info(f"   African Entities: {paper['african_entities']}")
                logger.info(f"   Keywords: {paper['keywords']}")
                logger.info(f"   Categories: {paper['categories']}")
                logger.info(f"   URL: {paper['url']}")
                logger.info(f"   Abstract: {paper['abstract'][:300]}...")
                logger.info("-" * 100)
        
        # Show comprehensive statistics
        if papers:
            avg_african_score = sum(p['african_relevance_score'] for p in papers) / len(papers)
            avg_ai_score = sum(p['ai_relevance_score'] for p in papers) / len(papers)
            
            # High relevance papers
            high_relevance = [p for p in papers if p['african_relevance_score'] >= 0.5 and p['ai_relevance_score'] >= 0.3]
            
            logger.info(f"\n📊 Comprehensive Statistics:")
            logger.info(f"   Total Papers: {len(papers)}")
            logger.info(f"   High Relevance Papers: {len(high_relevance)}")
            logger.info(f"   Average African Relevance: {avg_african_score:.3f}")
            logger.info(f"   Average AI Relevance: {avg_ai_score:.3f}")
            
            # Year distribution
            years = {}
            for paper in papers:
                year = paper['published_date'].year
                years[year] = years.get(year, 0) + 1
            
            logger.info(f"   Year Distribution: {dict(sorted(years.items(), reverse=True))}")
            
            # Category distribution
            categories = {}
            for paper in papers:
                for cat in paper['categories']:
                    categories[cat] = categories.get(cat, 0) + 1
            
            logger.info(f"   Top Categories: {dict(list(sorted(categories.items(), key=lambda x: x[1], reverse=True))[:10])}")
            
            # African entity distribution
            all_entities = []
            for paper in papers:
                all_entities.extend(paper['african_entities'])
            
            entity_count = {}
            for entity in all_entities:
                entity_count[entity] = entity_count.get(entity, 0) + 1
            
            logger.info(f"   Top African Entities: {dict(list(sorted(entity_count.items(), key=lambda x: x[1], reverse=True))[:10])}")
            
            # Innovation types based on keywords
            innovation_types = {}
            for paper in papers:
                for keyword in paper['keywords']:
                    if keyword.lower() in ['healthcare', 'agriculture', 'finance', 'education', 'transportation']:
                        innovation_types[keyword] = innovation_types.get(keyword, 0) + 1
            
            logger.info(f"   Innovation Domains: {dict(sorted(innovation_types.items(), key=lambda x: x[1], reverse=True))}")
        
        return papers


if __name__ == "__main__":
    logger.info("🔬 TAIFA-FIALA Extended Academic ETL Test Starting...")
    
    papers = asyncio.run(test_extended_arxiv())
    
    logger.info("🏁 Extended Academic ETL test completed!")
    
    if papers:
        logger.info(f"✨ Excellent! Found {len(papers)} relevant African AI papers")
        logger.info("📈 This is a much more comprehensive dataset!")
        logger.info("📝 Next steps:")
        logger.info("   1. Store these papers in the database")
        logger.info("   2. Process them through the vector database")
        logger.info("   3. Set up regular ETL runs")
        logger.info("   4. Connect to the frontend for display")
    else:
        logger.warning("⚠️  No papers found with extended search")