#!/usr/bin/env python3
"""
Unified Academic Data Processor for TAIFA-FIALA
Combines data from ArXiv, PubMed, Google Scholar, and Systematic Review
Creates a comprehensive dataset for the public innovation portal
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

# Import our ETL processors
from .arxiv_scraper import ArxivScraper
from .pubmed_scraper import PubMedScraper
from .systematic_review_processor import SystematicReviewProcessor
# Note: Google Scholar scraper to be integrated when available


class UnifiedAcademicProcessor:
    """Unified processor combining all academic data sources"""
    
    def __init__(self):
        self.all_papers = []
        self.source_statistics = {}
        
    async def collect_all_academic_data(self, max_results_per_source: int = 200) -> List[Dict[str, Any]]:
        """Collect data from all academic sources"""
        logger.info("🚀 Starting Unified Academic Data Collection...")
        
        all_papers = []
        
        # 1. Process Systematic Review Data (existing curated studies)
        logger.info("📚 Processing Systematic Review...")
        try:
            systematic_papers = await self.process_systematic_review()
            all_papers.extend(systematic_papers)
            self.source_statistics['systematic_review'] = len(systematic_papers)
            logger.info(f"   ✅ Added {len(systematic_papers)} systematic review studies")
        except Exception as e:
            logger.error(f"   ❌ Error processing systematic review: {e}")
            self.source_statistics['systematic_review'] = 0
        
        # 2. Collect ArXiv Papers
        logger.info("📄 Processing ArXiv Papers...")
        try:
            arxiv_papers = await self.process_arxiv_papers(max_results_per_source)
            all_papers.extend(arxiv_papers)
            self.source_statistics['arxiv'] = len(arxiv_papers)
            logger.info(f"   ✅ Added {len(arxiv_papers)} ArXiv papers")
        except Exception as e:
            logger.error(f"   ❌ Error processing ArXiv: {e}")
            self.source_statistics['arxiv'] = 0
        
        # 3. Collect PubMed Papers
        logger.info("🏥 Processing PubMed Medical Papers...")
        try:
            pubmed_papers = await self.process_pubmed_papers(max_results_per_source)
            all_papers.extend(pubmed_papers)
            self.source_statistics['pubmed'] = len(pubmed_papers)
            logger.info(f"   ✅ Added {len(pubmed_papers)} PubMed papers")
        except Exception as e:
            logger.error(f"   ❌ Error processing PubMed: {e}")
            self.source_statistics['pubmed'] = 0
        
        # 4. Collect Google Scholar Papers
        logger.info("🎓 Processing Google Scholar Papers...")
        try:
            scholar_papers = await self.process_scholar_papers(max_results_per_source // 4)  # Reduced due to API limits
            all_papers.extend(scholar_papers)
            self.source_statistics['google_scholar'] = len(scholar_papers)
            logger.info(f"   ✅ Added {len(scholar_papers)} Google Scholar papers")
        except Exception as e:
            logger.error(f"   ❌ Error processing Google Scholar: {e}")
            self.source_statistics['google_scholar'] = 0
        
        # 5. Deduplicate and clean
        logger.info("🔧 Deduplicating and cleaning data...")
        cleaned_papers = self.deduplicate_papers(all_papers)
        
        self.all_papers = cleaned_papers
        
        logger.info(f"🎉 Unified Academic Collection Complete!")
        logger.info(f"   Total Papers Collected: {len(cleaned_papers)}")
        logger.info(f"   Sources: {self.source_statistics}")
        
        return cleaned_papers
    
    async def process_systematic_review(self) -> List[Dict[str, Any]]:
        """Process systematic review data"""
        csv_path = "/Users/drjforrest/dev/devprojects/TAIFA-FIALA/data/Elicit - extract-results-review-b8c80b4e-9037-459f-9afb-d4c8b22f8553.csv"
        
        processor = SystematicReviewProcessor(csv_path)
        processor.load_data()
        studies = processor.clean_and_process_data()
        
        # Standardize format for consistency
        standardized_studies = []
        for study in studies:
            standardized = self.standardize_paper_format(study, 'systematic_review')
            if standardized:
                standardized_studies.append(standardized)
        
        return standardized_studies
    
    async def process_arxiv_papers(self, max_results: int) -> List[Dict[str, Any]]:
        """Process ArXiv papers"""
        async with ArxivScraper() as scraper:
            papers = await scraper.search_african_ai_papers(max_results=max_results)
            
            standardized_papers = []
            for paper in papers:
                standardized = self.standardize_paper_format(paper.__dict__, 'arxiv')
                if standardized:
                    standardized_papers.append(standardized)
            
            return standardized_papers
    
    async def process_pubmed_papers(self, max_results: int) -> List[Dict[str, Any]]:
        """Process PubMed papers"""
        async with PubMedScraper() as scraper:
            papers = await scraper.search_african_health_ai(max_results=max_results)
            
            standardized_papers = []
            for paper in papers:
                standardized = self.standardize_paper_format(paper.__dict__, 'pubmed')
                if standardized:
                    standardized_papers.append(standardized)
            
            return standardized_papers
    
    async def process_scholar_papers(self, max_results: int) -> List[Dict[str, Any]]:
        """Process Google Scholar papers - temporarily disabled pending ETL integration"""
        logger.info("Google Scholar processing temporarily disabled - awaiting ETL integration")
        return []  # Return empty list until Google Scholar ETL module is integrated
    
    def standardize_paper_format(self, paper: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Standardize paper format across all sources"""
        try:
            # Create a unified format
            standardized = {
                # Core identification
                'title': paper.get('title', '').strip(),
                'authors': paper.get('authors', []),
                'abstract': paper.get('abstract', '') or paper.get('snippet', ''),
                
                # Publication info
                'journal': paper.get('journal', '') or paper.get('venue', ''),
                'year': paper.get('year'),
                'publication_date': paper.get('publication_date'),
                'doi': paper.get('doi', ''),
                'url': paper.get('url', '') or paper.get('doi_link', ''),
                'pdf_url': paper.get('pdf_url', ''),
                
                # Metrics
                'citation_count': paper.get('citation_count', 0),
                
                # Relevance and classification
                'african_relevance_score': paper.get('african_relevance_score', 0.0),
                'ai_relevance_score': paper.get('ai_relevance_score', 0.0) or paper.get('medical_ai_score', 0.0),
                'african_entities': paper.get('african_entities', []),
                'keywords': paper.get('keywords', []),
                
                # Source-specific fields
                'source': source,
                'source_id': self.generate_source_id(paper, source),
                
                # Additional metadata
                'categories': paper.get('categories', []),
                'project_domain': paper.get('project_domain', ''),
                'funding_source': paper.get('funding_source', ''),
                'ai_techniques': paper.get('ai_techniques', ''),
                'geographic_scope': paper.get('geographic_scope', ''),
                'key_outcomes': paper.get('key_outcomes', ''),
                
                # Processing metadata
                'processed_at': datetime.now(),
                'data_type': paper.get('data_type', 'Academic Paper')
            }
            
            # Only return if we have a valid title
            if standardized['title'] and len(standardized['title']) > 5:
                return standardized
            
            return None
            
        except Exception as e:
            logger.error(f"Error standardizing paper: {e}")
            return None
    
    def generate_source_id(self, paper: Dict[str, Any], source: str) -> str:
        """Generate a unique source ID"""
        if source == 'arxiv':
            return f"arxiv:{paper.get('arxiv_id', '')}"
        elif source == 'pubmed':
            return f"pubmed:{paper.get('pmid', '')}"
        elif source == 'google_scholar':
            return f"scholar:{hash(paper.get('title', ''))}"
        elif source == 'systematic_review':
            return f"review:{hash(paper.get('title', ''))}"
        else:
            return f"{source}:{hash(paper.get('title', ''))}"
    
    def deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on title similarity"""
        logger.info(f"Deduplicating {len(papers)} papers...")
        
        unique_papers = {}
        duplicate_count = 0
        
        for paper in papers:
            # Create a normalized title for comparison
            title_key = self.normalize_title_for_dedup(paper['title'])
            
            if title_key in unique_papers:
                # Keep the one with higher relevance or more complete data
                existing = unique_papers[title_key]
                
                if self.is_better_paper(paper, existing):
                    unique_papers[title_key] = paper
                
                duplicate_count += 1
            else:
                unique_papers[title_key] = paper
        
        result = list(unique_papers.values())
        logger.info(f"Removed {duplicate_count} duplicates, {len(result)} unique papers remain")
        
        return result
    
    def normalize_title_for_dedup(self, title: str) -> str:
        """Normalize title for deduplication"""
        import re
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        
        # Remove common words and extra spaces
        normalized = re.sub(r'\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by)\b', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def is_better_paper(self, paper1: Dict[str, Any], paper2: Dict[str, Any]) -> bool:
        """Determine if paper1 is better than paper2"""
        # Prioritize systematic review data (curated)
        if paper1['source'] == 'systematic_review' and paper2['source'] != 'systematic_review':
            return True
        if paper2['source'] == 'systematic_review' and paper1['source'] != 'systematic_review':
            return False
        
        # Calculate combined relevance score
        score1 = (paper1['african_relevance_score'] * 0.5 + 
                 paper1['ai_relevance_score'] * 0.5 +
                 min(paper1['citation_count'] / 100, 0.2))
        
        score2 = (paper2['african_relevance_score'] * 0.5 + 
                 paper2['ai_relevance_score'] * 0.5 +
                 min(paper2['citation_count'] / 100, 0.2))
        
        return score1 > score2
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics of the unified dataset"""
        if not self.all_papers:
            return {}
        
        total_papers = len(self.all_papers)
        
        # Source distribution
        source_dist = {}
        for paper in self.all_papers:
            source = paper['source']
            source_dist[source] = source_dist.get(source, 0) + 1
        
        # Year distribution
        year_dist = {}
        for paper in self.all_papers:
            year = paper.get('year')
            if year:
                year_dist[year] = year_dist.get(year, 0) + 1
        
        # Domain distribution (from systematic review data)
        domain_dist = {}
        for paper in self.all_papers:
            domain = paper.get('project_domain', '')
            if domain and domain != 'nan':
                # Clean domain
                domain = domain.split('\n')[0].strip('- ').strip()
                if domain and len(domain) > 3:
                    domain_dist[domain] = domain_dist.get(domain, 0) + 1
        
        # Geographic distribution
        geo_dist = {}
        for paper in self.all_papers:
            for entity in paper.get('african_entities', []):
                geo_dist[entity] = geo_dist.get(entity, 0) + 1
        
        # Keywords distribution
        keyword_dist = {}
        for paper in self.all_papers:
            for keyword in paper.get('keywords', []):
                keyword_dist[keyword] = keyword_dist.get(keyword, 0) + 1
        
        # Relevance scores
        african_scores = [p['african_relevance_score'] for p in self.all_papers if p['african_relevance_score'] > 0]
        ai_scores = [p['ai_relevance_score'] for p in self.all_papers if p['ai_relevance_score'] > 0]
        citations = [p['citation_count'] for p in self.all_papers if p['citation_count'] > 0]
        
        return {
            'total_papers': total_papers,
            'source_distribution': dict(sorted(source_dist.items(), key=lambda x: x[1], reverse=True)),
            'year_distribution': dict(sorted(year_dist.items(), reverse=True)),
            'top_domains': dict(list(sorted(domain_dist.items(), key=lambda x: x[1], reverse=True))[:10]),
            'top_african_entities': dict(list(sorted(geo_dist.items(), key=lambda x: x[1], reverse=True))[:15]),
            'top_keywords': dict(list(sorted(keyword_dist.items(), key=lambda x: x[1], reverse=True))[:15]),
            'avg_african_relevance': sum(african_scores) / len(african_scores) if african_scores else 0,
            'avg_ai_relevance': sum(ai_scores) / len(ai_scores) if ai_scores else 0,
            'avg_citations': sum(citations) / len(citations) if citations else 0,
            'high_relevance_papers': len([p for p in self.all_papers 
                                        if p['african_relevance_score'] >= 0.5 and p['ai_relevance_score'] >= 0.3]),
            'recent_papers': len([p for p in self.all_papers 
                                if p.get('year', 0) >= 2020])
        }
    
    def save_dataset(self, filename: str = 'unified_african_ai_dataset.json') -> str:
        """Save the unified dataset to a JSON file"""
        filepath = f"/Users/drjforrest/dev/devprojects/TAIFA-FIALA/data/{filename}"
        
        dataset = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_papers': len(self.all_papers),
                'sources': self.source_statistics,
                'version': '1.0'
            },
            'statistics': self.get_comprehensive_statistics(),
            'papers': self.all_papers
        }
        
        # Convert datetime objects to strings for JSON serialization
        for paper in dataset['papers']:
            if paper.get('publication_date'):
                paper['publication_date'] = paper['publication_date'].isoformat()
            if paper.get('processed_at'):
                paper['processed_at'] = paper['processed_at'].isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset saved to: {filepath}")
        return filepath


async def main():
    """Main function to run the unified academic data collection"""
    logger.info("🌍 TAIFA-FIALA Unified Academic Data Collection Starting...")
    
    processor = UnifiedAcademicProcessor()
    
    # Collect all data (using smaller limits for testing)
    papers = await processor.collect_all_academic_data(max_results_per_source=100)
    
    if papers:
        # Show sample papers
        logger.info("\n🎓 Sample Papers from Unified Dataset:")
        for i, paper in enumerate(papers[:10], 1):
            logger.info(f"\n{i}. {paper['title']}")
            logger.info(f"   Source: {paper['source']}")
            logger.info(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            logger.info(f"   Journal: {paper['journal']}")
            if paper['year']:
                logger.info(f"   Year: {paper['year']}")
            logger.info(f"   Citations: {paper['citation_count']}")
            logger.info(f"   African Score: {paper['african_relevance_score']:.2f}")
            logger.info(f"   AI Score: {paper['ai_relevance_score']:.2f}")
            logger.info(f"   African Entities: {paper['african_entities']}")
            logger.info(f"   Keywords: {paper['keywords']}")
            if paper['url']:
                logger.info(f"   URL: {paper['url']}")
            logger.info("-" * 100)
        
        # Show comprehensive statistics
        stats = processor.get_comprehensive_statistics()
        
        logger.info(f"\n📊 Comprehensive Dataset Statistics:")
        logger.info(f"   Total Papers: {stats['total_papers']}")
        logger.info(f"   High Relevance Papers: {stats['high_relevance_papers']}")
        logger.info(f"   Recent Papers (2020+): {stats['recent_papers']}")
        logger.info(f"   Average African Relevance: {stats['avg_african_relevance']:.3f}")
        logger.info(f"   Average AI Relevance: {stats['avg_ai_relevance']:.3f}")
        logger.info(f"   Average Citations: {stats['avg_citations']:.1f}")
        
        logger.info(f"\n📈 Source Distribution: {stats['source_distribution']}")
        
        if stats['year_distribution']:
            logger.info(f"   Year Distribution: {dict(list(stats['year_distribution'].items())[:10])}")
        
        if stats['top_domains']:
            logger.info(f"   Top Domains: {stats['top_domains']}")
        
        if stats['top_african_entities']:
            logger.info(f"   Top African Entities: {stats['top_african_entities']}")
        
        if stats['top_keywords']:
            logger.info(f"   Top Keywords: {stats['top_keywords']}")
        
        # Save the dataset
        filepath = processor.save_dataset()
        
        logger.info("🎉 Unified Academic Data Collection Complete!")
        logger.info("📝 Next steps:")
        logger.info("   1. Store dataset in database")
        logger.info("   2. Build search and discovery APIs")
        logger.info("   3. Create public portal interface")
        logger.info("   4. Set up automated daily updates")
        logger.info(f"   5. Dataset available at: {filepath}")
        
        return papers
        
    else:
        logger.warning("⚠️  No papers were collected")
        return []


if __name__ == "__main__":
    papers = asyncio.run(main())