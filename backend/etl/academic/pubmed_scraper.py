"""
PubMed Integration for TAIFA-FIALA
Medical and health AI research scraper
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

import aiohttp
import xmltodict
from loguru import logger
from pydantic import BaseModel

from config.settings import settings
from services.database_service import DatabaseService
from services.deduplication_service import DeduplicationService
from utils.etl_deduplication import check_and_handle_publication_duplicates


class PubMedPaper(BaseModel):
    """Pydantic model for PubMed paper data"""
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    publication_date: datetime
    doi: Optional[str] = None
    url: str
    keywords: List[str] = []
    mesh_terms: List[str] = []
    african_relevance_score: float = 0.0
    ai_relevance_score: float = 0.0


class PubMedScraper:
    """PubMed API scraper for African health AI research"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self):
        self.session = None
        
        # Initialize database and deduplication services
        self.db_service = DatabaseService()
        self.dedup_service = DeduplicationService()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_african_health_ai(self, days_back: int = 30, max_results: int = 50) -> List[PubMedPaper]:
        """Search PubMed for African health AI papers"""
        
        # Construct search query targeting African health + AI
        search_terms = [
            "artificial intelligence",
            "machine learning", 
            "deep learning",
            "AI",
            "ML",
            "neural network",
            "computer vision",
            "natural language processing"
        ]
        
        african_terms = [
            "Africa", "African", "Nigeria", "Kenya", "South Africa", 
            "Ghana", "Ethiopia", "Tanzania", "Uganda", "Rwanda",
            "Botswana", "Zambia", "Zimbabwe", "Morocco", "Egypt",
            "Tunisia", "Senegal", "Mali", "Burkina Faso"
        ]
        
        health_terms = [
            "health", "healthcare", "medical", "medicine", "clinical",
            "disease", "diagnosis", "treatment", "public health",
            "epidemiology", "telemedicine", "digital health",
            "mobile health", "mHealth", "eHealth"
        ]
        
        # Build sophisticated query
        ai_query = "(" + " OR ".join([f'"{term}"' for term in search_terms]) + ")"
        africa_query = "(" + " OR ".join([f'"{term}"' for term in african_terms]) + ")"
        health_query = "(" + " OR ".join([f'"{term}"' for term in health_terms]) + ")"
        
        # Combine with date filter
        date_filter = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
        
        full_query = f"{ai_query} AND {africa_query} AND {health_query} AND (\"{date_filter}\"[Date - Publication] : \"3000\"[Date - Publication])"
        
        logger.info(f"Searching PubMed with query: {full_query[:100]}...")
        
        # Search for PMIDs
        pmids = await self._search_pmids(full_query, max_results)
        
        if not pmids:
            logger.info("No PMIDs found")
            return []
            
        logger.info(f"Found {len(pmids)} PMIDs, fetching details...")
        
        # Fetch paper details
        papers = await self._fetch_paper_details(pmids)
        
        # Score for African and AI relevance
        scored_papers = []
        for paper in papers:
            paper.african_relevance_score = self._calculate_african_relevance(paper)
            paper.ai_relevance_score = self._calculate_ai_relevance(paper)
            
            # Only include papers with reasonable relevance
            if paper.african_relevance_score > 0.3 and paper.ai_relevance_score > 0.4:
                scored_papers.append(paper)
        
        # Sort by combined relevance score
        scored_papers.sort(
            key=lambda p: p.african_relevance_score + p.ai_relevance_score, 
            reverse=True
        )
        
        logger.info(f"Filtered to {len(scored_papers)} highly relevant papers")
        return scored_papers

    async def _search_pmids(self, query: str, max_results: int) -> List[str]:
        """Search PubMed for PMIDs"""
        search_url = f"{self.BASE_URL}/esearch.fcgi"
        
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "pub_date",
            "tool": "taifa-fiala",
            "email": "research@taifa-fiala.org"  # Required by PubMed
        }
        
        try:
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("esearchresult", {}).get("idlist", [])
                else:
                    logger.error(f"PubMed search failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []

    async def _fetch_paper_details(self, pmids: List[str]) -> List[PubMedPaper]:
        """Fetch detailed paper information"""
        if not pmids:
            return []
            
        fetch_url = f"{self.BASE_URL}/efetch.fcgi"
        
        # Process in batches to avoid overwhelming the API
        batch_size = 20
        all_papers = []
        
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            
            params = {
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "xml",
                "tool": "taifa-fiala",
                "email": "research@taifa-fiala.org"
            }
            
            try:
                await asyncio.sleep(0.5)  # Respectful rate limiting
                
                async with self.session.get(fetch_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        papers = self._parse_pubmed_xml(xml_content)
                        all_papers.extend(papers)
                    else:
                        logger.error(f"PubMed fetch failed: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching PubMed batch: {e}")
                continue
                
        return all_papers

    def _parse_pubmed_xml(self, xml_content: str) -> List[PubMedPaper]:
        """Parse PubMed XML response"""
        papers = []
        
        try:
            data = xmltodict.parse(xml_content)
            articles = data.get("PubmedArticleSet", {}).get("PubmedArticle", [])
            
            # Handle single article case
            if isinstance(articles, dict):
                articles = [articles]
                
            for article in articles:
                try:
                    paper = self._extract_paper_data(article)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing paper: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            
        return papers

    def _extract_paper_data(self, article: Dict) -> Optional[PubMedPaper]:
        """Extract paper data from PubMed XML structure"""
        try:
            medline_citation = article.get("MedlineCitation", {})
            pubmed_data = article.get("PubmedData", {})
            
            # PMID
            pmid = medline_citation.get("PMID", {}).get("#text", "")
            
            # Article details
            article_data = medline_citation.get("Article", {})
            
            # Title
            title = article_data.get("ArticleTitle", "")
            if isinstance(title, dict):
                title = title.get("#text", "")
                
            # Abstract
            abstract_data = article_data.get("Abstract", {})
            abstract_text = ""
            if abstract_data:
                abstract_parts = abstract_data.get("AbstractText", [])
                if isinstance(abstract_parts, list):
                    abstract_text = " ".join([
                        part.get("#text", "") if isinstance(part, dict) else str(part)
                        for part in abstract_parts
                    ])
                elif isinstance(abstract_parts, dict):
                    abstract_text = abstract_parts.get("#text", "")
                else:
                    abstract_text = str(abstract_parts)
            
            # Authors
            authors = []
            author_list = article_data.get("AuthorList", {}).get("Author", [])
            if isinstance(author_list, dict):
                author_list = [author_list]
                
            for author in author_list:
                if isinstance(author, dict):
                    first_name = author.get("ForeName", "")
                    last_name = author.get("LastName", "")
                    if first_name and last_name:
                        authors.append(f"{first_name} {last_name}")
                    elif last_name:
                        authors.append(last_name)
            
            # Journal
            journal_data = article_data.get("Journal", {})
            journal = journal_data.get("Title", "") or journal_data.get("ISOAbbreviation", "")
            
            # Publication date
            pub_date_data = journal_data.get("JournalIssue", {}).get("PubDate", {})
            pub_date = self._parse_publication_date(pub_date_data)
            
            # DOI
            doi = None
            article_ids = pubmed_data.get("ArticleIdList", {}).get("ArticleId", [])
            if isinstance(article_ids, dict):
                article_ids = [article_ids]
                
            for article_id in article_ids:
                if isinstance(article_id, dict) and article_id.get("@IdType") == "doi":
                    doi = article_id.get("#text")
                    break
            
            # MeSH terms
            mesh_terms = []
            mesh_list = medline_citation.get("MeshHeadingList", {}).get("MeshHeading", [])
            if isinstance(mesh_list, dict):
                mesh_list = [mesh_list]
                
            for mesh in mesh_list:
                if isinstance(mesh, dict):
                    descriptor = mesh.get("DescriptorName", {})
                    if isinstance(descriptor, dict):
                        term = descriptor.get("#text", "")
                        if term:
                            mesh_terms.append(term)
            
            # Keywords
            keywords = []
            keyword_list = medline_citation.get("KeywordList", {}).get("Keyword", [])
            if isinstance(keyword_list, dict):
                keyword_list = [keyword_list]
                
            for keyword in keyword_list:
                if isinstance(keyword, dict):
                    keyword_text = keyword.get("#text", "")
                    if keyword_text:
                        keywords.append(keyword_text)
                elif isinstance(keyword, str):
                    keywords.append(keyword)
            
            # URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            return PubMedPaper(
                pmid=pmid,
                title=title,
                authors=authors,
                abstract=abstract_text,
                journal=journal,
                publication_date=pub_date,
                doi=doi,
                url=url,
                keywords=keywords,
                mesh_terms=mesh_terms
            )
            
        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None

    def _parse_publication_date(self, pub_date_data: Dict) -> datetime:
        """Parse publication date from various PubMed formats"""
        try:
            year = pub_date_data.get("Year", datetime.now().year)
            month = pub_date_data.get("Month", 1)
            day = pub_date_data.get("Day", 1)
            
            # Handle month names
            if isinstance(month, str):
                month_map = {
                    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
                }
                month = month_map.get(month[:3], 1)
            
            return datetime(int(year), int(month), int(day))
            
        except Exception:
            return datetime.now()

    def _calculate_african_relevance(self, paper: PubMedPaper) -> float:
        """Calculate African relevance score"""
        african_keywords = [
            "africa", "african", "nigeria", "kenya", "south africa", "ghana",
            "ethiopia", "tanzania", "uganda", "rwanda", "botswana", "zambia",
            "zimbabwe", "morocco", "egypt", "tunisia", "senegal", "mali",
            "burkina faso", "sub-saharan", "west africa", "east africa",
            "southern africa", "north africa"
        ]
        
        text = f"{paper.title} {paper.abstract}".lower()
        
        score = 0.0
        for keyword in african_keywords:
            if keyword in text:
                score += 0.2
                
        # Boost for specific African countries/regions
        country_mentions = len([k for k in african_keywords if k in text])
        score += min(country_mentions * 0.1, 0.5)
        
        return min(score, 1.0)

    def _calculate_ai_relevance(self, paper: PubMedPaper) -> float:
        """Calculate AI relevance score"""
        ai_keywords = [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "computer vision", "natural language processing",
            "ai", "ml", "nlp", "cnn", "rnn", "lstm", "transformer",
            "classification", "prediction", "algorithm", "automated"
        ]
        
        text = f"{paper.title} {paper.abstract}".lower()
        
        score = 0.0
        for keyword in ai_keywords:
            if keyword in text:
                if keyword in ["artificial intelligence", "machine learning", "deep learning"]:
                    score += 0.3  # High-value terms
                else:
                    score += 0.1
                    
        return min(score, 1.0)
    
    async def _store_papers_in_database(self, papers: List[PubMedPaper]) -> List[Dict[str, Any]]:
        """Store PubMed papers in Supabase database as publications"""
        
        stored_records = []
        
        for paper in papers:
            try:
                # Convert PubMed paper to publication format
                publication_data = {
                    'title': paper.title,
                    'publication_type': 'journal_paper',
                    'publication_date': paper.publication_date,
                    'year': paper.publication_date.year if paper.publication_date else None,
                    'doi': paper.doi,
                    'url': paper.url,
                    'journal': paper.journal,
                    'abstract': paper.abstract,
                    'keywords': paper.keywords,
                    'source': 'pubmed',
                    'source_id': paper.pubmed_id,
                    'african_relevance_score': paper.african_relevance_score,
                    'ai_relevance_score': paper.ai_relevance_score,
                    'african_entities': paper.african_entities,
                    'data_type': 'Academic Paper'
                }
                
                # Store in database with deduplication
                success, stored_record, action = await check_and_handle_publication_duplicates(
                    publication_data,
                    self.db_service,
                    self.dedup_service,
                    action='reject'  # Can be configured: reject, merge, update, link
                )
                
                if success and stored_record:
                    stored_records.append(stored_record)
                    logger.info(f"✅ Stored PubMed paper ({action}): {paper.title[:50]}...")
                elif not success:
                    logger.info(f"ℹ️ PubMed paper handling ({action}): {paper.title[:50]}...")
                    
            except Exception as e:
                logger.error(f"❌ Error storing PubMed paper {paper.title[:50]}: {e}")
                continue
        
        logger.info(f"📊 PubMed database storage complete: {len(stored_records)}/{len(papers)} papers stored")
        return stored_records


# Main scraping function
async def scrape_pubmed_papers(days_back: int = 30, max_results: int = 50) -> List[PubMedPaper]:
    """Main function to scrape PubMed for African health AI papers"""
    async with PubMedScraper() as scraper:
        papers = await scraper.search_african_health_ai(days_back, max_results)
        
        # Store papers in database with deduplication
        if papers:
            stored_papers = await scraper._store_papers_in_database(papers)
            logger.info(f"📊 PubMed database storage complete: {len(stored_papers)}/{len(papers)} papers stored")
        
    logger.info(f"PubMed scraper found {len(papers)} relevant African health AI papers")
    return papers


if __name__ == "__main__":
    # Test the PubMed scraper
    async def test_scraper():
        papers = await scrape_pubmed_papers(days_back=30, max_results=10)
        for paper in papers:
            print(f"Title: {paper.title}")
            print(f"African Score: {paper.african_relevance_score:.2f}")
            print(f"AI Score: {paper.ai_relevance_score:.2f}")
            print("---")

    asyncio.run(test_scraper())
