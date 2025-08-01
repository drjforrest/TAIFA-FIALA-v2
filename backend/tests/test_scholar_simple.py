#!/usr/bin/env python3
"""
Google Scholar Scraper for TAIFA-FIALA using SerpAPI
Third academic source to complement ArXiv and PubMed datasets
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

from serpapi import GoogleSearch
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

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


class GoogleScholarScraper:
    """Google Scholar scraper using SerpAPI for African AI research"""

    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")

    def build_search_queries(self, max_results: int = 200) -> List[Dict[str, str]]:
        """Build multiple Google Scholar search queries"""
        queries = []

        # Strategy 1: AI terms + Africa combinations
        ai_terms = [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "computer vision", "natural language processing",
            "data science", "AI", "ML"
        ]

        africa_terms = ["Africa", "African", "Sub-Saharan Africa"]

        for ai_term in ai_terms[:2]:  # Reduced for testing
            for africa_term in africa_terms[:1]:  # Reduced for testing
                query = f'"{ai_term}" "{africa_term}"'
                queries.append({
                    'query': query,
                    'description': f'{ai_term} + {africa_term}',
                    'num_results': max_results // 8
                })

        # Strategy 2: Major African countries + tech terms
        major_countries = ["South Africa", "Nigeria", "Kenya", "Egypt", "Ghana", "Ethiopia"]
        tech_terms = ["artificial intelligence", "machine learning", "technology innovation"]

        for country in major_countries[:1]:  # Reduced for testing
            for tech_term in tech_terms[:1]:  # Reduced for testing
                query = f'"{tech_term}" "{country}"'
                queries.append({
                    'query': query,
                    'description': f'{tech_term} + {country}',
                    'num_results': max_results // 8
                })

        # Strategy 3: African universities + AI research
        universities = ["University of Cape Town", "University of Witwatersrand", "Cairo University", "University of Nairobi"]

        # Skip universities and development queries for testing
        # Will add back after confirming the core functionality works

        return queries

    def search_google_scholar(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """Search Google Scholar using SerpAPI"""
        try:
            logger.info(f"Searching Google Scholar: {query[:50]}...")

            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": self.api_key,
                "num": min(num_results, 20),  # SerpAPI limit
                "as_ylo": 2020,  # Papers from 2020 onwards
                "scisbd": 1,  # Sort by date
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            if "organic_results" in results:
                papers = []
                for result in results["organic_results"]:
                    paper_data = self.extract_paper_data(result)
                    if paper_data:
                        papers.append(paper_data)

                logger.info(f"   Found {len(papers)} papers from Scholar")
                return papers
            else:
                logger.warning(f"   No organic results found")
                if "error" in results:
                    logger.error(f"   SerpAPI error: {results['error']}")
                return []

        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
            return []

    def extract_paper_data(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract paper data from Google Scholar result"""
        try:
            # Basic information
            title = result.get("title", "").strip()
            if not title:
                return None

            # Extract publication info
            publication_info = result.get("publication_info", {})
            authors = publication_info.get("authors", [])
            if isinstance(authors, str):
                authors = [authors]
            elif isinstance(authors, list):
                # Handle case where authors are dictionaries with name fields
                processed_authors = []
                for author in authors:
                    if isinstance(author, dict):
                        name = author.get("name", "")
                        if name:
                            processed_authors.append(name)
                    elif isinstance(author, str):
                        processed_authors.append(author)
                authors = processed_authors

            # Extract snippet/abstract
            snippet = result.get("snippet", "")

            # Extract publication details
            journal = ""
            year = None

            pub_summary = publication_info.get("summary", "")
            if pub_summary:
                # Try to extract year from publication summary
                year_match = re.search(r'\b(20\d{2})\b', pub_summary)
                if year_match:
                    year = int(year_match.group(1))

                # Extract journal/venue
                parts = pub_summary.split(',')
                if len(parts) > 1:
                    journal = parts[0].strip()

            # Links
            link = result.get("link", "")

            # Resources (PDF links, etc.)
            resources = result.get("resources", [])
            pdf_link = ""
            for resource in resources:
                if resource.get("title", "").lower().find("pdf") != -1:
                    pdf_link = resource.get("link", "")
                    break

            # Citation count
            citation_count = 0
            inline_links = result.get("inline_links", {})
            if "cited_by" in inline_links:
                cited_by = inline_links["cited_by"]
                if "total" in cited_by:
                    citation_count = cited_by["total"]

            # Calculate relevance scores
            african_score, african_entities = self.calculate_african_relevance(title, snippet, authors)
            ai_score = self.calculate_ai_relevance(title, snippet, journal)

            # Extract keywords
            keywords = self.extract_keywords(title, snippet)

            # Publication date
            pub_date = None
            if year:
                try:
                    pub_date = datetime(year, 1, 1)
                except:
                    pass

            return {
                'title': title,
                'authors': authors,
                'abstract': snippet,
                'journal': journal,
                'publication_date': pub_date,
                'year': year,
                'url': link,
                'pdf_url': pdf_link,
                'citation_count': citation_count,
                'source': 'Google Scholar',
                'african_relevance_score': african_score,
                'african_entities': african_entities,
                'ai_relevance_score': ai_score,
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
                score += 0.25

        # Check for African institutions
        for institution in AFRICAN_INSTITUTIONS:
            if institution.lower() in text:
                found_entities.append(institution)
                score += 0.35

        # Check for African-specific terms
        african_terms = [
            'africa', 'african', 'sub-saharan', 'sahel', 'maghreb',
            'east africa', 'west africa', 'north africa', 'southern africa',
            'developing country', 'developing countries', 'low resource',
            'resource constrained', 'global south', 'low-income countries'
        ]

        for term in african_terms:
            if term in text:
                score += 0.15
                found_entities.append(term.title())

        # Check author names for African patterns
        for author in authors:
            author_lower = author.lower()
            african_patterns = ['africa', 'cairo', 'lagos', 'nairobi', 'cape town', 'johannesburg', 'addis']
            for pattern in african_patterns:
                if pattern in author_lower:
                    score += 0.2
                    found_entities.append(f"Author: {pattern.title()}")

        return min(score, 1.0), list(set(found_entities))

    def calculate_ai_relevance(self, title: str, abstract: str, journal: str) -> float:
        """Calculate AI relevance score"""
        text = f"{title} {abstract} {journal}".lower()

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
                    score += 0.3
                elif term in ['ai', 'ml', 'dl']:
                    score += 0.2
                else:
                    score += 0.1

        # Check for AI-related journals/venues
        ai_venues = [
            'artificial intelligence', 'machine learning', 'neural networks',
            'ieee', 'acm', 'aaai', 'nips', 'icml', 'iclr', 'neurips'
        ]

        for venue in ai_venues:
            if venue in text:
                score += 0.25

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
            'mobile', 'internet', 'social', 'economic', 'public health',
            'climate', 'sustainable', 'innovation', 'technology'
        ]

        for keyword in domain_keywords:
            if keyword in text:
                keywords.append(keyword.title())

        return list(set(keywords))

    async def scrape_scholar_papers(self, max_results: int = 300) -> List[Dict[str, Any]]:
        """Scrape papers from Google Scholar"""
        logger.info(f"Starting Google Scholar academic scrape...")

        all_papers = []
        queries = self.build_search_queries(max_results)

        logger.info(f"Running {len(queries)} different Scholar queries...")

        for i, query_info in enumerate(queries, 1):
            try:
                logger.info(f"Query {i}/{len(queries)}: {query_info['description']}")

                papers = self.search_google_scholar(
                    query_info['query'],
                    query_info['num_results']
                )

                # Filter relevant papers
                relevant_papers = []
                for paper in papers:
                    african_score = paper['african_relevance_score']
                    ai_score = paper['ai_relevance_score']

                    # Filtering criteria
                    if (african_score >= 0.2 and ai_score >= 0.15) or \
                       (african_score >= 0.4) or \
                       (ai_score >= 0.5 and african_score >= 0.1):
                        relevant_papers.append(paper)

                all_papers.extend(relevant_papers)
                logger.info(f"   Found {len(relevant_papers)} relevant papers")

                # Rate limiting - SerpAPI has limits
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error in query {i}: {e}")
                continue

        # Remove duplicates by title
        unique_papers = {}
        for paper in all_papers:
            title_key = paper['title'].lower().strip()
            if title_key not in unique_papers:
                unique_papers[title_key] = paper

        result_papers = list(unique_papers.values())

        # Sort by relevance and citation count
        result_papers.sort(
            key=lambda p: (p['african_relevance_score'] * 0.5 + p['ai_relevance_score'] * 0.3 +
                          min(p['citation_count'] / 100, 0.2)),
            reverse=True
        )

        logger.info(f"Found {len(result_papers)} unique relevant Scholar papers")
        return result_papers


async def test_scholar_scraping():
    """Test Google Scholar academic scraping"""
    logger.info("📚 Starting Google Scholar Academic Test...")

    scraper = GoogleScholarScraper()
    papers = await scraper.scrape_scholar_papers(max_results=100)  # Reduced for testing

    logger.info(f"✅ Successfully scraped {len(papers)} Scholar papers")

    if papers:
        # Show top papers
        logger.info("\n📚 Top African AI Papers from Google Scholar:")
        for i, paper in enumerate(papers[:10], 1):
            logger.info(f"\n{i}. {paper['title']}")
            logger.info(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            logger.info(f"   Journal: {paper['journal']}")
            if paper['year']:
                logger.info(f"   Year: {paper['year']}")
            logger.info(f"   Citations: {paper['citation_count']}")
            logger.info(f"   African Score: {paper['african_relevance_score']:.2f}")
            logger.info(f"   AI Score: {paper['ai_relevance_score']:.2f}")
            logger.info(f"   African Entities: {paper['african_entities']}")
            logger.info(f"   Keywords: {paper['keywords']}")
            logger.info(f"   URL: {paper['url']}")
            if paper['pdf_url']:
                logger.info(f"   PDF: {paper['pdf_url']}")
            logger.info(f"   Abstract: {paper['abstract'][:300]}...")
            logger.info("-" * 100)

    # Comprehensive statistics
    if papers:
        avg_african_score = sum(p['african_relevance_score'] for p in papers) / len(papers)
        avg_ai_score = sum(p['ai_relevance_score'] for p in papers) / len(papers)
        avg_citations = sum(p['citation_count'] for p in papers) / len(papers)

        high_relevance = [p for p in papers if p['african_relevance_score'] >= 0.5 and p['ai_relevance_score'] >= 0.3]

        logger.info(f"\n📚 Google Scholar Statistics:")
        logger.info(f"   Total Scholar Papers: {len(papers)}")
        logger.info(f"   High Relevance Papers: {len(high_relevance)}")
        logger.info(f"   Average African Relevance: {avg_african_score:.3f}")
        logger.info(f"   Average AI Relevance: {avg_ai_score:.3f}")
        logger.info(f"   Average Citations: {avg_citations:.1f}")

        # Year distribution
        years = {}
        for paper in papers:
            if paper['year']:
                years[paper['year']] = years.get(paper['year'], 0) + 1

        if years:
            logger.info(f"   Year Distribution: {dict(sorted(years.items(), reverse=True))}")

        # Citation distribution
        high_cited = [p for p in papers if p['citation_count'] >= 50]
        logger.info(f"   Highly Cited Papers (50+): {len(high_cited)}")

        # African entity distribution
        all_entities = []
        for paper in papers:
            all_entities.extend(paper['african_entities'])

        entity_count = {}
        for entity in all_entities:
            entity_count[entity] = entity_count.get(entity, 0) + 1

        if entity_count:
            logger.info(f"   Top African Entities: {dict(list(sorted(entity_count.items(), key=lambda x: x[1], reverse=True))[:10])}")

        # Keywords distribution
        all_keywords = []
        for paper in papers:
            all_keywords.extend(paper['keywords'])

        keyword_count = {}
        for keyword in all_keywords:
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1

        if keyword_count:
            logger.info(f"   Top Keywords: {dict(list(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))[:10])}")

    return papers


if __name__ == "__main__":
    logger.info("📚 TAIFA-FIALA Google Scholar Academic Test Starting...")

    papers = asyncio.run(test_scholar_scraping())

    logger.info("🏁 Google Scholar academic test completed!")

    if papers:
        logger.info(f"✨ Excellent! Found {len(papers)} relevant African AI papers from Scholar")
        logger.info("📈 This significantly expands our academic dataset!")
        logger.info("📝 Next steps:")
        logger.info("   1. Combine ArXiv + PubMed + Scholar datasets")
        logger.info("   2. Store comprehensive papers in database")
        logger.info("   3. Process through vector database")
        logger.info("   4. Set up automated daily ETL runs")
    else:
        logger.warning("⚠️  No Scholar papers found")
