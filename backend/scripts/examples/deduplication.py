"""
Deduplication Pipeline Module

Implements multi-layer deduplication system to prevent duplicate opportunities
from reaching community validation. Uses URL, content, and metadata-based
deduplication strategies.
"""

import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import asyncpg
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer

from app.core.database import get_database
from app.utils.url_utils import normalize_url


@dataclass
class OpportunityContent:
    """Structure for opportunity content to be deduplicated"""
    url: str
    title: str
    description: str
    organization: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    deadline: Optional[datetime] = None
    source_id: Optional[int] = None


@dataclass
class DuplicateMatch:
    """Result of duplicate detection"""
    is_duplicate: bool
    match_type: str  # exact_url, similar_url, exact_content, semantic_similarity, metadata_similarity
    similarity_score: Optional[float] = None
    existing_opportunity_id: Optional[int] = None
    existing_url: Optional[str] = None
    reason: Optional[str] = None


class URLNormalizer:
    """Normalizes URLs for consistent comparison"""
    
    def __init__(self):
        self.params_to_remove = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
            'fbclid', 'gclid', 'ref', 'source', 'campaign_id', '_ga', 'mc_cid'
        }
    
    def normalize(self, url: str) -> str:
        """Normalize URL by removing tracking parameters and standardizing format"""
        try:
            parsed = urlparse(url.lower().strip())
            
            # Remove tracking parameters
            query_params = parse_qs(parsed.query)
            cleaned_params = {
                k: v for k, v in query_params.items() 
                if k not in self.params_to_remove
            }
            
            # Rebuild query string
            cleaned_query = urlencode(cleaned_params, doseq=True) if cleaned_params else ''
            
            # Remove fragment and rebuild URL
            normalized = urlunparse((
                parsed.scheme or 'https',
                parsed.netloc,
                parsed.path.rstrip('/') if parsed.path != '/' else '/',
                parsed.params,
                cleaned_query,
                ''  # Remove fragment
            ))
            
            return normalized
            
        except Exception:
            return url.lower().strip()


class ContentHasher:
    """Generates consistent hashes for content comparison"""
    
    def hash(self, title: str, description: str, organization: str) -> str:
        """Generate hash from normalized content fields"""
        # Normalize text (lowercase, strip whitespace)
        normalized_title = ' '.join(title.lower().strip().split())
        normalized_desc = ' '.join(description.lower().strip().split())
        normalized_org = ' '.join(organization.lower().strip().split())
        
        # Combine and hash
        combined = f"{normalized_title}|{normalized_desc}|{normalized_org}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()


class URLDeduplicator:
    """Handles URL-based deduplication"""
    
    def __init__(self):
        self.url_normalizer = URLNormalizer()
        self.logger = logging.getLogger(__name__)
    
    async def check_url_duplicate(self, opportunity_url: str) -> DuplicateMatch:
        """Check for URL-based duplicates"""
        try:
            # Normalize the incoming URL
            normalized_url = self.url_normalizer.normalize(opportunity_url)
            
            db = await get_database()
            
            # Check for exact URL match
            exact_match = await db.fetch_one(
                """
                SELECT id, url FROM africa_intelligence_feed 
                WHERE url = $1 OR url = $2
                """,
                opportunity_url, normalized_url
            )
            
            if exact_match:
                return DuplicateMatch(
                    is_duplicate=True,
                    match_type="exact_url",
                    existing_opportunity_id=exact_match["id"],
                    existing_url=exact_match["url"],
                    reason="Exact URL match found"
                )
            
            # Check for similar URLs (same domain + similar path)
            parsed_url = urlparse(normalized_url)
            domain = parsed_url.netloc
            path_parts = [part for part in parsed_url.path.split('/') if part]
            
            if len(path_parts) >= 2:
                # Look for URLs with same domain and similar path structure
                similar_urls = await db.fetch_all(
                    """
                    SELECT id, url FROM africa_intelligence_feed 
                    WHERE url ILIKE $1 AND url != $2
                    LIMIT 10
                    """,
                    f"%{domain}%", normalized_url
                )
                
                for similar in similar_urls:
                    similarity = self._calculate_url_similarity(normalized_url, similar["url"])
                    if similarity > 0.8:
                        return DuplicateMatch(
                            is_duplicate=True,
                            match_type="similar_url",
                            similarity_score=similarity,
                            existing_opportunity_id=similar["id"],
                            existing_url=similar["url"],
                            reason=f"Similar URL found (similarity: {similarity:.2f})"
                        )
            
            return DuplicateMatch(is_duplicate=False, match_type="no_url_match")
            
        except Exception as e:
            self.logger.error(f"Error in URL deduplication: {e}")
            return DuplicateMatch(is_duplicate=False, match_type="error", reason=str(e))
    
    def _calculate_url_similarity(self, url1: str, url2: str) -> float:
        """Calculate similarity between two URLs"""
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Domain must match
        if parsed1.netloc != parsed2.netloc:
            return 0.0
        
        # Calculate path similarity
        path1_parts = [part for part in parsed1.path.split('/') if part]
        path2_parts = [part for part in parsed2.path.split('/') if part]
        
        if not path1_parts and not path2_parts:
            return 1.0
        
        if not path1_parts or not path2_parts:
            return 0.3  # Some similarity for same domain
        
        # Use fuzzy matching on path components
        path_similarity = fuzz.ratio('/'.join(path1_parts), '/'.join(path2_parts)) / 100.0
        
        return path_similarity


class ContentDeduplicator:
    """Handles content-based deduplication using hashing and semantic similarity"""
    
    def __init__(self):
        self.content_hasher = ContentHasher()
        self.logger = logging.getLogger(__name__)
        # Initialize sentence transformer for semantic similarity
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.warning(f"Could not load sentence transformer: {e}")
            self.embedding_model = None
    
    async def check_content_duplicate(self, opportunity: OpportunityContent) -> DuplicateMatch:
        """Check for content-based duplicates using hash and semantic similarity"""
        try:
            # Generate content hash
            content_hash = self.content_hasher.hash(
                opportunity.title,
                opportunity.description,
                opportunity.organization
            )
            
            db = await get_database()
            
            # Check for exact content hash match
            hash_match = await db.fetch_one(
                """
                SELECT id, title, url FROM africa_intelligence_feed 
                WHERE content_hash = $1
                """,
                content_hash
            )
            
            if hash_match:
                return DuplicateMatch(
                    is_duplicate=True,
                    match_type="exact_content",
                    existing_opportunity_id=hash_match["id"],
                    existing_url=hash_match["url"],
                    reason="Exact content hash match found"
                )
            
            # Semantic similarity check if model is available
            if self.embedding_model:
                semantic_match = await self._check_semantic_similarity(opportunity)
                if semantic_match.is_duplicate:
                    return semantic_match
            
            return DuplicateMatch(is_duplicate=False, match_type="no_content_match")
            
        except Exception as e:
            self.logger.error(f"Error in content deduplication: {e}")
            return DuplicateMatch(is_duplicate=False, match_type="error", reason=str(e))
    
    async def _check_semantic_similarity(self, opportunity: OpportunityContent) -> DuplicateMatch:
        """Check for semantically similar content"""
        try:
            # Create embedding for the new opportunity
            content_text = f"{opportunity.title} {opportunity.description}"
            new_embedding = self.embedding_model.encode([content_text])[0]
            
            db = await get_database()
            
            # Get recent opportunities from same organization for comparison
            recent_opportunities = await db.fetch_all(
                """
                SELECT id, title, description, url, embedding
                FROM africa_intelligence_feed 
                WHERE organization_name ILIKE $1 
                AND created_at > $2
                AND embedding IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 20
                """,
                f"%{opportunity.organization}%",
                datetime.now() - timedelta(days=90)
            )
            
            for opp in recent_opportunities:
                if opp["embedding"]:
                    # Calculate cosine similarity
                    existing_embedding = opp["embedding"]
                    similarity = self._cosine_similarity(new_embedding, existing_embedding)
                    
                    if similarity > 0.9:  # High similarity threshold
                        return DuplicateMatch(
                            is_duplicate=True,
                            match_type="semantic_similarity",
                            similarity_score=similarity,
                            existing_opportunity_id=opp["id"],
                            existing_url=opp["url"],
                            reason=f"High semantic similarity (score: {similarity:.3f})"
                        )
            
            return DuplicateMatch(is_duplicate=False, match_type="no_semantic_match")
            
        except Exception as e:
            self.logger.error(f"Error in semantic similarity check: {e}")
            return DuplicateMatch(is_duplicate=False, match_type="error", reason=str(e))
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        
        # Convert to numpy arrays if needed
        if not isinstance(vec1, np.ndarray):
            vec1 = np.array(vec1)
        if not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class MetadataDeduplicator:
    """Handles metadata-based deduplication (organization + amount + deadline)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def check_metadata_duplicate(self, opportunity: OpportunityContent) -> DuplicateMatch:
        """Check for duplicates based on organization, amount, and deadline combination"""
        try:
            if not opportunity.organization:
                return DuplicateMatch(is_duplicate=False, match_type="no_metadata_check")
            
            db = await get_database()
            
            # Build query conditions based on available metadata
            conditions = ["organization_name ILIKE $1"]
            params = [f"%{opportunity.organization}%"]
            param_count = 1
            
            # Add amount range if available
            if opportunity.amount and opportunity.amount > 0:
                param_count += 1
                conditions.append(f"amount BETWEEN ${param_count} AND ${param_count + 1}")
                params.extend([
                    opportunity.amount * 0.9,  # 10% lower
                    opportunity.amount * 1.1   # 10% higher
                ])
                param_count += 1
            
            # Add deadline range if available
            if opportunity.deadline:
                param_count += 1
                conditions.append(f"deadline BETWEEN ${param_count} AND ${param_count + 1}")
                params.extend([
                    opportunity.deadline - timedelta(days=7),
                    opportunity.deadline + timedelta(days=7)
                ])
                param_count += 1
            
            # Execute query
            query = f"""
                SELECT id, title, organization_name, amount, deadline, url
                FROM africa_intelligence_feed 
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC
                LIMIT 10
            """
            
            potential_duplicates = await db.fetch_all(query, *params)
            
            # Check title similarity for potential matches
            for candidate in potential_duplicates:
                title_similarity = fuzz.ratio(
                    opportunity.title.lower(),
                    candidate["title"].lower()
                ) / 100.0
                
                if title_similarity > 0.85:
                    return DuplicateMatch(
                        is_duplicate=True,
                        match_type="metadata_similarity",
                        similarity_score=title_similarity,
                        existing_opportunity_id=candidate["id"],
                        existing_url=candidate["url"],
                        reason=f"Similar metadata + title (similarity: {title_similarity:.2f})"
                    )
            
            return DuplicateMatch(is_duplicate=False, match_type="no_metadata_match")
            
        except Exception as e:
            self.logger.error(f"Error in metadata deduplication: {e}")
            return DuplicateMatch(is_duplicate=False, match_type="error", reason=str(e))


class DeduplicationPipeline:
    """Main deduplication pipeline that orchestrates all deduplication checks"""
    
    def __init__(self):
        self.url_dedup = URLDeduplicator()
        self.content_dedup = ContentDeduplicator()
        self.metadata_dedup = MetadataDeduplicator()
        self.logger = logging.getLogger(__name__)
    
    async def check_for_duplicates(self, opportunity: OpportunityContent) -> Dict[str, Any]:
        """
        Run all deduplication checks before community validation
        
        Args:
            opportunity: OpportunityContent object to check for duplicates
            
        Returns:
            Dict with duplicate status and detailed results from all checks
        """
        self.logger.info(f"Starting deduplication check for: {opportunity.title[:50]}...")
        
        try:
            # Run all deduplication checks concurrently
            url_check, content_check, metadata_check = await asyncio.gather(
                self.url_dedup.check_url_duplicate(opportunity.url),
                self.content_dedup.check_content_duplicate(opportunity),
                self.metadata_dedup.check_metadata_duplicate(opportunity),
                return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(url_check, Exception):
                self.logger.error(f"URL deduplication error: {url_check}")
                url_check = DuplicateMatch(is_duplicate=False, match_type="error", reason=str(url_check))
            
            if isinstance(content_check, Exception):
                self.logger.error(f"Content deduplication error: {content_check}")
                content_check = DuplicateMatch(is_duplicate=False, match_type="error", reason=str(content_check))
            
            if isinstance(metadata_check, Exception):
                self.logger.error(f"Metadata deduplication error: {metadata_check}")
                metadata_check = DuplicateMatch(is_duplicate=False, match_type="error", reason=str(metadata_check))
            
            # Compile results
            results = {
                "url_check": self._duplicate_match_to_dict(url_check),
                "content_check": self._duplicate_match_to_dict(content_check),
                "metadata_check": self._duplicate_match_to_dict(metadata_check)
            }
            
            # Determine overall duplicate status
            is_duplicate = any(
                result["is_duplicate"] for result in results.values() 
                if result["match_type"] != "error"
            )
            
            # Extract existing opportunity ID if duplicate found
            existing_id = self._extract_existing_id(results)
            
            # Determine action based on results
            if is_duplicate:
                action = "reject_before_validation"
                status = "duplicate_detected"
                primary_match = self._get_primary_match(results)
            else:
                action = "proceed_to_validation"
                status = "unique_opportunity"
                primary_match = None
            
            final_result = {
                "status": status,
                "action": action,
                "is_duplicate": is_duplicate,
                "existing_opportunity_id": existing_id,
                "primary_match_type": primary_match["match_type"] if primary_match else None,
                "primary_similarity_score": primary_match.get("similarity_score") if primary_match else None,
                "duplicate_checks": results,
                "checked_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Deduplication complete: {status} ({action})")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error in deduplication pipeline: {e}")
            return {
                "status": "error",
                "action": "proceed_to_validation",  # Fail open
                "is_duplicate": False,
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    def _duplicate_match_to_dict(self, match: DuplicateMatch) -> Dict[str, Any]:
        """Convert DuplicateMatch object to dictionary"""
        return {
            "is_duplicate": match.is_duplicate,
            "match_type": match.match_type,
            "similarity_score": match.similarity_score,
            "existing_opportunity_id": match.existing_opportunity_id,
            "existing_url": match.existing_url,
            "reason": match.reason
        }
    
    def _extract_existing_id(self, results: Dict[str, Any]) -> Optional[int]:
        """Extract the existing opportunity ID from duplicate results"""
        for check_result in results.values():
            if check_result["is_duplicate"] and check_result["existing_opportunity_id"]:
                return check_result["existing_opportunity_id"]
        return None
    
    def _get_primary_match(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the primary/strongest duplicate match"""
        # Priority order: exact_content > exact_url > semantic_similarity > metadata_similarity > similar_url
        priority_order = [
            "exact_content", "exact_url", "semantic_similarity", 
            "metadata_similarity", "similar_url"
        ]
        
        for match_type in priority_order:
            for check_result in results.values():
                if check_result["is_duplicate"] and check_result["match_type"] == match_type:
                    return check_result
        
        # If no prioritized match found, return first duplicate
        for check_result in results.values():
            if check_result["is_duplicate"]:
                return check_result
        
        return None
    
    async def store_deduplication_result(self, opportunity_id: int, results: Dict[str, Any]) -> None:
        """Store deduplication results in database for analysis"""
        try:
            db = await get_database()
            
            await db.execute(
                """
                INSERT INTO deduplication_logs 
                (opportunity_id, results, checked_at, is_duplicate, action_taken)
                VALUES ($1, $2, $3, $4, $5)
                """,
                opportunity_id,
                results,  # Store full JSON results
                datetime.now(),
                results.get("is_duplicate", False),
                results.get("action", "unknown")
            )
            
        except Exception as e:
            self.logger.error(f"Error storing deduplication result: {e}")
    
    async def get_deduplication_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get deduplication statistics for the specified period"""
        try:
            db = await get_database()
            
            stats = await db.fetch_one(
                """
                SELECT 
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN is_duplicate THEN 1 ELSE 0 END) as duplicates_found,
                    SUM(CASE WHEN action_taken = 'reject_before_validation' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN action_taken = 'proceed_to_validation' THEN 1 ELSE 0 END) as proceeded
                FROM deduplication_logs 
                WHERE checked_at > $1
                """,
                datetime.now() - timedelta(days=days)
            )
            
            # Get breakdown by match type
            match_types = await db.fetch_all(
                """
                SELECT 
                    results->>'primary_match_type' as match_type,
                    COUNT(*) as count
                FROM deduplication_logs 
                WHERE checked_at > $1 AND is_duplicate = true
                GROUP BY results->>'primary_match_type'
                ORDER BY count DESC
                """,
                datetime.now() - timedelta(days=days)
            )
            
            return {
                "period_days": days,
                "total_checks": stats["total_checks"] or 0,
                "duplicates_found": stats["duplicates_found"] or 0,
                "duplicates_rejected": stats["rejected"] or 0,
                "unique_opportunities": stats["proceeded"] or 0,
                "duplicate_rate": (stats["duplicates_found"] / stats["total_checks"]) if stats["total_checks"] > 0 else 0,
                "match_type_breakdown": [
                    {"match_type": row["match_type"], "count": row["count"]}
                    for row in match_types
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting deduplication stats: {e}")
            return {"error": str(e)}


async def test_deduplication_pipeline():
    """Test function for the deduplication pipeline"""
    # Create test opportunity
    test_opportunity = OpportunityContent(
        url="https://example.org/funding/ai-research-grant-2025",
        title="AI Research Grant for African Universities",
        description="Funding opportunity for artificial intelligence research projects in African universities, focusing on healthcare applications.",
        organization="Example Foundation",
        amount=50000.0,
        currency="USD",
        deadline=datetime(2025, 12, 31)
    )
    
    # Test deduplication
    pipeline = DeduplicationPipeline()
    results = await pipeline.check_for_duplicates(test_opportunity)
    
    print("Deduplication Test Results:")
    print(f"Status: {results['status']}")
    print(f"Action: {results['action']}")
    print(f"Is Duplicate: {results['is_duplicate']}")
    
    for check_name, check_result in results["duplicate_checks"].items():
        print(f"\n{check_name}:")
        print(f"  - Is Duplicate: {check_result['is_duplicate']}")
        print(f"  - Match Type: {check_result['match_type']}")
        if check_result.get('similarity_score'):
            print(f"  - Similarity: {check_result['similarity_score']:.3f}")
        if check_result.get('reason'):
            print(f"  - Reason: {check_result['reason']}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_deduplication_pipeline())
