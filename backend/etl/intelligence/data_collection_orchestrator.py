"""
TAIFA-FIALA Data Collection Orchestrator
========================================

Mission: Coordinate all data collectors with clear missions for comprehensive
African AI innovation discovery and documentation.

This orchestrator manages the entire data collection pipeline, from intelligence
synthesis through deep extraction to database population.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import json

from .perplexity_african_ai import PerplexityAfricanAIModule, IntelligenceType
from .enhanced_crawl4ai import IntelligentCrawl4AIOrchestrator, ContentType, InnovationExtractionResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectorType(Enum):
    INTELLIGENCE_SYNTHESIS = "intelligence_synthesis"
    ACADEMIC_DISCOVERY = "academic_discovery" 
    INNOVATION_DISCOVERY = "innovation_discovery"
    NEWS_MONITORING = "news_monitoring"
    COMMUNITY_SIGNALS = "community_signals"


class PriorityLevel(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BATCH = "batch"


@dataclass
class CollectionTarget:
    """Represents a target for data collection"""
    id: str
    url: str
    content_type: ContentType
    priority: PriorityLevel
    source_collector: CollectorType
    metadata: Dict[str, Any]
    discovered_at: datetime
    processed_at: Optional[datetime] = None
    extraction_result: Optional[InnovationExtractionResult] = None


@dataclass
class CollectionCycleResult:
    """Results from a complete collection cycle"""
    cycle_id: str
    start_time: datetime
    end_time: datetime
    targets_discovered: int
    targets_processed: int
    innovations_extracted: int
    database_records_created: int
    errors_encountered: List[str]
    recommendations: List[str]


class DataCollectionOrchestrator:
    """Master orchestrator for all TAIFA-FIALA data collection activities"""
    
    def __init__(self, perplexity_api_key: str, openai_api_key: str):
        self.perplexity_api_key = perplexity_api_key
        self.openai_api_key = openai_api_key
        
        # Initialize core modules
        self.intelligence_module = None
        self.extraction_orchestrator = None
        
        # Collection state
        self.active_targets: List[CollectionTarget] = []
        self.collection_history: List[CollectionCycleResult] = []
        
        # Content type mapping
        self.content_type_mapping = {
            "github.com": ContentType.GITHUB_REPOSITORY,
            "arxiv.org": ContentType.RESEARCH_PAPER,
            "scholar.google": ContentType.ACADEMIC_PROFILE,
            "crunchbase.com": ContentType.STARTUP_PROFILE,
            "techpoint.africa": ContentType.NEWS_ARTICLE,
            "techcabal.com": ContentType.NEWS_ARTICLE
        }
    
    async def __aenter__(self):
        """Initialize async components"""
        self.intelligence_module = PerplexityAfricanAIModule(self.perplexity_api_key)
        self.extraction_orchestrator = IntelligentCrawl4AIOrchestrator(self.openai_api_key)
        
        await self.intelligence_module.__aenter__()
        await self.extraction_orchestrator.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async components"""
        if self.intelligence_module:
            await self.intelligence_module.__aexit__(exc_type, exc_val, exc_tb)
        if self.extraction_orchestrator:
            await self.extraction_orchestrator.__aexit__(exc_type, exc_val, exc_tb)
    
    async def run_collection_cycle(self) -> CollectionCycleResult:
        """Execute a complete data collection cycle"""
        
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting collection cycle {cycle_id}")
        
        try:
            # Phase 1: Intelligence Synthesis
            intelligence_targets = await self._run_intelligence_synthesis()
            self.active_targets.extend(intelligence_targets)
            
            # Phase 2: Prioritize and Process
            priority_targets = self._prioritize_targets(self.active_targets[:10])  # Limit for demo
            
            # Phase 3: Deep Extraction
            extraction_results = await self._process_extraction_queue(priority_targets)
            
            # Phase 4: Validate and Store
            validated_innovations = await self._validate_innovations(extraction_results)
            
            end_time = datetime.now()
            
            cycle_result = CollectionCycleResult(
                cycle_id=cycle_id,
                start_time=start_time,
                end_time=end_time,
                targets_discovered=len(intelligence_targets),
                targets_processed=len(extraction_results),
                innovations_extracted=len([r for r in extraction_results if r.success]),
                database_records_created=len(validated_innovations),
                errors_encountered=[],
                recommendations=self._generate_recommendations(extraction_results)
            )
            
            self.collection_history.append(cycle_result)
            
            logger.info(f"Collection cycle {cycle_id} completed successfully")
            return cycle_result
            
        except Exception as e:
            logger.error(f"Collection cycle {cycle_id} failed: {e}")
            return CollectionCycleResult(
                cycle_id=cycle_id,
                start_time=start_time,
                end_time=datetime.now(),
                targets_discovered=0,
                targets_processed=0,
                innovations_extracted=0,
                database_records_created=0,
                errors_encountered=[str(e)],
                recommendations=[]
            )
    
    async def _run_intelligence_synthesis(self) -> List[CollectionTarget]:
        """Run Perplexity intelligence synthesis"""
        
        logger.info("Running intelligence synthesis")
        
        # Generate intelligence reports
        reports = await self.intelligence_module.synthesize_intelligence(
            intelligence_types=[IntelligenceType.INNOVATION_DISCOVERY],
            time_period='last_7_days'
        )
        
        targets = []
        for report in reports:
            for innovation in report.innovations_mentioned:
                if 'company_name' in innovation:
                    target = await self._create_target_from_innovation(innovation)
                    if target:
                        targets.append(target)
        
        logger.info(f"Intelligence synthesis discovered {len(targets)} targets")
        return targets
    
    async def _create_target_from_innovation(self, innovation: Dict[str, Any]) -> Optional[CollectionTarget]:
        """Create collection target from intelligence mention"""
        
        company_name = innovation.get('company_name', '')
        if not company_name:
            return None
        
        # Simple URL discovery strategy
        url = await self._discover_innovation_url(company_name)
        if not url:
            return None
        
        content_type = self._determine_content_type(url)
        priority = PriorityLevel.MEDIUM
        
        return CollectionTarget(
            id=f"intel_{company_name}_{datetime.now().timestamp()}",
            url=url,
            content_type=content_type,
            priority=priority,
            source_collector=CollectorType.INTELLIGENCE_SYNTHESIS,
            metadata={
                'company_name': company_name,
                'original_mention': innovation
            },
            discovered_at=datetime.now()
        )
    
    async def _discover_innovation_url(self, company_name: str) -> Optional[str]:
        """Discover URL for innovation using search"""
        
        try:
            # Use Perplexity to find official website
            search_query = f"{company_name} official website African AI startup"
            response = await self.intelligence_module._query_perplexity(search_query)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract URLs from response
            import re
            urls = re.findall(r'https?://[^\s]+', content)
            
            # Return first valid URL (simplified)
            for url in urls:
                if not any(excluded in url for excluded in ['google.com', 'facebook.com', 'twitter.com']):
                    return url.rstrip('.,)')  # Clean up punctuation
            
        except Exception as e:
            logger.warning(f"Could not search for {company_name} website: {e}")
        
        return None
    
    def _determine_content_type(self, url: str) -> ContentType:
        """Determine content type based on URL"""
        
        for pattern, content_type in self.content_type_mapping.items():
            if pattern in url:
                return content_type
        
        return ContentType.INNOVATION_PROFILE
    
    def _prioritize_targets(self, targets: List[CollectionTarget]) -> List[CollectionTarget]:
        """Prioritize targets for processing"""
        
        priority_order = {
            PriorityLevel.URGENT: 0,
            PriorityLevel.HIGH: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
            PriorityLevel.BATCH: 4
        }
        
        return sorted(targets, key=lambda t: priority_order[t.priority])
    
    async def _process_extraction_queue(self, targets: List[CollectionTarget]) -> List[InnovationExtractionResult]:
        """Process extraction queue with concurrency control"""
        
        logger.info(f"Processing {len(targets)} targets")
        
        extraction_results = []
        
        for target in targets:
            try:
                logger.info(f"Extracting: {target.url}")
                
                result = await self.extraction_orchestrator.extract_innovation_data(
                    url=target.url,
                    content_type=target.content_type,
                    follow_links=False,  # Simplified for demo
                    max_depth=1
                )
                
                target.extraction_result = result
                target.processed_at = datetime.now()
                extraction_results.append(result)
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to extract {target.url}: {e}")
                
                # Create failed result
                failed_result = InnovationExtractionResult(
                    url=target.url,
                    content_type=target.content_type,
                    extraction_timestamp=datetime.now(),
                    success=False,
                    validation_flags=[f"Extraction failed: {str(e)}"]
                )
                extraction_results.append(failed_result)
        
        return extraction_results
    
    async def _validate_innovations(self, results: List[InnovationExtractionResult]) -> List[Dict[str, Any]]:
        """Validate extraction results"""
        
        validated = []
        
        for result in results:
            if (result.success and 
                result.data_completeness_score >= 0.3 and 
                result.confidence_score >= 0.5):
                
                innovation_record = {
                    'title': result.title,
                    'description': result.description,
                    'innovation_type': result.innovation_type,
                    'location': result.location,
                    'source_url': result.url,
                    'completeness_score': result.data_completeness_score,
                    'confidence_score': result.confidence_score,
                    'extracted_at': result.extraction_timestamp
                }
                
                validated.append(innovation_record)
                logger.info(f"Validated innovation: {result.title}")
        
        logger.info(f"Validated {len(validated)} innovations")
        return validated
    
    def _generate_recommendations(self, results: List[InnovationExtractionResult]) -> List[str]:
        """Generate recommendations for next cycle"""
        
        recommendations = []
        
        success_rate = len([r for r in results if r.success]) / len(results) if results else 0
        
        if success_rate < 0.7:
            recommendations.append("Improve URL discovery and validation")
        
        avg_completeness = sum(r.data_completeness_score for r in results if r.success) / len([r for r in results if r.success]) if any(r.success for r in results) else 0
        
        if avg_completeness < 0.5:
            recommendations.append("Enhance extraction schemas for better data capture")
        
        return recommendations
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        
        if not self.collection_history:
            return {"message": "No collection cycles completed yet"}
        
        latest = self.collection_history[-1]
        
        return {
            "latest_cycle_id": latest.cycle_id,
            "total_cycles": len(self.collection_history),
            "last_performance": {
                "targets_discovered": latest.targets_discovered,
                "targets_processed": latest.targets_processed,
                "innovations_extracted": latest.innovations_extracted,
                "success_rate": latest.innovations_extracted / latest.targets_processed if latest.targets_processed > 0 else 0
            },
            "active_targets": len(self.active_targets),
            "recommendations": latest.recommendations
        }


# Example usage
async def main():
    """Example usage of Data Collection Orchestrator"""
    
    # Replace with actual API keys
    perplexity_key = "your_perplexity_api_key"
    openai_key = "your_openai_api_key"
    
    async with DataCollectionOrchestrator(perplexity_key, openai_key) as orchestrator:
        
        # Run collection cycle
        result = await orchestrator.run_collection_cycle()
        
        logger.info(f"Cycle completed: {result.cycle_id}")
        logger.info(f"Discovered: {result.targets_discovered}")
        logger.info(f"Processed: {result.targets_processed}")
        logger.info(f"Extracted: {result.innovations_extracted}")
        
        # Get stats
        stats = orchestrator.get_stats()
        logger.info(f"Stats: {json.dumps(stats, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())
