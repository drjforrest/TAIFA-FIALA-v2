"""
Modern Deduplication Service for TAIFA-FIALA
Refactored from previous version to work with current Supabase-integrated ETL pipeline

Implements multi-layer deduplication for:
- Publications (ArXiv, PubMed, systematic reviews)
- Innovations (startups, research projects)
- Organizations (universities, companies)
- Funding announcements

Integrates with the current database service and ETL pipeline.
"""

import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
from loguru import logger

try:
    from fuzzywuzzy import fuzz
except ImportError:
    logger.warning("fuzzywuzzy not installed. Install with: pip install fuzzywuzzy python-levenshtein")
    # Fallback to simple string comparison
    class fuzz:
        @staticmethod
        def ratio(s1: str, s2: str) -> int:
            return 100 if s1.lower() == s2.lower() else 0

from services.database_service import db_service


class DuplicateType(Enum):
    """Types of duplicates detected"""
    EXACT_MATCH = "exact_match"
    TITLE_SIMILARITY = "title_similarity"
    CONTENT_SIMILARITY = "content_similarity"
    URL_MATCH = "url_match"
    DOI_MATCH = "doi_match"
    ARXIV_ID_MATCH = "arxiv_id_match"
    PUBMED_ID_MATCH = "pubmed_id_match"
    SEMANTIC_MATCH = "semantic_match"
    TEMPORAL_CLUSTER = "temporal_cluster"
    ORGANIZATION_MATCH = "organization_match"


class DuplicateAction(Enum):
    """Actions to take for duplicates"""
    REJECT = "reject"
    MERGE = "merge"
    UPDATE = "update"
    LINK = "link"


@dataclass
class DuplicateMatch:
    """Result of duplicate detection"""
    is_duplicate: bool
    match_type: DuplicateType
    similarity_score: float
    existing_record_id: Optional[str] = None
    existing_record: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    action: DuplicateAction = DuplicateAction.REJECT


class URLNormalizer:
    """Normalizes URLs for consistent comparison"""
    
    def normalize(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        
        # Remove common tracking parameters
        tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'ref', 'source', 'campaign'
        ]
        
        try:
            parsed = urlparse(url.lower().strip())
            
            # Remove www prefix
            netloc = parsed.netloc
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            # Remove trailing slash from path
            path = parsed.path.rstrip('/')
            
            # Remove tracking parameters from query
            if parsed.query:
                query_parts = []
                for part in parsed.query.split('&'):
                    if '=' in part:
                        key, _ = part.split('=', 1)
                        if key not in tracking_params:
                            query_parts.append(part)
                query = '&'.join(query_parts)
            else:
                query = ''
            
            # Reconstruct URL
            normalized = f"{parsed.scheme}://{netloc}{path}"
            if query:
                normalized += f"?{query}"
            
            return normalized
            
        except Exception as e:
            logger.warning(f"Failed to normalize URL {url}: {e}")
            return url.lower().strip()


class ContentHasher:
    """Creates content hashes for duplicate detection"""
    
    def create_content_hash(self, title: str, description: str, organization: str = "") -> str:
        """Create a hash from normalized content"""
        # Normalize text
        normalized_title = self._normalize_text(title)
        normalized_desc = self._normalize_text(description)
        normalized_org = self._normalize_text(organization)
        
        # Combine and hash
        combined = f"{normalized_title}|{normalized_desc}|{normalized_org}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        return text


class DeduplicationService:
    """Main deduplication service for TAIFA-FIALA ETL pipeline"""
    
    def __init__(self):
        self.url_normalizer = URLNormalizer()
        self.content_hasher = ContentHasher()
        self.db_service = db_service
    
    # PUBLICATION DEDUPLICATION
    async def check_publication_duplicates(self, publication_data: Dict[str, Any]) -> List[DuplicateMatch]:
        """Check for duplicate publications using multiple detection methods"""
        duplicates = []
        
        # Method 1: DOI exact match
        if publication_data.get('doi'):
            existing = await self.db_service.query_publications(
                filters={'doi': publication_data['doi']}
            )
            if existing:
                duplicates.extend([
                    DuplicateMatch(
                        existing_id=pub['id'],
                        match_type='doi_exact',
                        confidence=1.0,
                        existing_record=pub
                    ) for pub in existing
                ])
        
        # Method 2: Source ID exact match (ArXiv, PubMed, etc.)
        if publication_data.get('source_id'):
            existing = await self.db_service.query_publications(
                filters={'source_id': publication_data['source_id']}
            )
            if existing:
                duplicates.extend([
                    DuplicateMatch(
                        existing_id=pub['id'],
                        match_type='source_id_exact',
                        confidence=1.0,
                        existing_record=pub
                    ) for pub in existing
                ])
        
        # Method 3: URL exact match
        if publication_data.get('url'):
            normalized_url = self.url_normalizer.normalize(publication_data['url'])
            existing = await self.db_service.query_publications(
                filters={'url': normalized_url}
            )
            if existing:
                duplicates.extend([
                    DuplicateMatch(
                        existing_id=pub['id'],
                        match_type='url_exact',
                        confidence=0.95,
                        existing_record=pub
                    ) for pub in existing
                ])
        
        # Method 4: Title similarity
        if publication_data.get('title'):
            title_match = await self._check_title_similarity(
                publication_data['title'], 
                'publications',
                threshold=0.85
            )
            if title_match.is_duplicate:
                duplicates.append(title_match)
        
        # Method 5: Content similarity
        content_match = await self._check_content_similarity(
            publication_data.get('title', ''),
            publication_data.get('abstract', ''),
            'publications'
        )
        if content_match.is_duplicate:
            duplicates.append(content_match)
        
        return duplicates
    
    # INNOVATION DEDUPLICATION
    async def check_innovation_duplicate(self, innovation_data: Dict[str, Any]) -> DuplicateMatch:
        """Check if an innovation is a duplicate"""
        
        # 1. Check URL match
        if innovation_data.get('source_url'):
            url_match = await self._check_url_duplicate(innovation_data['source_url'], 'innovations')
            if url_match.is_duplicate:
                return url_match
        
        # 2. Check title similarity
        if innovation_data.get('title'):
            title_match = await self._check_title_similarity(
                innovation_data['title'],
                'innovations',
                threshold=0.80
            )
            if title_match.is_duplicate:
                return title_match
        
        # 3. Check content similarity
        content_match = await self._check_content_similarity(
            innovation_data.get('title', ''),
            innovation_data.get('description', ''),
            'innovations'
        )
        if content_match.is_duplicate:
            return content_match
        
        return DuplicateMatch(
            is_duplicate=False,
            match_type=DuplicateType.EXACT_MATCH,
            similarity_score=0.0
        )
    
    # ORGANIZATION DEDUPLICATION
    async def check_organization_duplicate(self, org_data: Dict[str, Any]) -> DuplicateMatch:
        """Check if an organization is a duplicate"""
        
        # 1. Check exact name match
        if org_data.get('name'):
            name_match = await self._check_organization_name(org_data['name'])
            if name_match.is_duplicate:
                return name_match
        
        # 2. Check website match
        if org_data.get('website'):
            url_match = await self._check_url_duplicate(org_data['website'], 'organizations')
            if url_match.is_duplicate:
                return url_match
        
        return DuplicateMatch(
            is_duplicate=False,
            match_type=DuplicateType.EXACT_MATCH,
            similarity_score=0.0
        )
    
    # HELPER METHODS
    async def _check_doi_duplicate(self, doi: str) -> DuplicateMatch:
        """Check for DOI duplicates"""
        try:
            publications = await self.db_service.get_publications(filters={'doi': doi})
            
            if publications:
                return DuplicateMatch(
                    is_duplicate=True,
                    match_type=DuplicateType.DOI_MATCH,
                    similarity_score=1.0,
                    existing_record_id=publications[0]['id'],
                    existing_record=publications[0],
                    reason=f"DOI match found: {doi}",
                    action=DuplicateAction.UPDATE
                )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.DOI_MATCH, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking DOI duplicate: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.DOI_MATCH, similarity_score=0.0)
    
    async def _check_arxiv_id_duplicate(self, arxiv_id: str) -> DuplicateMatch:
        """Check for ArXiv ID duplicates"""
        try:
            publications = await self.db_service.get_publications(filters={'arxiv_id': arxiv_id})
            
            if publications:
                return DuplicateMatch(
                    is_duplicate=True,
                    match_type=DuplicateType.ARXIV_ID_MATCH,
                    similarity_score=1.0,
                    existing_record_id=publications[0]['id'],
                    existing_record=publications[0],
                    reason=f"ArXiv ID match found: {arxiv_id}",
                    action=DuplicateAction.UPDATE
                )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.ARXIV_ID_MATCH, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking ArXiv ID duplicate: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.ARXIV_ID_MATCH, similarity_score=0.0)
    
    async def _check_pubmed_id_duplicate(self, pubmed_id: str) -> DuplicateMatch:
        """Check for PubMed ID duplicates"""
        try:
            publications = await self.db_service.get_publications(filters={'pubmed_id': pubmed_id})
            
            if publications:
                return DuplicateMatch(
                    is_duplicate=True,
                    match_type=DuplicateType.PUBMED_ID_MATCH,
                    similarity_score=1.0,
                    existing_record_id=publications[0]['id'],
                    existing_record=publications[0],
                    reason=f"PubMed ID match found: {pubmed_id}",
                    action=DuplicateAction.UPDATE
                )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.PUBMED_ID_MATCH, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking PubMed ID duplicate: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.PUBMED_ID_MATCH, similarity_score=0.0)
    
    async def _check_url_duplicate(self, url: str, table_name: str) -> DuplicateMatch:
        """Check for URL duplicates"""
        try:
            normalized_url = self.url_normalizer.normalize(url)
            
            # Get records from appropriate table
            if table_name == 'publications':
                records = await self.db_service.get_publications(limit=1000)
            elif table_name == 'innovations':
                records = await self.db_service.get_innovations(limit=1000)
            else:
                return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.URL_MATCH, similarity_score=0.0)
            
            for record in records:
                record_url = record.get('url') or record.get('source_url') or record.get('website')
                if record_url:
                    normalized_record_url = self.url_normalizer.normalize(record_url)
                    if normalized_url == normalized_record_url:
                        return DuplicateMatch(
                            is_duplicate=True,
                            match_type=DuplicateType.URL_MATCH,
                            similarity_score=1.0,
                            existing_record_id=record['id'],
                            existing_record=record,
                            reason=f"URL match found: {normalized_url}",
                            action=DuplicateAction.UPDATE
                        )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.URL_MATCH, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking URL duplicate: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.URL_MATCH, similarity_score=0.0)
    
    async def _check_title_similarity(self, title: str, table_name: str, threshold: float = 0.85) -> DuplicateMatch:
        """Check for title similarity"""
        try:
            # Get records from appropriate table
            if table_name == 'publications':
                records = await self.db_service.get_publications(limit=1000)
            elif table_name == 'innovations':
                records = await self.db_service.get_innovations(limit=1000)
            else:
                return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.TITLE_SIMILARITY, similarity_score=0.0)
            
            for record in records:
                record_title = record.get('title', '')
                if record_title:
                    similarity = fuzz.ratio(title.lower(), record_title.lower()) / 100.0
                    if similarity >= threshold:
                        return DuplicateMatch(
                            is_duplicate=True,
                            match_type=DuplicateType.TITLE_SIMILARITY,
                            similarity_score=similarity,
                            existing_record_id=record['id'],
                            existing_record=record,
                            reason=f"Title similarity: {similarity:.2f}",
                            action=DuplicateAction.MERGE if similarity > 0.95 else DuplicateAction.LINK
                        )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.TITLE_SIMILARITY, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking title similarity: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.TITLE_SIMILARITY, similarity_score=0.0)
    
    async def _check_content_similarity(self, title: str, content: str, table_name: str, threshold: float = 0.80) -> DuplicateMatch:
        """Check for content similarity using hashing"""
        try:
            content_hash = self.content_hasher.create_content_hash(title, content)
            
            # Get records from appropriate table
            if table_name == 'publications':
                records = await self.db_service.get_publications(limit=1000)
            elif table_name == 'innovations':
                records = await self.db_service.get_innovations(limit=1000)
            else:
                return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.CONTENT_SIMILARITY, similarity_score=0.0)
            
            for record in records:
                record_title = record.get('title', '')
                record_content = record.get('abstract') or record.get('description', '')
                
                if record_title or record_content:
                    record_hash = self.content_hasher.create_content_hash(record_title, record_content)
                    
                    if content_hash == record_hash:
                        return DuplicateMatch(
                            is_duplicate=True,
                            match_type=DuplicateType.CONTENT_SIMILARITY,
                            similarity_score=1.0,
                            existing_record_id=record['id'],
                            existing_record=record,
                            reason="Exact content hash match",
                            action=DuplicateAction.REJECT
                        )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.CONTENT_SIMILARITY, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking content similarity: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.CONTENT_SIMILARITY, similarity_score=0.0)
    
    async def _check_organization_name(self, name: str) -> DuplicateMatch:
        """Check for organization name duplicates"""
        try:
            # Simple exact match for now - can be enhanced with fuzzy matching
            organizations = await self.db_service.client.table('organizations').select('*').ilike('name', f'%{name}%').execute()
            
            if organizations.data:
                for org in organizations.data:
                    similarity = fuzz.ratio(name.lower(), org['name'].lower()) / 100.0
                    if similarity >= 0.90:
                        return DuplicateMatch(
                            is_duplicate=True,
                            match_type=DuplicateType.ORGANIZATION_MATCH,
                            similarity_score=similarity,
                            existing_record_id=org['id'],
                            existing_record=org,
                            reason=f"Organization name similarity: {similarity:.2f}",
                            action=DuplicateAction.MERGE if similarity > 0.95 else DuplicateAction.LINK
                        )
            
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.ORGANIZATION_MATCH, similarity_score=0.0)
            
        except Exception as e:
            logger.error(f"Error checking organization name: {e}")
            return DuplicateMatch(is_duplicate=False, match_type=DuplicateType.ORGANIZATION_MATCH, similarity_score=0.0)


# Global deduplication service instance
dedup_service = DeduplicationService()
