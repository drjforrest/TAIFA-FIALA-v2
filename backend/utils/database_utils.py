"""
Database utility functions for TAIFA-FIALA
Provides convenient wrappers for common database operations
"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from services.database_service import db_service


def store_publications_sync(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Synchronous wrapper for storing publications"""
    return asyncio.run(db_service.bulk_create_publications(publications))


def store_publication_sync(publication: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for storing a single publication"""
    return asyncio.run(db_service.create_publication(publication))


def store_innovation_sync(innovation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for storing an innovation"""
    return asyncio.run(db_service.create_innovation(innovation))


def store_organization_sync(organization: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for storing an organization"""
    return asyncio.run(db_service.create_organization(organization))


def get_database_stats_sync() -> Dict[str, Any]:
    """Synchronous wrapper for getting database statistics"""
    return asyncio.run(db_service.get_statistics())


def search_publications_sync(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Synchronous wrapper for searching publications"""
    return asyncio.run(db_service.search_publications(query, limit))


def search_innovations_sync(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Synchronous wrapper for searching innovations"""
    return asyncio.run(db_service.search_innovations(query, limit))


class DatabaseManager:
    """Easy-to-use database manager for backend modules"""
    
    def __init__(self):
        self.service = db_service
    
    def store_systematic_review_data(self, studies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Store systematic review studies as publications"""
        logger.info(f"📚 Storing {len(studies)} systematic review studies...")
        
        # Convert studies to publication format
        publications = []
        for study in studies:
            pub_data = {
                'title': study.get('title'),
                'publication_type': 'journal',  # Default for systematic review
                'publication_date': study.get('publication_date'),
                'doi': study.get('doi'),
                'url': study.get('url'),
                'venue': study.get('venue'),
                'abstract': study.get('key_outcomes'),  # Use key outcomes as abstract
                'authors': study.get('authors', []),
                'keywords': study.get('keywords', []),
                'citation_count': study.get('citation_count', 0),
                'source_type': 'systematic_review',
                'source_url': study.get('url'),
                'extraction_metadata': {
                    'project_domain': study.get('project_domain'),
                    'ai_techniques': study.get('ai_techniques'),
                    'geographic_scope': study.get('geographic_scope'),
                    'funding_source': study.get('funding_source'),
                    'african_relevance_score': study.get('african_relevance_score'),
                    'ai_relevance_score': study.get('ai_relevance_score'),
                    'african_entities': study.get('african_entities', []),
                    'year': study.get('year')
                }
            }
            publications.append(pub_data)
        
        return store_publications_sync(publications)
    
    def store_arxiv_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Store ArXiv papers as publications"""
        logger.info(f"📄 Storing {len(papers)} ArXiv papers...")
        
        publications = []
        for paper in papers:
            pub_data = {
                'title': paper.get('title'),
                'publication_type': 'preprint',
                'publication_date': paper.get('published'),
                'url': paper.get('link'),
                'venue': 'arXiv',
                'abstract': paper.get('summary'),
                'authors': paper.get('authors', []),
                'keywords': paper.get('categories', []),
                'arxiv_id': paper.get('id'),
                'source_type': 'arxiv',
                'source_url': paper.get('link'),
                'extraction_metadata': paper
            }
            publications.append(pub_data)
        
        return store_publications_sync(publications)
    
    def store_pubmed_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Store PubMed papers as publications"""
        logger.info(f"🏥 Storing {len(papers)} PubMed papers...")
        
        publications = []
        for paper in papers:
            pub_data = {
                'title': paper.get('title'),
                'publication_type': 'journal',
                'publication_date': paper.get('pub_date'),
                'doi': paper.get('doi'),
                'url': paper.get('url'),
                'venue': paper.get('journal'),
                'abstract': paper.get('abstract'),
                'authors': paper.get('authors', []),
                'keywords': paper.get('keywords', []),
                'pubmed_id': paper.get('pmid'),
                'source_type': 'pubmed',
                'source_url': paper.get('url'),
                'extraction_metadata': paper
            }
            publications.append(pub_data)
        
        return store_publications_sync(publications)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        return get_database_stats_sync()


# Global database manager instance
db_manager = DatabaseManager()
