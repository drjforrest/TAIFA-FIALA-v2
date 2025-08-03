"""
Enhanced Duplicate Detection System
===================================

Advanced duplicate detection specifically designed to handle:
1. Multiple articles about the same funding announcement
2. Press releases vs actual intelligence feed
3. Temporal duplicate detection (same opportunity posted at different times)
4. Source linking and original opportunity tracking
5. Semantic similarity beyond simple text matching

This system addresses the specific issue of "funding announcements" being 
ingested as separate opportunities when they're actually the same story.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import re
from urllib.parse import urlparse, parse_qs
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DUPLICATE DETECTION MODELS
# =============================================================================

class DuplicateType(Enum):
    """Types of duplicates detected"""
    EXACT_MATCH = "exact_match"
    TITLE_SIMILARITY = "title_similarity"
    CONTENT_SIMILARITY = "content_similarity"
    URL_MATCH = "url_match"
    SEMANTIC_MATCH = "semantic_match"
    TEMPORAL_CLUSTER = "temporal_cluster"
    ORGANIZATION_FUNDING_MATCH = "organization_funding_match"
    ANNOUNCEMENT_CHAIN = "announcement_chain"

class DuplicateAction(Enum):
    """Actions to take for duplicates"""
    REJECT = "reject"
    MERGE = "merge"
    MARK_RELATED = "mark_related"
    ENHANCE_ORIGINAL = "enhance_original"
    MANUAL_REVIEW = "manual_review"

@dataclass
class DuplicateMatch:
    """Represents a duplicate match"""
    original_id: str
    duplicate_id: str
    duplicate_type: DuplicateType
    confidence_score: float
    similarity_score: float
    action: DuplicateAction
    details: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'original_id': self.original_id,
            'duplicate_id': self.duplicate_id,
            'duplicate_type': self.duplicate_type.value,
            'confidence_score': self.confidence_score,
            'similarity_score': self.similarity_score,
            'action': self.action.value,
            'details': self.details,
            'detected_at': self.detected_at.isoformat()
        }

@dataclass
class ContentFingerprint:
    """Unique fingerprint for content identification"""
    content_id: str
    title_hash: str
    content_hash: str
    semantic_hash: str
    organization_name: str
    funding_amount: Optional[float] = None
    funding_currency: Optional[str] = None
    announcement_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    url_domain: Optional[str] = None
    key_phrases: List[str] = field(default_factory=list)
    
    def generate_signature(self) -> str:
        """Generate unique signature for matching"""
        signature_parts = [
            self.title_hash,
            self.organization_name.lower().strip(),
            str(self.funding_amount or 0),
            self.funding_currency or 'unknown'
        ]
        
        signature = '|'.join(signature_parts)
        return hashlib.md5(signature.encode()).hexdigest()

# =============================================================================
# ENHANCED DUPLICATE DETECTOR
# =============================================================================

class EnhancedDuplicateDetector:
    """Enhanced duplicate detection with multiple strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Detection thresholds
        self.exact_match_threshold = 0.95
        self.title_similarity_threshold = 0.85
        self.content_similarity_threshold = 0.80
        self.semantic_similarity_threshold = 0.75
        self.temporal_window_hours = 72  # 3 days
        
        # Caches
        self.content_fingerprints = {}
        self.organization_funding_map = {}
        self.announcement_chains = {}
        
        # Patterns for extracting funding information
        self.funding_amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|k|thousand)?',
            r'([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|k|thousand)?\s*dollars?',
            r'USD\s*([0-9,]+(?:\.[0-9]+)?)',
            r'€([0-9,]+(?:\.[0-9]+)?)',
            r'£([0-9,]+(?:\.[0-9]+)?)',
        ]
        
        # Organization name extraction patterns
        self.organization_patterns = [
            r'(?:funded by|grant from|investment from|backed by)\s+([A-Z][a-zA-Z\s&]+)',
            r'([A-Z][a-zA-Z\s&]+)\s+(?:announces|provides|awards|grants)',
            r'([A-Z][a-zA-Z\s&]+)\s+(?:Foundation|Fund|Capital|Ventures|Partners)',
        ]
    
    async def detect_duplicates(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Detect duplicates using multiple strategies"""
        matches = []
        
        try:
            # Generate fingerprint for new content
            new_fingerprint = await self._generate_fingerprint(new_content)
            
            # Strategy 1: Exact signature matching
            signature_matches = await self._check_signature_matches(new_fingerprint, existing_content)
            matches.extend(signature_matches)
            
            # Strategy 2: Title similarity with context
            title_matches = await self._check_title_similarity(new_content, existing_content)
            matches.extend(title_matches)
            
            # Strategy 3: Content similarity
            content_matches = await self._check_content_similarity(new_content, existing_content)
            matches.extend(content_matches)
            
            # Strategy 4: Semantic similarity using AI
            semantic_matches = await self._check_semantic_similarity(new_content, existing_content)
            matches.extend(semantic_matches)
            
            # Strategy 5: Temporal clustering
            temporal_matches = await self._check_temporal_clustering(new_content, existing_content)
            matches.extend(temporal_matches)
            
            # Strategy 6: Organization-funding matching
            org_matches = await self._check_organization_funding_match(new_content, existing_content)
            matches.extend(org_matches)
            
            # Strategy 7: Announcement chain detection
            chain_matches = await self._check_announcement_chains(new_content, existing_content)
            matches.extend(chain_matches)
            
            # Remove duplicates and sort by confidence
            unique_matches = self._deduplicate_matches(matches)
            unique_matches.sort(key=lambda x: x.confidence_score, reverse=True)
            
            return unique_matches
            
        except Exception as e:
            self.logger.error(f"Duplicate detection failed: {e}")
            return []
    
    async def _generate_fingerprint(self, content: Dict[str, Any]) -> ContentFingerprint:
        """Generate content fingerprint"""
        try:
            title = content.get('title', '').strip()
            description = content.get('description', '').strip()
            url = content.get('url', content.get('link', ''))
            
            # Generate hashes
            title_hash = hashlib.md5(title.lower().encode()).hexdigest()
            content_hash = hashlib.md5(f"{title} {description}".lower().encode()).hexdigest()
            
            # Extract funding information
            funding_amount = await self._extract_funding_amount(f"{title} {description}")
            funding_currency = await self._extract_currency(f"{title} {description}")
            
            # Extract organization name
            organization_name = await self._extract_organization_name(f"{title} {description}")
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(f"{title} {description}")
            
            # Generate semantic hash using AI
            semantic_hash = await self._generate_semantic_hash(f"{title} {description}")
            
            # Extract dates
            announcement_date = content.get('published_date') or content.get('created_at')
            deadline_date = content.get('deadline')
            
            # URL domain
            url_domain = urlparse(url).netloc if url else None
            
            return ContentFingerprint(
                content_id=content.get('id', str(uuid.uuid4())),
                title_hash=title_hash,
                content_hash=content_hash,
                semantic_hash=semantic_hash,
                organization_name=organization_name,
                funding_amount=funding_amount,
                funding_currency=funding_currency,
                announcement_date=announcement_date,
                deadline_date=deadline_date,
                url_domain=url_domain,
                key_phrases=key_phrases
            )
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            return ContentFingerprint(
                content_id=content.get('id', str(uuid.uuid4())),
                title_hash='',
                content_hash='',
                semantic_hash='',
                organization_name='',
            )
    
    async def _check_signature_matches(self, new_fingerprint: ContentFingerprint, existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check for exact signature matches"""
        matches = []
        
        try:
            new_signature = new_fingerprint.generate_signature()
            
            for existing in existing_content:
                existing_fingerprint = await self._generate_fingerprint(existing)
                existing_signature = existing_fingerprint.generate_signature()
                
                if new_signature == existing_signature:
                    matches.append(DuplicateMatch(
                        original_id=existing.get('id'),
                        duplicate_id=new_fingerprint.content_id,
                        duplicate_type=DuplicateType.EXACT_MATCH,
                        confidence_score=0.95,
                        similarity_score=1.0,
                        action=DuplicateAction.REJECT,
                        details={
                            'signature': new_signature,
                            'match_type': 'exact_signature'
                        }
                    ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Signature matching failed: {e}")
            return []
    
    async def _check_title_similarity(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check title similarity with context awareness"""
        matches = []
        
        try:
            from difflib import SequenceMatcher
            
            new_title = new_content.get('title', '').strip().lower()
            
            for existing in existing_content:
                existing_title = existing.get('title', '').strip().lower()
                
                # Calculate similarity
                similarity = SequenceMatcher(None, new_title, existing_title).ratio()
                
                if similarity >= self.title_similarity_threshold:
                    # Additional context checks
                    org_match = await self._check_organization_context(new_content, existing)
                    amount_match = await self._check_funding_amount_context(new_content, existing)
                    
                    confidence = similarity * 0.7 + org_match * 0.2 + amount_match * 0.1
                    
                    if confidence >= 0.75:
                        action = DuplicateAction.REJECT if confidence >= 0.9 else DuplicateAction.MANUAL_REVIEW
                        
                        matches.append(DuplicateMatch(
                            original_id=existing.get('id'),
                            duplicate_id=new_content.get('id'),
                            duplicate_type=DuplicateType.TITLE_SIMILARITY,
                            confidence_score=confidence,
                            similarity_score=similarity,
                            action=action,
                            details={
                                'title_similarity': similarity,
                                'org_match': org_match,
                                'amount_match': amount_match
                            }
                        ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Title similarity check failed: {e}")
            return []
    
    async def _check_content_similarity(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check content similarity using TF-IDF and cosine similarity"""
        matches = []
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            new_text = f"{new_content.get('title', '')} {new_content.get('description', '')}"
            
            # Prepare text corpus
            texts = [new_text]
            existing_texts = []
            existing_ids = []
            
            for existing in existing_content:
                existing_text = f"{existing.get('title', '')} {existing.get('description', '')}"
                texts.append(existing_text)
                existing_texts.append(existing_text)
                existing_ids.append(existing.get('id'))
            
            if not existing_texts:
                return matches
            
            # Calculate TF-IDF
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=1000,
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Find matches above threshold
            for i, similarity in enumerate(similarities):
                if similarity >= self.content_similarity_threshold:
                    confidence = similarity * 0.8  # Slight penalty for content-only match
                    
                    action = DuplicateAction.REJECT if confidence >= 0.85 else DuplicateAction.MANUAL_REVIEW
                    
                    matches.append(DuplicateMatch(
                        original_id=existing_ids[i],
                        duplicate_id=new_content.get('id'),
                        duplicate_type=DuplicateType.CONTENT_SIMILARITY,
                        confidence_score=confidence,
                        similarity_score=similarity,
                        action=action,
                        details={
                            'content_similarity': similarity,
                            'vector_features': len(vectorizer.vocabulary_)
                        }
                    ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Content similarity check failed: {e}")
            return []
    
    async def _check_semantic_similarity(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check semantic similarity using AI"""
        matches = []
        
        try:
            import openai
            
            client = openai.AsyncOpenAI()
            
            new_text = f"{new_content.get('title', '')} {new_content.get('description', '')}"
            
            for existing in existing_content:
                existing_text = f"{existing.get('title', '')} {existing.get('description', '')}"
                
                # Use AI to check semantic similarity
                prompt = f"""
                Compare these two funding-related texts and determine if they refer to the same intelligence item:
                
                Text 1: {new_text}
                Text 2: {existing_text}
                
                Consider:
                1. Same organization providing funding
                2. Same funding program/initiative
                3. Similar funding amounts
                4. Similar deadlines or timeframes
                5. Similar eligibility criteria
                
                Return JSON with:
                {{
                    "is_same_opportunity": true/false,
                    "confidence": 0.0-1.0,
                    "reasoning": "explanation"
                }}
                """
                
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.1
                )
                
                result = json.loads(response.choices[0].message.content)
                
                if result.get('is_same_opportunity') and result.get('confidence', 0) >= self.semantic_similarity_threshold:
                    confidence = result.get('confidence', 0)
                    
                    action = DuplicateAction.REJECT if confidence >= 0.9 else DuplicateAction.MANUAL_REVIEW
                    
                    matches.append(DuplicateMatch(
                        original_id=existing.get('id'),
                        duplicate_id=new_content.get('id'),
                        duplicate_type=DuplicateType.SEMANTIC_MATCH,
                        confidence_score=confidence,
                        similarity_score=confidence,
                        action=action,
                        details={
                            'ai_reasoning': result.get('reasoning'),
                            'semantic_confidence': confidence
                        }
                    ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Semantic similarity check failed: {e}")
            return []
    
    async def _check_temporal_clustering(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check for temporal clustering of similar content"""
        matches = []
        
        try:
            new_date = new_content.get('published_date') or new_content.get('created_at')
            if not new_date:
                return matches
            
            if isinstance(new_date, str):
                new_date = datetime.fromisoformat(new_date.replace('Z', '+00:00'))
            
            new_title = new_content.get('title', '').lower()
            
            for existing in existing_content:
                existing_date = existing.get('published_date') or existing.get('created_at')
                if not existing_date:
                    continue
                
                if isinstance(existing_date, str):
                    existing_date = datetime.fromisoformat(existing_date.replace('Z', '+00:00'))
                
                # Check if within temporal window
                time_diff = abs((new_date - existing_date).total_seconds() / 3600)
                
                if time_diff <= self.temporal_window_hours:
                    # Check if similar content within time window
                    existing_title = existing.get('title', '').lower()
                    
                    # Simple similarity check
                    common_words = set(new_title.split()) & set(existing_title.split())
                    title_similarity = len(common_words) / max(len(new_title.split()), len(existing_title.split()))
                    
                    if title_similarity >= 0.5:  # Lower threshold for temporal clustering
                        confidence = title_similarity * 0.6 + (1 - time_diff / self.temporal_window_hours) * 0.4
                        
                        if confidence >= 0.6:
                            matches.append(DuplicateMatch(
                                original_id=existing.get('id'),
                                duplicate_id=new_content.get('id'),
                                duplicate_type=DuplicateType.TEMPORAL_CLUSTER,
                                confidence_score=confidence,
                                similarity_score=title_similarity,
                                action=DuplicateAction.MANUAL_REVIEW,
                                details={
                                    'time_diff_hours': time_diff,
                                    'title_similarity': title_similarity,
                                    'temporal_confidence': confidence
                                }
                            ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Temporal clustering check failed: {e}")
            return []
    
    async def _check_organization_funding_match(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check for same organization providing similar funding"""
        matches = []
        
        try:
            new_org = await self._extract_organization_name(f"{new_content.get('title', '')} {new_content.get('description', '')}")
            new_amount = await self._extract_funding_amount(f"{new_content.get('title', '')} {new_content.get('description', '')}")
            
            if not new_org:
                return matches
            
            for existing in existing_content:
                existing_org = await self._extract_organization_name(f"{existing.get('title', '')} {existing.get('description', '')}")
                existing_amount = await self._extract_funding_amount(f"{existing.get('title', '')} {existing.get('description', '')}")
                
                if existing_org and new_org.lower() == existing_org.lower():
                    # Same organization
                    amount_match = 0.0
                    if new_amount and existing_amount:
                        amount_ratio = min(new_amount, existing_amount) / max(new_amount, existing_amount)
                        amount_match = amount_ratio if amount_ratio >= 0.8 else 0.0
                    
                    confidence = 0.7 + amount_match * 0.3
                    
                    if confidence >= 0.7:
                        matches.append(DuplicateMatch(
                            original_id=existing.get('id'),
                            duplicate_id=new_content.get('id'),
                            duplicate_type=DuplicateType.ORGANIZATION_FUNDING_MATCH,
                            confidence_score=confidence,
                            similarity_score=confidence,
                            action=DuplicateAction.MANUAL_REVIEW,
                            details={
                                'organization': new_org,
                                'new_amount': new_amount,
                                'existing_amount': existing_amount,
                                'amount_match': amount_match
                            }
                        ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Organization funding match check failed: {e}")
            return []
    
    async def _check_announcement_chains(self, new_content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> List[DuplicateMatch]:
        """Check for announcement chains (multiple articles about same announcement)"""
        matches = []
        
        try:
            # Look for announcement indicators
            announcement_indicators = [
                'announces', 'announced', 'receives funding', 'awarded', 'secures',
                'gets funding', 'funding round', 'investment round', 'raises'
            ]
            
            new_text = f"{new_content.get('title', '')} {new_content.get('description', '')}".lower()
            
            is_announcement = any(indicator in new_text for indicator in announcement_indicators)
            
            if is_announcement:
                # Check if similar announcements exist
                for existing in existing_content:
                    existing_text = f"{existing.get('title', '')} {existing.get('description', '')}".lower()
                    
                    existing_is_announcement = any(indicator in existing_text for indicator in announcement_indicators)
                    
                    if existing_is_announcement:
                        # Check for common entities (organizations, amounts, etc.)
                        new_org = await self._extract_organization_name(new_text)
                        existing_org = await self._extract_organization_name(existing_text)
                        
                        if new_org and existing_org and new_org.lower() == existing_org.lower():
                            confidence = 0.8  # High confidence for announcement chains
                            
                            matches.append(DuplicateMatch(
                                original_id=existing.get('id'),
                                duplicate_id=new_content.get('id'),
                                duplicate_type=DuplicateType.ANNOUNCEMENT_CHAIN,
                                confidence_score=confidence,
                                similarity_score=confidence,
                                action=DuplicateAction.MARK_RELATED,
                                details={
                                    'organization': new_org,
                                    'announcement_type': 'funding_announcement'
                                }
                            ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Announcement chain check failed: {e}")
            return []
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    async def _extract_funding_amount(self, text: str) -> Optional[float]:
        """Extract funding amount from text"""
        try:
            for pattern in self.funding_amount_patterns:
                match = re.search(pattern, text.lower())
                if match:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Handle multipliers
                    if len(match.groups()) > 1:
                        multiplier = match.group(2)
                        if multiplier in ['million', 'm']:
                            amount *= 1000000
                        elif multiplier in ['billion', 'b']:
                            amount *= 1000000000
                        elif multiplier in ['thousand', 'k']:
                            amount *= 1000
                    
                    return amount
            
            return None
            
        except Exception as e:
            self.logger.error(f"Funding amount extraction failed: {e}")
            return None
    
    async def _extract_currency(self, text: str) -> Optional[str]:
        """Extract currency from text"""
        try:
            currency_patterns = [
                r'USD|US\$|\$',
                r'EUR|€',
                r'GBP|£',
                r'CAD|C\$',
                r'AUD|A\$'
            ]
            
            for pattern in currency_patterns:
                if re.search(pattern, text):
                    return pattern.replace('\\', '')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Currency extraction failed: {e}")
            return None
    
    async def _extract_organization_name(self, text: str) -> str:
        """Extract organization name from text"""
        try:
            for pattern in self.organization_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    org_name = match.group(1).strip()
                    if len(org_name) > 3:  # Minimum length check
                        return org_name
            
            return ''
            
        except Exception as e:
            self.logger.error(f"Organization name extraction failed: {e}")
            return ''
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        try:
            # Simple keyword extraction
            keywords = [
                'funding', 'grant', 'investment', 'venture capital',
                'accelerator', 'incubator', 'startup', 'entrepreneur',
                'artificial intelligence', 'machine learning', 'AI', 'ML',
                'technology', 'innovation', 'research', 'development'
            ]
            
            found_phrases = []
            text_lower = text.lower()
            
            for keyword in keywords:
                if keyword in text_lower:
                    found_phrases.append(keyword)
            
            return found_phrases
            
        except Exception as e:
            self.logger.error(f"Key phrase extraction failed: {e}")
            return []
    
    async def _generate_semantic_hash(self, text: str) -> str:
        """Generate semantic hash using AI"""
        try:
            # Simple semantic hash based on key concepts
            # In production, this could use embeddings
            key_concepts = await self._extract_key_phrases(text)
            concept_string = '|'.join(sorted(key_concepts))
            return hashlib.md5(concept_string.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Semantic hash generation failed: {e}")
            return hashlib.md5(text.encode()).hexdigest()
    
    async def _check_organization_context(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> float:
        """Check if organizations match between two pieces of content"""
        try:
            org1 = await self._extract_organization_name(f"{content1.get('title', '')} {content1.get('description', '')}")
            org2 = await self._extract_organization_name(f"{content2.get('title', '')} {content2.get('description', '')}")
            
            if org1 and org2:
                return 1.0 if org1.lower() == org2.lower() else 0.0
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Organization context check failed: {e}")
            return 0.0
    
    async def _check_funding_amount_context(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> float:
        """Check if funding amounts match between two pieces of content"""
        try:
            amount1 = await self._extract_funding_amount(f"{content1.get('title', '')} {content1.get('description', '')}")
            amount2 = await self._extract_funding_amount(f"{content2.get('title', '')} {content2.get('description', '')}")
            
            if amount1 and amount2:
                ratio = min(amount1, amount2) / max(amount1, amount2)
                return ratio if ratio >= 0.8 else 0.0
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Funding amount context check failed: {e}")
            return 0.0
    
    def _deduplicate_matches(self, matches: List[DuplicateMatch]) -> List[DuplicateMatch]:
        """Remove duplicate matches"""
        seen = set()
        unique_matches = []
        
        for match in matches:
            key = (match.original_id, match.duplicate_id)
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of enhanced duplicate detection"""
    detector = EnhancedDuplicateDetector()
    
    # New content to check
    new_content = {
        'id': 'new_123',
        'title': 'Microsoft announces $100M AI for Good initiative',
        'description': 'Microsoft Corporation today announced a new $100 million funding initiative called AI for Good, designed to support startups developing AI solutions for social impact.',
        'published_date': '2024-01-15T10:00:00Z'
    }
    
    # Existing content in database
    existing_content = [
        {
            'id': 'existing_456',
            'title': 'Microsoft launches AI for Good program with $100M funding',
            'description': 'Tech giant Microsoft has launched its AI for Good program, providing $100 million in funding for AI startups focused on social impact.',
            'published_date': '2024-01-14T15:30:00Z'
        }
    ]
    
    # Detect duplicates
    matches = await detector.detect_duplicates(new_content, existing_content)
    
    for match in matches:
        print(f"Duplicate detected: {match.duplicate_type.value}")
        print(f"Confidence: {match.confidence_score:.3f}")
        print(f"Action: {match.action.value}")
        print(f"Details: {match.details}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(example_usage())