#!/usr/bin/env python3
"""
PubMed Medical Research Scraper for TAIFA-FIALA
Focuses on African medical AI research and health technology innovations
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import xml.etree.ElementTree as ET

import aiohttp
from loguru import logger


# Configuration
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_API_KEY = "26bf219be13f649f25bddc444bb85ea17909"  # From your .env

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

MEDICAL_AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "computer vision", "natural language processing",
    "predictive modeling", "clinical decision support", "medical imaging",
    "telemedicine", "mHealth", "digital health", "health informatics",
    "electronic health records", "automated diagnosis", "medical AI"
]


class PubMedScraper:
    """PubMed scraper for African medical AI research"""
    
    def __init__(self):
        self.session = None
        self.api_key = PUBMED_API_KEY
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def build_search_queries(self, max_results: int = 200, days_back: int = 365) -> List[Dict[str, str]]:
        """Build multiple PubMed search queries"""
        queries = []
        
        # Strategy 1: Medical AI + African countries
        major_countries = ["South Africa", "Nigeria", "Kenya", "Egypt", "Ghana", "Ethiopia"]
        medical_ai_terms = [
            "artificial intelligence", "machine learning", "digital health",
            "telemedicine", "medical imaging", "clinical decision support"
        ]
        
        for country in major_countries[:4]:
            for ai_term in medical_ai_terms[:3]:
                query = f'"{ai_term}"[Title/Abstract] AND "{country}"[Affiliation]'
                queries.append({
                    'query': query,
                    'description': f'{ai_term} + {country}'
                })
        
        # Strategy 2: Africa + Health technology
        africa_health_queries = [
            '"artificial intelligence"[Title/Abstract] AND "Africa"[Title/Abstract]',
            '"machine learning"[Title/Abstract] AND "African"[Title/Abstract]',
            '"digital health"[Title/Abstract] AND "Sub-Saharan"[Title/Abstract]',
            '"telemedicine"[Title/Abstract] AND "developing countries"[Title/Abstract] AND "Africa"[Title/Abstract]',
            '"mHealth"[Title/Abstract] AND "African"[Title/Abstract]',
            '"health informatics"[Title/Abstract] AND "low-resource"[Title/Abstract]'
        ]
        
        for query in africa_health_queries:
            queries.append({
                'query': query,
                'description': f'Health tech query: {query[:50]}...'
            })
        
        # Strategy 3: Specific medical conditions + AI + Africa
        medical_conditions = [
            "malaria", "tuberculosis", "HIV", "maternal health", 
            "infectious diseases", "radiology", "pathology"
        ]
        
        for condition in medical_conditions[:4]:
            query = f'"{condition}"[Title/Abstract] AND ("artificial intelligence" OR "machine learning")[Title/Abstract] AND "Africa"[Title/Abstract]'
            queries.append({
                'query': query,
                'description': f'{condition} + AI + Africa'
            })
        
        return queries
    
    async def search_pubmed(self, query: str, max_results: int = 50) -> List[str]:
        """Search PubMed and return PMIDs"""
        try:
            # Build search URL
            search_url = f"{PUBMED_BASE_URL}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'xml',
                'api_key': self.api_key,
                'sort': 'relevance'
            }
            
            # Add date filter for recent papers
            params['reldate'] = 1095  # Last 3 years
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self.parse_search_results(xml_content)
                else:
                    logger.error(f"PubMed search error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def parse_search_results(self, xml_content: str) -> List[str]:
        """Parse PubMed search results to extract PMIDs"""
        try:
            root = ET.fromstring(xml_content)
            pmids = []
            
            id_list = root.find('IdList')
            if id_list is not None:
                for id_elem in id_list.findall('Id'):
                    pmids.append(id_elem.text)
            
            return pmids
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            return []
    
    async def fetch_paper_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed paper information using PMIDs"""
        if not pmids:
            return []
        
        try:
            # Build fetch URL
            fetch_url = f"{PUBMED_BASE_URL}/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml',
                'api_key': self.api_key
            }
            
            async with self.session.get(fetch_url, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self.parse_paper_details(xml_content)
                else:
                    logger.error(f"PubMed fetch error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching paper details: {e}")
            return []
    
    def parse_paper_details(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse detailed paper information from PubMed XML"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    paper_data = self.extract_paper_data(article)
                    if paper_data:
                        papers.append(paper_data)
                except Exception as e:
                    logger.error(f"Error extracting paper data: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing paper details: {e}")
            
        return papers
    
    def extract_paper_data(self, article) -> Optional[Dict[str, Any]]:
        """Extract paper data from PubMed XML article"""
        try:
            # Basic information
            medline_citation = article.find('MedlineCitation')
            if medline_citation is None:
                return None
            
            pmid = medline_citation.find('PMID').text if medline_citation.find('PMID') is not None else ""
            
            # Article details
            article_elem = medline_citation.find('Article')
            if article_elem is None:
                return None
            
            # Title
            title_elem = article_elem.find('ArticleTitle')
            title = title_elem.text if title_elem is not None else ""
            
            # Abstract
            abstract = ""
            abstract_elem = article_elem.find('Abstract')
            if abstract_elem is not None:
                abstract_texts = abstract_elem.findall('.//AbstractText')
                abstract_parts = []
                for abs_text in abstract_texts:
                    if abs_text.text:
                        abstract_parts.append(abs_text.text)
                abstract = " ".join(abstract_parts)
            
            # Authors
            authors = []
            author_list = article_elem.find('AuthorList')
            if author_list is not None:
                for author in author_list.findall('Author'):
                    last_name = author.find('LastName')
                    first_name = author.find('ForeName')
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
            
            # Journal and publication date
            journal_elem = article_elem.find('Journal')
            journal = ""
            pub_date = None
            
            if journal_elem is not None:
                journal_title = journal_elem.find('Title')
                if journal_title is not None:
                    journal = journal_title.text
                
                # Publication date
                journal_issue = journal_elem.find('JournalIssue')
                if journal_issue is not None:
                    pub_date_elem = journal_issue.find('PubDate')
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find('Year')
                        month_elem = pub_date_elem.find('Month')
                        day_elem = pub_date_elem.find('Day')
                        
                        if year_elem is not None:
                            year = int(year_elem.text)
                            month = 1
                            day = 1
                            
                            if month_elem is not None:
                                try:
                                    month = int(month_elem.text)
                                except:
                                    # Handle month names
                                    month_names = {
                                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                                        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                                        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                                    }
                                    month = month_names.get(month_elem.text, 1)
                            
                            if day_elem is not None:
                                try:
                                    day = int(day_elem.text)
                                except:
                                    day = 1
                            
                            pub_date = datetime(year, month, day)
            
            # DOI
            doi = ""
            article_id_list = article_elem.find('ELocationID')
            if article_id_list is not None and article_id_list.get('EIdType') == 'doi':
                doi = article_id_list.text
            
            # Calculate relevance scores
            african_score, african_entities = self.calculate_african_relevance(title, abstract, authors)
            medical_ai_score = self.calculate_medical_ai_relevance(title, abstract, journal)
            
            # Extract keywords
            keywords = self.extract_medical_keywords(title, abstract)
            
            # Build URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            return {
                'pmid': pmid,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'journal': journal,
                'publication_date': pub_date,
                'doi': doi,
                'url': url,
                'african_relevance_score': african_score,
                'african_entities': african_entities,
                'medical_ai_score': medical_ai_score,
                'keywords': keywords
            }
            
        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None
    
    def calculate_african_relevance(self, title: str, abstract: str, authors: List[str]) -> tuple[float, List[str]]:
        """Calculate African relevance score"""
        text = f"{title} {abstract} {' '.join(authors)}".lower()
        
        found_entities = []
        score = 0.0
        
        # Check for African countries
        for country in AFRICAN_COUNTRIES:
            if country.lower() in text:
                found_entities.append(country)
                score += 0.3
        
        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'sahel', 'maghreb',
            'east africa', 'west africa', 'north africa', 'southern africa',
            'developing country', 'developing countries', 'low resource',
            'resource constrained', 'global south', 'low-income countries'
        ]
        
        for term in african_terms:
            if term in text:
                score += 0.2
                found_entities.append(term.title())
        
        # Check for African medical institutions/organizations
        african_medical_terms = [
            'african union', 'who africa', 'african development bank',
            'cape town', 'johannesburg', 'cairo', 'nairobi', 'lagos',
            'university of cape town', 'university of witwatersrand'
        ]
        
        for term in african_medical_terms:
            if term in text:
                score += 0.25
                found_entities.append(term.title())
        
        return min(score, 1.0), list(set(found_entities))
    
    def calculate_medical_ai_relevance(self, title: str, abstract: str, journal: str) -> float:
        """Calculate medical AI relevance score"""
        text = f"{title} {abstract} {journal}".lower()
        
        medical_ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing',
            'predictive modeling', 'clinical decision support', 'medical imaging',
            'telemedicine', 'mhealth', 'digital health', 'health informatics',
            'electronic health records', 'automated diagnosis', 'medical ai',
            'clinical ai', 'diagnostic ai', 'healthcare ai', 'biomedical ai',
            'radiomics', 'pathomics', 'precision medicine', 'personalized medicine'
        ]
        
        score = 0.0
        for term in medical_ai_terms:
            if term in text:
                if term in ['artificial intelligence', 'machine learning', 'deep learning']:
                    score += 0.3
                elif term in ['telemedicine', 'digital health', 'medical ai']:
                    score += 0.25
                elif term in ['clinical decision support', 'medical imaging']:
                    score += 0.2
                else:
                    score += 0.1
        
        # Check for AI-related medical journals
        ai_medical_journals = [
            'artificial intelligence in medicine', 'ieee transactions on biomedical engineering',
            'journal of medical internet research', 'npj digital medicine',
            'nature medicine', 'computer methods and programs in biomedicine'
        ]
        
        for journal_name in ai_medical_journals:
            if journal_name in text:
                score += 0.3
        
        return min(score, 1.0)
    
    def extract_medical_keywords(self, title: str, abstract: str) -> List[str]:
        """Extract medical and AI keywords"""
        text = f"{title} {abstract}".lower()
        
        keywords = []
        
        # Medical AI keywords
        medical_ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'telemedicine', 'digital health',
            'clinical decision support', 'medical imaging', 'predictive modeling'
        ]
        
        for keyword in medical_ai_keywords:
            if keyword in text:
                keywords.append(keyword.title())
        
        # Medical domain keywords
        medical_domains = [
            'radiology', 'pathology', 'cardiology', 'oncology', 'infectious diseases',
            'maternal health', 'child health', 'mental health', 'public health',
            'epidemiology', 'primary care', 'emergency medicine', 'surgery'
        ]
        
        for keyword in medical_domains:
            if keyword in text:
                keywords.append(keyword.title())
        
        # African health priorities
        african_health = [
            'malaria', 'tuberculosis', 'hiv', 'maternal mortality', 'child mortality',
            'malnutrition', 'vaccine', 'immunization', 'neglected tropical diseases'
        ]
        
        for keyword in african_health:
            if keyword in text:
                keywords.append(keyword.title())
        
        return list(set(keywords))
    
    async def scrape_medical_papers(self, max_results: int = 300) -> List[Dict[str, Any]]:
        """Scrape medical papers related to African AI research"""
        logger.info(f"Starting PubMed medical research scrape...")
        
        all_papers = []
        queries = self.build_search_queries(max_results)
        
        logger.info(f"Running {len(queries)} different PubMed queries...")
        
        for i, query_info in enumerate(queries, 1):
            try:
                logger.info(f"Query {i}/{len(queries)}: {query_info['description']}")
                
                # Search for PMIDs
                pmids = await self.search_pubmed(query_info['query'], max_results // len(queries))
                
                if pmids:
                    logger.info(f"   Found {len(pmids)} papers")
                    
                    # Fetch paper details in batches
                    batch_size = 20
                    for j in range(0, len(pmids), batch_size):
                        batch_pmids = pmids[j:j+batch_size]
                        papers = await self.fetch_paper_details(batch_pmids)
                        
                        # Filter relevant papers
                        relevant_papers = []
                        for paper in papers:
                            african_score = paper['african_relevance_score']
                            medical_ai_score = paper['medical_ai_score']
                            
                            # More lenient filtering for medical papers
                            if (african_score >= 0.2 and medical_ai_score >= 0.2) or \
                               (african_score >= 0.4) or \
                               (medical_ai_score >= 0.5 and african_score >= 0.1):
                                relevant_papers.append(paper)
                        
                        all_papers.extend(relevant_papers)
                        logger.info(f"   Batch {j//batch_size + 1}: {len(relevant_papers)} relevant papers")
                        
                        # Rate limiting between batches
                        await asyncio.sleep(1)
                else:
                    logger.info(f"   No papers found")
                
                # Rate limiting between queries
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in query {i}: {e}")
                continue
        
        # Remove duplicates by PMID
        unique_papers = {}
        for paper in all_papers:
            if paper['pmid'] not in unique_papers:
                unique_papers[paper['pmid']] = paper
        
        result_papers = list(unique_papers.values())
        
        # Sort by relevance
        result_papers.sort(
            key=lambda p: p['african_relevance_score'] * 0.5 + p['medical_ai_score'] * 0.5,
            reverse=True
        )
        
        logger.info(f"Found {len(result_papers)} unique relevant medical papers")
        return result_papers


async def test_pubmed_scraping():
    """Test PubMed medical research scraping"""
    logger.info("🏥 Starting PubMed Medical AI Research Test...")
    
    async with PubMedScraper() as scraper:
        papers = await scraper.scrape_medical_papers(max_results=400)
        
        logger.info(f"✅ Successfully scraped {len(papers)} medical papers")
        
        if papers:
            # Show top papers
            logger.info("\n🏥 Top African Medical AI Papers Found:")
            for i, paper in enumerate(papers[:10], 1):
                logger.info(f"\n{i}. {paper['title']}")
                logger.info(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                logger.info(f"   Journal: {paper['journal']}")
                if paper['publication_date']:
                    logger.info(f"   Published: {paper['publication_date'].strftime('%Y-%m-%d')}")
                logger.info(f"   African Score: {paper['african_relevance_score']:.2f}")
                logger.info(f"   Medical AI Score: {paper['medical_ai_score']:.2f}")
                logger.info(f"   African Entities: {paper['african_entities']}")
                logger.info(f"   Keywords: {paper['keywords']}")
                logger.info(f"   PMID: {paper['pmid']}")
                logger.info(f"   URL: {paper['url']}")
                logger.info(f"   Abstract: {paper['abstract'][:300]}...")
                logger.info("-" * 100)
        
        # Comprehensive statistics
        if papers:
            avg_african_score = sum(p['african_relevance_score'] for p in papers) / len(papers)
            avg_medical_score = sum(p['medical_ai_score'] for p in papers) / len(papers)
            
            high_relevance = [p for p in papers if p['african_relevance_score'] >= 0.5 and p['medical_ai_score'] >= 0.4]
            
            logger.info(f"\n🏥 Medical Research Statistics:")
            logger.info(f"   Total Medical Papers: {len(papers)}")
            logger.info(f"   High Relevance Papers: {len(high_relevance)}")
            logger.info(f"   Average African Relevance: {avg_african_score:.3f}")
            logger.info(f"   Average Medical AI Relevance: {avg_medical_score:.3f}")
            
            # Year distribution
            years = {}
            for paper in papers:
                if paper['publication_date']:
                    year = paper['publication_date'].year
                    years[year] = years.get(year, 0) + 1
            
            if years:
                logger.info(f"   Year Distribution: {dict(sorted(years.items(), reverse=True))}")
            
            # African entity distribution
            all_entities = []
            for paper in papers:
                all_entities.extend(paper['african_entities'])
            
            entity_count = {}
            for entity in all_entities:
                entity_count[entity] = entity_count.get(entity, 0) + 1
            
            if entity_count:
                logger.info(f"   Top African Entities: {dict(list(sorted(entity_count.items(), key=lambda x: x[1], reverse=True))[:10])}")
            
            # Medical keywords distribution
            all_keywords = []
            for paper in papers:
                all_keywords.extend(paper['keywords'])
            
            keyword_count = {}
            for keyword in all_keywords:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            
            if keyword_count:
                logger.info(f"   Top Medical Keywords: {dict(list(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))[:10])}")
        
        return papers


if __name__ == "__main__":
    logger.info("🏥 TAIFA-FIALA PubMed Medical AI Research Test Starting...")
    
    papers = asyncio.run(test_pubmed_scraping())
    
    logger.info("🏁 PubMed medical research test completed!")
    
    if papers:
        logger.info(f"✨ Excellent! Found {len(papers)} relevant African medical AI papers")
        logger.info("🏥 This complements our ArXiv dataset with medical research!")
        logger.info("📝 Next steps:")
        logger.info("   1. Combine ArXiv + PubMed datasets")
        logger.info("   2. Store in the database")
        logger.info("   3. Process through vector database")
        logger.info("   4. Set up automated daily ETL runs")
    else:
        logger.warning("⚠️  No medical papers found")