"""
Targeted Search Service for Missing Innovation Values
===================================================

This service uses Serper.dev API to perform highly targeted searches for specific missing values.
It's designed to be cost-efficient and focused on specific data points like investment amounts,
contact information, URLs, and other structured data.

The service implements conditional triggering to avoid expensive searches for low-priority data.
"""

import asyncio
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from services.serper_service import SerperService, SearchResult


class SearchCondition(Enum):
    """Conditions that trigger targeted searches"""
    MISSING_FUNDING_WITH_MENTIONS = "missing_funding_with_mentions"  # Has funding mentions but no amount
    VERIFIED_INNOVATION_MISSING_WEBSITE = "verified_innovation_missing_website"  # Verified but no website
    HIGH_IMPACT_MISSING_METRICS = "high_impact_missing_metrics"  # High user count mentions but no metrics
    RECENT_NEWS_MISSING_DETAILS = "recent_news_missing_details"  # Recent mentions but missing key details


@dataclass
class TargetedSearchQuery:
    """Represents a targeted search query for specific missing data"""
    innovation_id: str
    innovation_name: str
    field_name: str
    search_terms: List[str]
    extraction_patterns: List[str]
    condition: SearchCondition
    max_cost: float
    expected_value_type: str  # 'amount', 'url', 'text', 'number'


@dataclass
class SearchTriggering:
    """Determines if a targeted search should be triggered"""
    should_trigger: bool
    reason: str
    confidence: float
    estimated_value: float  # Expected value of the data
    cost_benefit_ratio: float


@dataclass
class TargetedSearchResult:
    """Result of a targeted search operation"""
    innovation_id: str
    field_name: str
    extracted_value: Any
    confidence_score: float
    supporting_evidence: List[str]
    search_cost: float
    extraction_method: str
    validation_notes: str


class TargetedSearchService:
    """Service for cost-efficient targeted searches for missing innovation data"""
    
    def __init__(self):
        self.serper_service = None
        self.search_history: Dict[str, List[datetime]] = {}  # Track search frequency
        self.daily_budget = 20.0  # $20 per day for targeted searches
        self.current_daily_spend = 0.0
        
    async def __aenter__(self):
        self.serper_service = SerperService()
        await self.serper_service.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.serper_service:
            await self.serper_service.__aexit__(exc_type, exc_val, exc_tb)
    
    def should_trigger_search(self, innovation: Dict[str, Any], field_name: str) -> SearchTriggering:
        """Determine if a targeted search should be triggered based on conditions"""
        
        innovation_name = innovation.get('title', '').lower()
        description = innovation.get('description', '').lower()
        combined_text = f"{innovation_name} {description}"
        
        # Check for funding-related searches
        if field_name == 'funding_amount':
            return self._check_funding_search_conditions(innovation, combined_text)
        
        # Check for website URL searches
        elif field_name == 'website_url':
            return self._check_website_search_conditions(innovation, combined_text)
        
        # Check for investment details
        elif field_name == 'investment_details':
            return self._check_investment_search_conditions(innovation, combined_text)
        
        # Check for user metrics
        elif field_name == 'user_metrics':
            return self._check_metrics_search_conditions(innovation, combined_text)
        
        # Check for contact information
        elif field_name == 'contact_info':
            return self._check_contact_search_conditions(innovation, combined_text)
        
        return SearchTriggering(
            should_trigger=False,
            reason="No triggering conditions met",
            confidence=0.0,
            estimated_value=0.0,
            cost_benefit_ratio=0.0
        )
    
    def _check_funding_search_conditions(self, innovation: Dict[str, Any], text: str) -> SearchTriggering:
        """Check conditions for funding amount searches"""
        
        # High-value condition: Mentions funding/investment but no amount recorded
        funding_mentions = [
            'funding', 'investment', 'raised', 'series', 'round', 'million', 'investor'
        ]
        
        has_funding_mentions = any(mention in text for mention in funding_mentions)
        has_recorded_funding = bool(innovation.get('fundings') and len(innovation.get('fundings', [])) > 0)
        is_verified = innovation.get('verification_status') == 'verified'
        
        if has_funding_mentions and not has_recorded_funding:
            confidence = 0.8 if is_verified else 0.6
            estimated_value = 100.0  # High value for funding information
            
            return SearchTriggering(
                should_trigger=True,
                reason="Has funding mentions but no recorded funding amount",
                confidence=confidence,
                estimated_value=estimated_value,
                cost_benefit_ratio=estimated_value / 0.10  # $0.10 search cost
            )
        
        return SearchTriggering(False, "No funding search conditions met", 0.0, 0.0, 0.0)
    
    def _check_website_search_conditions(self, innovation: Dict[str, Any], text: str) -> SearchTriggering:
        """Check conditions for website URL searches"""
        
        is_verified = innovation.get('verification_status') == 'verified'
        has_website = bool(innovation.get('website_url'))
        has_company_mentions = any(term in text for term in ['company', 'startup', 'platform', 'app'])
        
        if is_verified and not has_website and has_company_mentions:
            return SearchTriggering(
                should_trigger=True,
                reason="Verified innovation missing website URL",
                confidence=0.7,
                estimated_value=50.0,
                cost_benefit_ratio=50.0 / 0.05  # $0.05 search cost
            )
        
        return SearchTriggering(False, "No website search conditions met", 0.0, 0.0, 0.0)
    
    def _check_investment_search_conditions(self, innovation: Dict[str, Any], text: str) -> SearchTriggering:
        """Check conditions for detailed investment information searches"""
        
        # Look for specific investment patterns that suggest more details are available
        investment_indicators = [
            'led by', 'participated', 'venture capital', 'vc', 'angel investor',
            'pre-seed', 'seed round', 'series a', 'series b'
        ]
        
        has_investment_details = any(indicator in text for indicator in investment_indicators)
        has_funding_recorded = bool(innovation.get('fundings'))
        
        if has_investment_details and not has_funding_recorded:
            return SearchTriggering(
                should_trigger=True,
                reason="Detailed investment mentions without recorded funding",
                confidence=0.75,
                estimated_value=80.0,
                cost_benefit_ratio=80.0 / 0.12  # $0.12 search cost
            )
        
        return SearchTriggering(False, "No investment search conditions met", 0.0, 0.0, 0.0)
    
    def _check_metrics_search_conditions(self, innovation: Dict[str, Any], text: str) -> SearchTriggering:
        """Check conditions for user metrics searches"""
        
        metrics_indicators = [
            'users', 'customers', 'downloads', 'active', 'million users',
            'thousand users', 'user base', 'subscribers'
        ]
        
        has_metrics_mentions = any(indicator in text for indicator in metrics_indicators)
        has_recorded_metrics = bool(innovation.get('impact_metrics', {}).get('users_reached'))
        
        if has_metrics_mentions and not has_recorded_metrics:
            return SearchTriggering(
                should_trigger=True,
                reason="User metrics mentioned but not recorded",
                confidence=0.6,
                estimated_value=30.0,
                cost_benefit_ratio=30.0 / 0.08  # $0.08 search cost
            )
        
        return SearchTriggering(False, "No metrics search conditions met", 0.0, 0.0, 0.0)
    
    def _check_contact_search_conditions(self, innovation: Dict[str, Any], text: str) -> SearchTriggering:
        """Check conditions for contact information searches"""
        
        has_organizations = bool(innovation.get('organizations') and len(innovation.get('organizations', [])) > 0)
        has_individuals = bool(innovation.get('individuals') and len(innovation.get('individuals', [])) > 0)
        is_verified = innovation.get('verification_status') == 'verified'
        
        if is_verified and not (has_organizations or has_individuals):
            return SearchTriggering(
                should_trigger=True,
                reason="Verified innovation missing contact information",
                confidence=0.65,
                estimated_value=40.0,
                cost_benefit_ratio=40.0 / 0.07  # $0.07 search cost
            )
        
        return SearchTriggering(False, "No contact search conditions met", 0.0, 0.0, 0.0)
    
    async def perform_targeted_search(self, innovation: Dict[str, Any], field_name: str) -> Optional[TargetedSearchResult]:
        """Perform a targeted search for a specific missing field"""
        
        # Check if search should be triggered
        trigger_check = self.should_trigger_search(innovation, field_name)
        
        if not trigger_check.should_trigger:
            logger.info(f"Search not triggered for {field_name}: {trigger_check.reason}")
            return None
        
        # Check budget constraints
        search_cost = self._estimate_search_cost(field_name)
        if self.current_daily_spend + search_cost > self.daily_budget:
            logger.warning(f"Daily budget exceeded. Skipping search for {field_name}")
            return None
        
        logger.info(f"Performing targeted search for {field_name} (confidence: {trigger_check.confidence:.2f})")
        
        try:
            # Create targeted search query
            search_query = self._create_targeted_query(innovation, field_name)
            
            # Perform search
            search_results = await self.serper_service.search_web(search_query, num_results=15)
            
            if not search_results.results:
                logger.info(f"No search results found for {field_name}")
                return None
            
            # Extract specific value using field-specific patterns
            extracted_value = await self._extract_targeted_value(
                search_results.results, field_name, innovation
            )
            
            if extracted_value:
                self.current_daily_spend += search_cost
                
                return TargetedSearchResult(
                    innovation_id=innovation.get('id'),
                    field_name=field_name,
                    extracted_value=extracted_value['value'],
                    confidence_score=extracted_value['confidence'],
                    supporting_evidence=extracted_value.get('evidence', []),
                    search_cost=search_cost,
                    extraction_method='pattern_matching',
                    validation_notes=extracted_value.get('notes', '')
                )
            
        except Exception as e:
            logger.error(f"Error in targeted search for {field_name}: {e}")
            return None
    
    def _create_targeted_query(self, innovation: Dict[str, Any], field_name: str) -> str:
        """Create highly specific search query for the target field"""
        
        innovation_name = innovation.get('title', '')
        
        queries = {
            'funding_amount': f'"{innovation_name}" AND ("raised" OR "funding" OR "investment") AND ("million" OR "$")',
            'website_url': f'"{innovation_name}" AND ("website" OR "official" OR ".com" OR "platform")',
            'investment_details': f'"{innovation_name}" AND ("led by" OR "investor" OR "VC" OR "venture capital")',
            'user_metrics': f'"{innovation_name}" AND ("users" OR "customers" OR "downloads" OR "active")',
            'contact_info': f'"{innovation_name}" AND ("founded by" OR "CEO" OR "founder" OR "team")'
        }
        
        return queries.get(field_name, f'"{innovation_name}" {field_name}')
    
    async def _extract_targeted_value(self, results: List[SearchResult], field_name: str, innovation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract specific values using targeted patterns"""
        
        # Combine text from top results
        combined_text = " ".join([
            f"{result.title} {result.snippet}" 
            for result in results[:8]  # Use top 8 results
        ])
        
        if field_name == 'funding_amount':
            return self._extract_funding_amount(combined_text, results)
        
        elif field_name == 'website_url':
            return self._extract_website_url(combined_text, results, innovation.get('title', ''))
        
        elif field_name == 'investment_details':
            return self._extract_investment_details(combined_text, results)
        
        elif field_name == 'user_metrics':
            return self._extract_user_metrics(combined_text, results)
        
        elif field_name == 'contact_info':
            return self._extract_contact_info(combined_text, results)
        
        return None
    
    def _extract_funding_amount(self, text: str, results: List[SearchResult]) -> Optional[Dict[str, Any]]:
        """Extract funding amount with high precision"""
        
        # Advanced funding patterns
        patterns = [
            r'raised\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)(?:\s+in\s+(?:series\s+[A-Z]|seed|funding))?',
            r'(\d+(?:\.\d+)?)\s*(million|billion|M|B)\s+(?:in\s+)?(?:series\s+[A-Z]|seed|funding|investment)',
            r'funding\s+round\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'secured\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'investment\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)'
        ]
        
        best_match = None
        highest_confidence = 0.0
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                amount = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to USD
                if unit in ['billion', 'b']:
                    amount_usd = amount * 1000000000
                elif unit in ['million', 'm']:
                    amount_usd = amount * 1000000
                else:
                    amount_usd = amount
                
                # Calculate confidence based on pattern quality and context
                confidence = self._calculate_funding_confidence(match.group(), text, results)
                
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_match = {
                        'value': {
                            'amount': amount_usd,
                            'currency': 'USD',
                            'raw_text': match.group(),
                            'formatted_amount': f"${amount}{unit.upper()}"
                        },
                        'confidence': confidence,
                        'evidence': [match.group()],
                        'notes': f'Extracted using pattern: {pattern[:50]}...'
                    }
        
        return best_match if highest_confidence > 0.6 else None
    
    def _extract_website_url(self, text: str, results: List[SearchResult], innovation_name: str) -> Optional[Dict[str, Any]]:
        """Extract website URL with validation"""
        
        # Look for URLs in search results
        potential_urls = []
        
        for result in results:
            url = str(result.link)
            domain = url.split('/')[2] if '/' in url else url
            
            # Score URLs based on relevance to innovation name
            relevance_score = self._calculate_url_relevance(domain, innovation_name)
            
            if relevance_score > 0.3:
                potential_urls.append({
                    'url': url,
                    'domain': domain,
                    'relevance': relevance_score,
                    'title': result.title
                })
        
        if potential_urls:
            # Return the most relevant URL
            best_url = max(potential_urls, key=lambda x: x['relevance'])
            
            return {
                'value': best_url['url'],
                'confidence': min(0.9, best_url['relevance'] + 0.2),
                'evidence': [best_url['title']],
                'notes': f"Selected from {len(potential_urls)} potential URLs"
            }
        
        return None
    
    def _extract_investment_details(self, text: str, results: List[SearchResult]) -> Optional[Dict[str, Any]]:
        """Extract detailed investment information"""
        
        # Patterns for investor names and details
        investor_patterns = [
            r'led by\s+([A-Z][a-zA-Z\s&]+(?:Capital|Ventures|Partners|Fund|VC))',
            r'participated\s+by\s+([A-Z][a-zA-Z\s&]+(?:Capital|Ventures|Partners|Fund|VC))',
            r'invested\s+by\s+([A-Z][a-zA-Z\s&]+(?:Capital|Ventures|Partners|Fund|VC))',
            r'([A-Z][a-zA-Z\s&]+(?:Capital|Ventures|Partners|Fund|VC))\s+led\s+the'
        ]
        
        investors = []
        
        for pattern in investor_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                investor_name = match.group(1).strip()
                if len(investor_name) > 3 and investor_name not in investors:
                    investors.append(investor_name)
        
        if investors:
            return {
                'value': {
                    'investors': investors,
                    'lead_investor': investors[0] if investors else None
                },
                'confidence': 0.75,
                'evidence': investors,
                'notes': f"Found {len(investors)} investor mentions"
            }
        
        return None
    
    def _extract_user_metrics(self, text: str, results: List[SearchResult]) -> Optional[Dict[str, Any]]:
        """Extract user metrics and growth numbers"""
        
        metrics_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M)?\s+(?:active\s+)?users',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M)?\s+customers',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|thousand|K)?\s+downloads',
            r'user\s+base\s+of\s+(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M)?',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M)?\s+registered\s+users'
        ]
        
        metrics = {}
        
        for pattern in metrics_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                number_str = match.group(1).replace(',', '')
                number = float(number_str)
                
                # Determine metric type
                if 'user' in match.group().lower():
                    metrics['users_reached'] = number
                elif 'customer' in match.group().lower():
                    metrics['customers'] = number
                elif 'download' in match.group().lower():
                    metrics['downloads'] = number
        
        if metrics:
            return {
                'value': metrics,
                'confidence': 0.7,
                'evidence': list(metrics.keys()),
                'notes': f"Extracted {len(metrics)} metrics"
            }
        
        return None
    
    def _extract_contact_info(self, text: str, results: List[SearchResult]) -> Optional[Dict[str, Any]]:
        """Extract founder and team contact information"""
        
        founder_patterns = [
            r'founded\s+by\s+([A-Z][a-zA-Z\s]+?)(?:\s+and\s+([A-Z][a-zA-Z\s]+?))?',
            r'co-?founders?\s+([A-Z][a-zA-Z\s]+?)(?:\s+and\s+([A-Z][a-zA-Z\s]+?))?',
            r'CEO\s+([A-Z][a-zA-Z\s]+)',
            r'founder\s+([A-Z][a-zA-Z\s]+)'
        ]
        
        team_members = []
        
        for pattern in founder_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                for i in range(1, len(match.groups()) + 1):
                    name = match.group(i)
                    if name and len(name.strip()) > 2:
                        clean_name = name.strip().rstrip(',.')
                        if clean_name not in team_members:
                            team_members.append(clean_name)
        
        if team_members:
            return {
                'value': {
                    'team_members': team_members,
                    'founder': team_members[0] if team_members else None
                },
                'confidence': 0.65,
                'evidence': team_members,
                'notes': f"Found {len(team_members)} team member mentions"
            }
        
        return None
    
    def _calculate_funding_confidence(self, match_text: str, full_text: str, results: List[SearchResult]) -> float:
        """Calculate confidence score for funding extraction"""
        
        base_confidence = 0.6
        
        # Boost confidence for specific patterns
        if 'series' in match_text.lower():
            base_confidence += 0.15
        
        if any(word in match_text.lower() for word in ['raised', 'secured', 'completed']):
            base_confidence += 0.1
        
        # Boost for multiple sources
        if len(results) > 3:
            base_confidence += 0.05
        
        # Boost for recent dates
        if any(word in full_text.lower() for word in ['2024', '2023', 'recently']):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_url_relevance(self, domain: str, innovation_name: str) -> float:
        """Calculate relevance score for a URL domain"""
        
        domain_lower = domain.lower()
        name_lower = innovation_name.lower()
        
        # Direct name match
        if name_lower in domain_lower or any(word in domain_lower for word in name_lower.split()):
            return 0.9
        
        # Exclude common irrelevant domains
        irrelevant_domains = [
            'techcrunch.com', 'venturebeat.com', 'bloomberg.com', 'reuters.com',
            'facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com'
        ]
        
        if any(irrelevant in domain_lower for irrelevant in irrelevant_domains):
            return 0.1
        
        # African domain bonus
        african_tlds = ['.ng', '.ke', '.za', '.gh', '.eg', '.ma']
        if any(tld in domain_lower for tld in african_tlds):
            return 0.6
        
        return 0.3  # Default relevance
    
    def _estimate_search_cost(self, field_name: str) -> float:
        """Estimate the cost of a targeted search"""
        
        costs = {
            'funding_amount': 0.10,
            'website_url': 0.05,
            'investment_details': 0.12,
            'user_metrics': 0.08,
            'contact_info': 0.07
        }
        
        return costs.get(field_name, 0.06)
    
    async def batch_targeted_search(self, innovations: List[Dict[str, Any]], 
                                  max_searches: int = 20) -> List[TargetedSearchResult]:
        """Perform batch targeted searches with budget constraints"""
        
        logger.info(f"Starting batch targeted search for {len(innovations)} innovations")
        
        results = []
        searches_performed = 0
        
        # Priority order for field searches
        field_priority = ['funding_amount', 'website_url', 'investment_details', 'user_metrics', 'contact_info']
        
        for innovation in innovations:
            if searches_performed >= max_searches:
                break
            
            for field_name in field_priority:
                if searches_performed >= max_searches:
                    break
                
                # Check if field is missing
                if self._is_field_missing(innovation, field_name):
                    
                    result = await self.perform_targeted_search(innovation, field_name)
                    
                    if result:
                        results.append(result)
                        searches_performed += 1
                        logger.info(f"Found {field_name} for {innovation.get('title')}: ${result.search_cost:.3f}")
                    
                    # Rate limiting
                    await asyncio.sleep(1)
        
        logger.info(f"Completed {searches_performed} targeted searches, found {len(results)} results")
        return results
    
    def _is_field_missing(self, innovation: Dict[str, Any], field_name: str) -> bool:
        """Check if a specific field is missing from the innovation"""
        
        if field_name == 'funding_amount':
            return not (innovation.get('fundings') and len(innovation.get('fundings', [])) > 0)
        
        elif field_name == 'website_url':
            return not innovation.get('website_url')
        
        elif field_name == 'investment_details':
            return not (innovation.get('fundings') and any(
                funding.get('funder_name') for funding in innovation.get('fundings', [])
            ))
        
        elif field_name == 'user_metrics':
            return not innovation.get('impact_metrics', {}).get('users_reached')
        
        elif field_name == 'contact_info':
            return not (innovation.get('organizations') or innovation.get('individuals'))
        
        return False


# Convenience function for ETL pipeline
async def run_targeted_searches_for_innovations(innovations: List[Dict[str, Any]], 
                                              max_searches: int = 20) -> List[TargetedSearchResult]:
    """Run targeted searches for a batch of innovations"""
    
    async with TargetedSearchService() as search_service:
        return await search_service.batch_targeted_search(innovations, max_searches)


if __name__ == "__main__":
    # Test the targeted search service
    async def test_targeted_search():
        print("🎯 Testing Targeted Search Service")
        
        # Mock innovation with potential triggers
        test_innovation = {
            'id': 'test-456',
            'title': 'Paystack',
            'description': 'Nigerian fintech startup that was acquired by Stripe for millions',
            'verification_status': 'verified',
            'fundings': [],  # Missing despite description mentioning acquisition
            'website_url': None,  # Missing website
        }
        
        async with TargetedSearchService() as search_service:
            # Check funding search conditions
            funding_trigger = search_service.should_trigger_search(test_innovation, 'funding_amount')
            print(f"Funding search trigger: {funding_trigger.should_trigger} - {funding_trigger.reason}")
            
            # Check website search conditions  
            website_trigger = search_service.should_trigger_search(test_innovation, 'website_url')
            print(f"Website search trigger: {website_trigger.should_trigger} - {website_trigger.reason}")
    
    asyncio.run(test_targeted_search())