"""
Citation Extraction and Snowball Sampling Service
================================================

Extracts structured citations from Perplexity API responses and implements
snowball sampling for discovering new research papers and innovations.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import aiohttp
from loguru import logger

# Database imports (adjust based on your database setup)
from database.models import Publication, Innovation, EnrichmentCitation
from database.connection import get_db_connection

# Import null result cache
from services.null_result_cache import (
    check_citation_cache, cache_null_citation, check_web_scraping_cache, 
    cache_null_web_scraping, CacheReason, DataSource
)


class CitationType(Enum):
    """Types of citations that can be extracted"""
    ACADEMIC_PAPER = "academic_paper"
    NEWS_ARTICLE = "news_article"
    COMPANY_WEBSITE = "company_website"
    GITHUB_REPO = "github_repo"
    BLOG_POST = "blog_post"
    REPORT = "report"
    UNKNOWN = "unknown"


@dataclass
class ExtractedCitation:
    """Represents a citation extracted from Perplexity response"""
    id: str
    title: str
    url: Optional[str]
    citation_text: str
    confidence_score: float
    citation_type: CitationType
    discovered_at: datetime
    source_response_id: str
    processed: bool = False
    
    # Additional metadata
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    african_relevance_indicators: Optional[List[str]] = None
    ai_relevance_indicators: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        data['citation_type'] = self.citation_type.value
        data['discovered_at'] = self.discovered_at.isoformat()
        return data


class CitationExtractor:
    """Extracts and processes citations from AI responses"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection or get_db_connection()
        self.citation_patterns = self._init_citation_patterns()
        
    def _init_citation_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for different citation types"""
        return {
            'url_patterns': [
                r'https?://[^\s<>"{}|\\^`\[\]]+',
                r'www\.[^\s<>"{}|\\^`\[\]]+',
            ],
            'doi_patterns': [
                r'doi:?\s*10\.\d+/[^\s]+',
                r'https?://doi\.org/10\.\d+/[^\s]+',
                r'https?://dx\.doi\.org/10\.\d+/[^\s]+',
            ],
            'arxiv_patterns': [
                r'arxiv:?\s*\d{4}\.\d{4,5}',
                r'https?://arxiv\.org/abs/\d{4}\.\d{4,5}',
            ],
            'journal_patterns': [
                r'published in ([^.]+)',
                r'appeared in ([^.]+)',
                r'(\w+ Journal of \w+)',
                r'(Nature|Science|Cell|PNAS)\s+(?:journal)?',
            ],
            'author_patterns': [
                r'by ([A-Z][a-z]+ [A-Z][a-z]+(?:,?\s+(?:and\s+)?[A-Z][a-z]+ [A-Z][a-z]+)*)',
                r'authored by ([^.]+)',
                r'researchers? ([^.]+)',
            ]
        }

    async def extract_citations_from_response(self, 
                                            response_content: str, 
                                            response_id: str,
                                            context: Dict[str, Any] = None) -> List[ExtractedCitation]:
        """Extract structured citations from Perplexity response"""
        
        citations = []
        
        # Extract URLs and create citations
        urls = await self._extract_urls(response_content)
        
        for url in urls:
            # Get context around the URL
            url_context = self._get_url_context(response_content, url)
            
            # Determine citation type
            citation_type = self._classify_citation_type(url, url_context)
            
            # Extract title and metadata
            title = self._extract_title_from_context(url_context, url)
            
            # Calculate confidence score
            confidence = self._calculate_citation_confidence(url, url_context, citation_type)
            
            # Create citation object
            citation = ExtractedCitation(
                id=str(uuid.uuid4()),
                title=title,
                url=url,
                citation_text=url_context,
                confidence_score=confidence,
                citation_type=citation_type,
                discovered_at=datetime.now(),
                source_response_id=response_id,
                authors=self._extract_authors(url_context),
                journal=self._extract_journal(url_context),
                doi=self._extract_doi(url_context),
                african_relevance_indicators=self._extract_african_indicators(url_context),
                ai_relevance_indicators=self._extract_ai_indicators(url_context)
            )
            
            citations.append(citation)
            
        # Also extract citations without URLs (text-only references)
        text_citations = self._extract_text_only_citations(response_content, response_id)
        citations.extend(text_citations)
        
        logger.info(f"Extracted {len(citations)} citations from response {response_id}")
        return citations

    async def _extract_urls(self, content: str, citation_type: str = "unknown") -> List[str]:
        """Extract URLs from content (with cache checking)"""
        urls = set()
        
        for pattern in self.citation_patterns['url_patterns']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match.group().strip('.,;!?')
                if await self._is_valid_citation_url(url, citation_type):
                    urls.add(url)
        
        return list(urls)

    async def _is_valid_citation_url(self, url: str, citation_type: str = "unknown") -> bool:
        """Check if URL is likely to be a valid citation (with cache check)"""
        
        # First check if this URL is cached as null
        try:
            is_cached, cache_entry = await check_citation_cache(url, citation_type)
            if is_cached:
                logger.debug(f"URL {url} is cached as null ({cache_entry.reason.value}), skipping")
                return False
        except Exception as e:
            logger.warning(f"Error checking citation cache for {url}: {e}")
        
        # Skip common non-citation URLs
        skip_domains = [
            'twitter.com', 'facebook.com', 'instagram.com',
            'youtube.com', 'tiktok.com', 'linkedin.com'
        ]
        
        for domain in skip_domains:
            if domain in url.lower():
                # Cache this as permanently invalid
                try:
                    await cache_null_citation(url, citation_type, CacheReason.IRRELEVANT_CONTENT, 
                                           {'skip_reason': 'social_media_domain'})
                except Exception as e:
                    logger.warning(f"Error caching null citation: {e}")
                return False
                
        # Prefer academic and research URLs
        academic_indicators = [
            'arxiv.org', 'doi.org', 'pubmed', 'scholar.google',
            'researchgate', 'acm.org', 'ieee.org', 'springer',
            'nature.com', 'science.org', 'cell.com'
        ]
        
        for indicator in academic_indicators:
            if indicator in url.lower():
                return True
                
        # General validation
        is_valid = len(url) > 10 and ('http' in url or 'www.' in url)
        
        # Cache invalid URLs
        if not is_valid:
            try:
                await cache_null_citation(url, citation_type, CacheReason.INVALID_URL,
                                       {'validation_reason': 'basic_format_check_failed'})
            except Exception as e:
                logger.warning(f"Error caching invalid URL: {e}")
        
        return is_valid

    def _get_url_context(self, content: str, url: str) -> str:
        """Get context around a URL for better understanding"""
        
        # Find the URL position and extract surrounding text
        url_pos = content.find(url)
        if url_pos == -1:
            return ""
            
        start = max(0, url_pos - 200)
        end = min(len(content), url_pos + len(url) + 200)
        
        return content[start:end].strip()

    def _classify_citation_type(self, url: str, context: str) -> CitationType:
        """Classify the type of citation based on URL and context"""
        
        url_lower = url.lower()
        context_lower = context.lower()
        
        # Academic papers
        if any(indicator in url_lower for indicator in [
            'arxiv', 'doi.org', 'pubmed', 'acm.org', 'ieee.org',
            'springer', 'nature.com', 'science.org'
        ]):
            return CitationType.ACADEMIC_PAPER
            
        # GitHub repositories
        if 'github.com' in url_lower:
            return CitationType.GITHUB_REPO
            
        # Company websites
        if any(indicator in context_lower for indicator in [
            'company', 'startup', 'founded', 'ceo', 'headquarters'
        ]):
            return CitationType.COMPANY_WEBSITE
            
        # News articles
        if any(indicator in url_lower for indicator in [
            'techcrunch', 'reuters', 'bloomberg', 'cnn', 'bbc',
            'news', 'blog', 'medium.com'
        ]):
            return CitationType.NEWS_ARTICLE
            
        # Reports
        if any(indicator in context_lower for indicator in [
            'report', 'survey', 'analysis', 'study', 'whitepaper'
        ]):
            return CitationType.REPORT
            
        return CitationType.UNKNOWN

    def _extract_title_from_context(self, context: str, url: str) -> str:
        """Extract title from context around URL"""
        
        # Look for quoted titles
        quote_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'titled\s+"([^"]+)"',
            r'called\s+"([^"]+)"'
        ]
        
        for pattern in quote_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match and len(match.group(1)) > 10:
                return match.group(1).strip()
        
        # Look for sentence containing the URL
        sentences = context.split('.')
        for sentence in sentences:
            if url in sentence:
                # Clean up the sentence and use it as title
                clean_sentence = re.sub(r'https?://[^\s]+', '', sentence).strip()
                if len(clean_sentence) > 20:
                    return clean_sentence[:100] + "..." if len(clean_sentence) > 100 else clean_sentence
        
        # Fallback: use domain name
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            return f"Resource from {domain_match.group(1)}"
            
        return "Untitled Citation"

    def _calculate_citation_confidence(self, url: str, context: str, citation_type: CitationType) -> float:
        """Calculate confidence score for citation"""
        
        base_score = 0.5
        
        # Boost for academic sources
        if citation_type == CitationType.ACADEMIC_PAPER:
            base_score += 0.3
        elif citation_type == CitationType.GITHUB_REPO:
            base_score += 0.2
        elif citation_type == CitationType.REPORT:
            base_score += 0.2
            
        # Boost for African relevance
        african_indicators = ['africa', 'kenya', 'nigeria', 'ghana', 'south africa', 'rwanda']
        if any(indicator in context.lower() for indicator in african_indicators):
            base_score += 0.1
            
        # Boost for AI relevance
        ai_indicators = ['artificial intelligence', 'machine learning', 'ai', 'ml', 'deep learning']
        if any(indicator in context.lower() for indicator in ai_indicators):
            base_score += 0.1
            
        # Penalty for unclear context
        if len(context) < 50:
            base_score -= 0.1
            
        return min(1.0, max(0.1, base_score))

    def _extract_authors(self, context: str) -> Optional[List[str]]:
        """Extract author names from context"""
        
        authors = []
        
        for pattern in self.citation_patterns['author_patterns']:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                author_string = match.group(1)
                # Split by commas and 'and'
                author_list = re.split(r',\s*(?:and\s+)?|\s+and\s+', author_string)
                authors.extend([author.strip() for author in author_list if author.strip()])
        
        return authors if authors else None

    def _extract_journal(self, context: str) -> Optional[str]:
        """Extract journal name from context"""
        
        for pattern in self.citation_patterns['journal_patterns']:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_doi(self, context: str) -> Optional[str]:
        """Extract DOI from context"""
        
        for pattern in self.citation_patterns['doi_patterns']:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None

    def _extract_african_indicators(self, context: str) -> List[str]:
        """Extract indicators of African relevance"""
        
        african_terms = [
            'africa', 'african', 'nigeria', 'kenya', 'ghana', 'south africa',
            'rwanda', 'uganda', 'tanzania', 'egypt', 'morocco', 'tunisia',
            'lagos', 'nairobi', 'cape town', 'cairo', 'accra', 'kigali'
        ]
        
        found_terms = []
        context_lower = context.lower()
        
        for term in african_terms:
            if term in context_lower:
                found_terms.append(term)
        
        return found_terms

    def _extract_ai_indicators(self, context: str) -> List[str]:
        """Extract indicators of AI relevance"""
        
        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'ai', 'ml', 'nlp', 'computer vision',
            'data science', 'algorithm', 'model', 'training'
        ]
        
        found_terms = []
        context_lower = context.lower()
        
        for term in ai_terms:
            if term in context_lower:
                found_terms.append(term)
        
        return found_terms

    def _extract_text_only_citations(self, content: str, response_id: str) -> List[ExtractedCitation]:
        """Extract citations that don't have URLs but are referenced in text"""
        
        citations = []
        
        # Look for patterns like "According to a study by..." or "Research from..."
        reference_patterns = [
            r'according to a (?:study|report|paper|research)(?:\s+by\s+([^,\.]+))?[^\.]*\.([^\.]*)',
            r'research from ([^,\.]+)[^\.]*\.([^\.]*)',
            r'a (?:study|report|paper) by ([^,\.]+)[^\.]*\.([^\.]*)',
            r'(?:paper|study) titled "([^"]+)"[^\.]*\.([^\.]*)'
        ]
        
        for pattern in reference_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                title = match.group(1) if match.group(1) else "Referenced Study"
                context = match.group(0)
                
                citation = ExtractedCitation(
                    id=str(uuid.uuid4()),
                    title=title,
                    url=None,
                    citation_text=context,
                    confidence_score=0.6,  # Lower confidence for text-only
                    citation_type=CitationType.ACADEMIC_PAPER,
                    discovered_at=datetime.now(),
                    source_response_id=response_id,
                    african_relevance_indicators=self._extract_african_indicators(context),
                    ai_relevance_indicators=self._extract_ai_indicators(context)
                )
                
                citations.append(citation)
        
        return citations

    async def store_citations(self, citations: List[ExtractedCitation], 
                            source_publication_id: Optional[str] = None,
                            source_innovation_id: Optional[str] = None) -> List[str]:
        """Store citations in database and return their IDs"""
        
        stored_ids = []
        
        for citation in citations:
            try:
                # Insert into enrichment_citations table
                citation_data = citation.to_dict()
                citation_data['publication_id'] = source_publication_id
                citation_data['innovation_id'] = source_innovation_id
                
                # Execute database insert (adjust SQL based on your schema)
                query = """
                INSERT INTO enrichment_citations 
                (id, publication_id, innovation_id, title, url, confidence_score, 
                 citation_text, discovered_at, processed, citation_type)
                VALUES (%(id)s, %(publication_id)s, %(innovation_id)s, %(title)s, 
                        %(url)s, %(confidence_score)s, %(citation_text)s, 
                        %(discovered_at)s, %(processed)s, %(citation_type)s)
                RETURNING id
                """
                
                result = await self.db.execute(query, citation_data)
                stored_ids.append(citation.id)
                
                logger.info(f"Stored citation: {citation.title[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to store citation {citation.id}: {e}")
        
        return stored_ids

    async def get_unprocessed_citations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get citations that haven't been processed for snowball sampling"""
        
        query = """
        SELECT * FROM enrichment_citations 
        WHERE processed = FALSE 
        AND confidence_score >= 0.7
        ORDER BY confidence_score DESC, discovered_at DESC
        LIMIT %s
        """
        
        results = await self.db.fetch_all(query, (limit,))
        return [dict(row) for row in results]

    async def mark_citation_processed(self, citation_id: str) -> bool:
        """Mark a citation as processed"""
        
        query = """
        UPDATE enrichment_citations 
        SET processed = TRUE, processed_at = NOW()
        WHERE id = %s
        """
        
        try:
            await self.db.execute(query, (citation_id,))
            return True
        except Exception as e:
            logger.error(f"Failed to mark citation {citation_id} as processed: {e}")
            return False

    async def create_snowball_discovery_queue(self) -> List[Dict[str, Any]]:
        """Create a queue of citations for snowball sampling discovery"""
        
        unprocessed_citations = await self.get_unprocessed_citations()
        
        discovery_queue = []
        
        for citation in unprocessed_citations:
            # Prioritize academic papers and high-confidence citations
            priority_score = citation['confidence_score']
            
            if citation['citation_type'] == 'academic_paper':
                priority_score += 0.2
            
            # Boost African AI content
            if (citation.get('african_relevance_indicators') and 
                citation.get('ai_relevance_indicators')):
                priority_score += 0.1
            
            discovery_item = {
                'citation_id': citation['id'],
                'title': citation['title'],
                'url': citation['url'],
                'priority_score': min(1.0, priority_score),
                'citation_type': citation['citation_type'],
                'discovery_method': 'snowball_sampling'
            }
            
            discovery_queue.append(discovery_item)
        
        # Sort by priority score
        discovery_queue.sort(key=lambda x: x['priority_score'], reverse=True)
        
        logger.info(f"Created discovery queue with {len(discovery_queue)} items")
        return discovery_queue


# Integration function for existing pipeline
async def enhance_perplexity_response_with_citations(response_content: str, 
                                                   response_id: str,
                                                   publication_id: Optional[str] = None,
                                                   innovation_id: Optional[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Enhance existing Perplexity response processing with citation extraction
    
    Returns:
        Tuple of (original_content, extracted_citations_data)
    """
    
    extractor = CitationExtractor()
    
    # Extract citations
    citations = await extractor.extract_citations_from_response(
        response_content, response_id
    )
    
    # Store citations
    await extractor.store_citations(citations, publication_id, innovation_id)
    
    # Return citation data for immediate use
    citation_data = [citation.to_dict() for citation in citations]
    
    return response_content, citation_data


if __name__ == "__main__":
    # Test the citation extractor
    async def test_citation_extraction():
        test_content = """
        According to a recent study by researchers at University of Lagos titled "AI Applications in African Healthcare", 
        machine learning models can improve diagnostic accuracy by 40%. The research, published in Nature Medicine 
        (https://doi.org/10.1038/s41591-024-example), shows promising results across 5 African countries.
        
        Another study from Rwanda's AI Lab (https://arxiv.org/abs/2024.12345) demonstrates similar findings.
        The team led by Dr. Jane Uwimana found that computer vision algorithms trained on local data 
        performed significantly better than global models.
        
        See also: https://github.com/ailabrwanda/healthcare-ai for the open source implementation.
        """
        
        extractor = CitationExtractor()
        citations = await extractor.extract_citations_from_response(
            test_content, "test_response_123"
        )
        
        print(f"Extracted {len(citations)} citations:")
        for citation in citations:
            print(f"- {citation.title}")
            print(f"  URL: {citation.url}")
            print(f"  Type: {citation.citation_type.value}")
            print(f"  Confidence: {citation.confidence_score:.2f}")
            print(f"  African indicators: {citation.african_relevance_indicators}")
            print(f"  AI indicators: {citation.ai_relevance_indicators}")
            print()
    
    asyncio.run(test_citation_extraction())