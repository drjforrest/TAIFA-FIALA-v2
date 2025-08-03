"""
Enhanced ETL Integration Module
Integrates the enhanced_funding_extractor.py into existing ETL workflows

This module provides:
- Integration with RSS parsing workflows
- Integration with Crawl4AI scraping workflows  
- Integration with Serper search workflows
- Enhanced data extraction using the new funding patterns
- Backward compatibility with existing systems
- Comprehensive field mapping to the enhanced schema

Strategy:
1. Wrap existing ETL components with enhanced extraction
2. Apply enhanced extraction to all data sources (RSS, Crawl4AI, Serper)
3. Map extracted data to the enhanced database schema
4. Maintain backward compatibility
5. Add comprehensive logging and monitoring
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import time
from dataclasses import dataclass
from enum import Enum

# Import the enhanced funding extractor
from .enhanced_funding_extractor import EnhancedFundingExtractor, EnhancedETLPipeline

# Import existing ETL components
from ..data_ingestion.master_pipeline import MasterDataIngestionPipeline
from ..data_ingestion.crawl4ai_integration import EnhancedCrawl4AIProcessor, CrawlTarget
from ..ETL_pipelines.serper_search import SerperSearch
from ...core.database import get_database_connection

# Import database utilities
from ..data_ingestion.supabase_utils import supabase_utils

logger = logging.getLogger(__name__)


class ETLDataSource(Enum):
    """ETL data source types"""
    RSS_FEED = "rss_feed"
    CRAWL4AI_SCRAPING = "crawl4ai_scraping"
    SERPER_SEARCH = "serper_search"
    WEB_SCRAPING = "web_scraping"
    NEWS_API = "news_api"


@dataclass
class EnhancedETLConfig:
    """Configuration for enhanced ETL integration"""
    # Enhanced extraction settings
    enable_enhanced_extraction: bool = True
    enable_field_validation: bool = True
    enable_data_enrichment: bool = True
    
    # Processing settings
    batch_size: int = 50
    max_workers: int = 10
    retry_attempts: int = 3
    
    # Quality control
    min_relevance_score: float = 0.6
    enable_duplicate_detection: bool = True
    enable_content_validation: bool = True
    
    # Database settings
    enable_enhanced_schema: bool = True
    enable_backward_compatibility: bool = True


class EnhancedETLIntegrator:
    """
    Enhanced ETL Integrator that wraps existing ETL workflows
    with the new enhanced funding extraction capabilities
    """
    
    def __init__(self, config: EnhancedETLConfig):
        self.config = config
        
        # Initialize enhanced components
        self.enhanced_extractor = EnhancedFundingExtractor()
        self.enhanced_pipeline = EnhancedETLPipeline()
        
        # Initialize existing components (will be set by master pipeline)
        self.master_pipeline: Optional[MasterDataIngestionPipeline] = None
        self.crawl4ai_processor: Optional[EnhancedCrawl4AIProcessor] = None
        self.serper_search: Optional[SerperSearch] = None
        
        # Processing statistics
        self.stats = {
            'total_items_processed': 0,
            'enhanced_extractions': 0,
            'field_enrichments': 0,
            'validation_failures': 0,
            'database_saves': 0,
            'processing_errors': 0,
            'by_source': {
                'rss_feed': 0,
                'crawl4ai_scraping': 0,
                'serper_search': 0,
                'web_scraping': 0,
                'news_api': 0
            }
        }
        
        logger.info("Enhanced ETL Integrator initialized")
    
    def set_master_pipeline(self, master_pipeline: MasterDataIngestionPipeline):
        """Set reference to master pipeline"""
        self.master_pipeline = master_pipeline
        self.crawl4ai_processor = master_pipeline.crawl4ai_processor
        self.serper_search = master_pipeline.serper_search
        logger.info("Master pipeline reference set")
    
    async def process_rss_data_enhanced(self, rss_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process RSS data with enhanced extraction
        Integrates with existing RSS monitoring workflows
        """
        logger.info(f"Processing {len(rss_items)} RSS items with enhanced extraction")
        
        enhanced_opportunities = []
        
        for item in rss_items:
            try:
                # Apply enhanced extraction
                enhanced_data = self.enhanced_pipeline.process_rss_item(item)
                
                # Validate and enrich
                if self.config.enable_field_validation:
                    enhanced_data = await self._validate_and_enrich_data(
                        enhanced_data, 
                        ETLDataSource.RSS_FEED
                    )
                
                # Apply quality filters
                if self._passes_quality_filters(enhanced_data):
                    enhanced_opportunities.append(enhanced_data)
                    self.stats['enhanced_extractions'] += 1
                else:
                    self.stats['validation_failures'] += 1
                
                self.stats['total_items_processed'] += 1
                self.stats['by_source']['rss_feed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing RSS item: {e}")
                self.stats['processing_errors'] += 1
                continue
        
        # Save to database with enhanced schema
        if enhanced_opportunities and self.config.enable_enhanced_schema:
            await self._save_enhanced_opportunities(enhanced_opportunities, ETLDataSource.RSS_FEED)
        
        logger.info(f"Enhanced RSS processing completed: {len(enhanced_opportunities)} opportunities extracted")
        return enhanced_opportunities
    
    async def process_crawl4ai_data_enhanced(self, crawl_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process Crawl4AI scraped data with enhanced extraction
        Integrates with existing Crawl4AI workflows
        """
        logger.info(f"Processing {len(crawl_results)} Crawl4AI results with enhanced extraction")
        
        enhanced_opportunities = []
        
        for result in crawl_results:
            try:
                # Convert Crawl4AI result to web scraped format
                scraped_data = {
                    'title': result.get('title', ''),
                    'content': result.get('description', '') or result.get('extracted_content', ''),
                    'url': result.get('source_url', ''),
                    'meta_description': result.get('description', ''),
                    'crawl_metadata': result.get('crawl_metadata', {}),
                    'relevance_score': result.get('relevance_score', 0.0)
                }
                
                # Apply enhanced extraction
                enhanced_data = self.enhanced_pipeline.process_web_scraped_content(scraped_data)
                
                # Add Crawl4AI specific metadata
                enhanced_data.update({
                    'extraction_strategy': result.get('extraction_strategy', 'unknown'),
                    'crawl_target_type': result.get('crawl_metadata', {}).get('target_type', 'unknown'),
                    'crawl_priority': result.get('crawl_metadata', {}).get('source_priority', 1),
                    'original_relevance_score': result.get('relevance_score', 0.0)
                })
                
                # Validate and enrich
                if self.config.enable_field_validation:
                    enhanced_data = await self._validate_and_enrich_data(
                        enhanced_data, 
                        ETLDataSource.CRAWL4AI_SCRAPING
                    )
                
                # Apply quality filters
                if self._passes_quality_filters(enhanced_data):
                    enhanced_opportunities.append(enhanced_data)
                    self.stats['enhanced_extractions'] += 1
                else:
                    self.stats['validation_failures'] += 1
                
                self.stats['total_items_processed'] += 1
                self.stats['by_source']['crawl4ai_scraping'] += 1
                
            except Exception as e:
                logger.error(f"Error processing Crawl4AI result: {e}")
                self.stats['processing_errors'] += 1
                continue
        
        # Save to database with enhanced schema
        if enhanced_opportunities and self.config.enable_enhanced_schema:
            await self._save_enhanced_opportunities(enhanced_opportunities, ETLDataSource.CRAWL4AI_SCRAPING)
        
        logger.info(f"Enhanced Crawl4AI processing completed: {len(enhanced_opportunities)} opportunities extracted")
        return enhanced_opportunities
    
    async def process_serper_data_enhanced(self, search_results: List[Dict[str, Any]], search_query: str) -> List[Dict[str, Any]]:
        """
        Process Serper search results with enhanced extraction
        Integrates with existing Serper search workflows
        """
        logger.info(f"Processing {len(search_results)} Serper results with enhanced extraction")
        
        enhanced_opportunities = []
        
        for result in search_results:
            try:
                # Convert Serper result to web scraped format
                scraped_data = {
                    'title': result.get('title', ''),
                    'content': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'meta_description': result.get('snippet', ''),
                    'search_query': search_query,
                    'search_position': result.get('position', 0)
                }
                
                # Apply enhanced extraction
                enhanced_data = self.enhanced_pipeline.process_web_scraped_content(scraped_data)
                
                # Add Serper specific metadata
                enhanced_data.update({
                    'search_query': search_query,
                    'search_position': result.get('position', 0),
                    'search_engine': 'google',
                    'search_timestamp': datetime.utcnow().isoformat()
                })
                
                # Validate and enrich
                if self.config.enable_field_validation:
                    enhanced_data = await self._validate_and_enrich_data(
                        enhanced_data, 
                        ETLDataSource.SERPER_SEARCH
                    )
                
                # Apply quality filters
                if self._passes_quality_filters(enhanced_data):
                    enhanced_opportunities.append(enhanced_data)
                    self.stats['enhanced_extractions'] += 1
                else:
                    self.stats['validation_failures'] += 1
                
                self.stats['total_items_processed'] += 1
                self.stats['by_source']['serper_search'] += 1
                
            except Exception as e:
                logger.error(f"Error processing Serper result: {e}")
                self.stats['processing_errors'] += 1
                continue
        
        # Save to database with enhanced schema
        if enhanced_opportunities and self.config.enable_enhanced_schema:
            await self._save_enhanced_opportunities(enhanced_opportunities, ETLDataSource.SERPER_SEARCH)
        
        logger.info(f"Enhanced Serper processing completed: {len(enhanced_opportunities)} opportunities extracted")
        return enhanced_opportunities
    
    async def _validate_and_enrich_data(self, data: Dict[str, Any], source: ETLDataSource) -> Dict[str, Any]:
        """
        Validate and enrich extracted data
        """
        try:
            # Field validation
            validated_data = await self._validate_required_fields(data)
            
            # Data enrichment
            if self.config.enable_data_enrichment:
                enriched_data = await self._enrich_data_fields(validated_data, source)
            else:
                enriched_data = validated_data
            
            # Add processing metadata
            enriched_data.update({
                'processing_timestamp': datetime.utcnow().isoformat(),
                'enhanced_extraction_version': '1.0',
                'validation_passed': True,
                'enrichment_applied': self.config.enable_data_enrichment
            })
            
            self.stats['field_enrichments'] += 1
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error in validation/enrichment: {e}")
            # Return original data with error flag
            data['validation_passed'] = False
            data['validation_error'] = str(e)
            return data
    
    async def _validate_required_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required fields and data quality"""
        
        # Required fields validation
        required_fields = ['title', 'description', 'source_url']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Data quality validation
        if len(data.get('title', '')) < 10:
            raise ValueError("Title too short")
        
        if len(data.get('description', '')) < 50:
            raise ValueError("Description too short")
        
        # URL validation
        source_url = data.get('source_url', '')
        if not source_url.startswith(('http://', 'https://')):
            raise ValueError("Invalid source URL")
        
        # Funding type validation
        funding_type = data.get('funding_type')
        if funding_type and funding_type not in ['total_pool', 'per_project_exact', 'per_project_range']:
            data['funding_type'] = 'per_project_range'  # Default fallback
        
        # Currency validation
        currency = data.get('currency')
        if currency and len(currency) != 3:
            data['currency'] = 'USD'  # Default fallback
        
        return data
    
    async def _enrich_data_fields(self, data: Dict[str, Any], source: ETLDataSource) -> Dict[str, Any]:
        """Enrich data with additional computed fields"""
        
        # Calculate urgency level based on deadline
        deadline = data.get('deadline')
        if deadline:
            try:
                if isinstance(deadline, str):
                    from dateutil.parser import parse
                    deadline_date = parse(deadline).date()
                else:
                    deadline_date = deadline
                
                days_until_deadline = (deadline_date - datetime.now().date()).days
                
                if days_until_deadline <= 7:
                    data['urgency_level'] = 'high'
                elif days_until_deadline <= 30:
                    data['urgency_level'] = 'medium'
                else:
                    data['urgency_level'] = 'low'
                    
                data['days_until_deadline'] = days_until_deadline
                
            except Exception as e:
                logger.warning(f"Error calculating urgency: {e}")
                data['urgency_level'] = 'unknown'
        
        # Calculate suitability score based on multiple factors
        suitability_score = 0.0
        
        # Geographic relevance (Africa focus)
        text_content = f"{data.get('title', '')} {data.get('description', '')}".lower()
        africa_terms = ['africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana', 'uganda', 'rwanda']
        if any(term in text_content for term in africa_terms):
            suitability_score += 0.3
        
        # AI/Tech relevance
        ai_terms = ['ai', 'artificial intelligence', 'machine learning', 'technology', 'digital', 'innovation']
        if any(term in text_content for term in ai_terms):
            suitability_score += 0.3
        
        # Funding clarity
        if data.get('funding_type') and data.get('funding_type') != 'per_project_range':
            suitability_score += 0.2
        
        # Application process clarity
        if data.get('application_url') or data.get('contact_email'):
            suitability_score += 0.1
        
        # Deadline clarity
        if data.get('deadline'):
            suitability_score += 0.1
        
        data['suitability_score'] = min(suitability_score, 1.0)
        
        # Add source-specific enrichments
        if source == ETLDataSource.RSS_FEED:
            data['data_freshness'] = 'high'  # RSS feeds are typically fresh
        elif source == ETLDataSource.CRAWL4AI_SCRAPING:
            data['data_depth'] = 'high'  # Crawl4AI provides deep content extraction
        elif source == ETLDataSource.SERPER_SEARCH:
            data['discovery_method'] = 'search'  # Found through search
        
        return data
    
    def _passes_quality_filters(self, data: Dict[str, Any]) -> bool:
        """Apply quality filters to determine if data should be saved"""
        
        # Minimum relevance score filter
        relevance_score = data.get('relevance_score', 0.0)
        suitability_score = data.get('suitability_score', 0.0)
        
        # Use the higher of the two scores
        combined_score = max(relevance_score, suitability_score)
        
        if combined_score < self.config.min_relevance_score:
            return False
        
        # Validation passed filter
        if not data.get('validation_passed', True):
            return False
        
        # Duplicate detection (basic)
        if self.config.enable_duplicate_detection:
            # This would integrate with more sophisticated duplicate detection
            # For now, just check if we have a source URL
            if not data.get('source_url'):
                return False
        
        return True
    
    async def _save_enhanced_opportunities(self, opportunities: List[Dict[str, Any]], source: ETLDataSource):
        """Save opportunities to database using enhanced schema"""
        
        try:
            # Prepare data for enhanced schema
            enhanced_records = []
            
            for opp in opportunities:
                # Map to enhanced schema fields
                enhanced_record = {
                    # Core fields
                    'title': opp.get('title'),
                    'description': opp.get('description'),
                    'source_url': opp.get('source_url'),
                    'application_url': opp.get('application_url'),
                    
                    # Enhanced funding fields
                    'funding_type': opp.get('funding_type', 'per_project_range'),
                    'total_funding_pool': opp.get('total_funding_pool'),
                    'min_amount_per_project': opp.get('min_amount_per_project'),
                    'max_amount_per_project': opp.get('max_amount_per_project'),
                    'exact_amount_per_project': opp.get('exact_amount_per_project'),
                    'estimated_project_count': opp.get('estimated_project_count'),
                    'project_count_range': opp.get('project_count_range'),
                    'currency': opp.get('currency', 'USD'),
                    
                    # Enhanced process fields
                    'deadline': opp.get('deadline'),
                    'application_deadline_type': opp.get('application_deadline_type', 'fixed'),
                    'application_process': opp.get('application_process'),
                    'selection_criteria': opp.get('selection_criteria'),
                    'reporting_requirements': opp.get('reporting_requirements'),
                    
                    # Enhanced targeting fields
                    'target_audience': opp.get('target_audience'),
                    'ai_subsectors': opp.get('ai_subsectors'),
                    'development_stage': opp.get('development_stage'),
                    'project_duration': opp.get('project_duration'),
                    
                    # Focus indicators
                    'collaboration_required': opp.get('collaboration_required'),
                    'gender_focused': opp.get('gender_focused'),
                    'youth_focused': opp.get('youth_focused'),
                    
                    # Computed fields
                    'urgency_level': opp.get('urgency_level'),
                    'suitability_score': opp.get('suitability_score'),
                    'relevance_score': opp.get('relevance_score'),
                    'days_until_deadline': opp.get('days_until_deadline'),
                    
                    # Metadata
                    'status': 'active',
                    'source_type': source.value,
                    'enhanced_extraction_applied': True,
                    'processing_timestamp': opp.get('processing_timestamp'),
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                }
                
                # Remove None values
                enhanced_record = {k: v for k, v in enhanced_record.items() if v is not None}
                enhanced_records.append(enhanced_record)
            
            # Save to database using Supabase utils
            if enhanced_records:
                result = await supabase_utils.bulk_insert_opportunities(enhanced_records)
                
                if result.get('success'):
                    self.stats['database_saves'] += result.get('inserted', 0)
                    logger.info(f"Saved {result.get('inserted', 0)} enhanced opportunities to database")
                else:
                    logger.error(f"Database save failed: {result.get('error')}")
                    self.stats['processing_errors'] += 1
            
        except Exception as e:
            logger.error(f"Error saving enhanced opportunities: {e}")
            self.stats['processing_errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['enhanced_extractions'] / max(self.stats['total_items_processed'], 1) * 100
            ),
            'validation_success_rate': (
                (self.stats['total_items_processed'] - self.stats['validation_failures']) / 
                max(self.stats['total_items_processed'], 1) * 100
            ),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def process_batch_with_enhanced_extraction(self, 
                                                   items: List[Dict[str, Any]], 
                                                   source: ETLDataSource) -> List[Dict[str, Any]]:
        """
        Generic batch processing method that can handle any data source
        """
        logger.info(f"Processing batch of {len(items)} items from {source.value}")
        
        if source == ETLDataSource.RSS_FEED:
            return await self.process_rss_data_enhanced(items)
        elif source == ETLDataSource.CRAWL4AI_SCRAPING:
            return await self.process_crawl4ai_data_enhanced(items)
        elif source == ETLDataSource.SERPER_SEARCH:
            # For Serper, we need a search query - extract from first item or use default
            search_query = items[0].get('search_query', 'AI funding Africa') if items else 'AI funding Africa'
            return await self.process_serper_data_enhanced(items, search_query)
        else:
            logger.warning(f"Unsupported source type: {source}")
            return []


# Integration wrapper for existing master pipeline
class EnhancedMasterPipelineWrapper:
    """
    Wrapper that integrates enhanced ETL processing into the existing master pipeline
    """
    
    def __init__(self, master_pipeline: MasterDataIngestionPipeline, config: EnhancedETLConfig = None):
        self.master_pipeline = master_pipeline
        self.config = config or EnhancedETLConfig()
        
        # Initialize enhanced integrator
        self.enhanced_integrator = EnhancedETLIntegrator(self.config)
        self.enhanced_integrator.set_master_pipeline(master_pipeline)
        
        logger.info("Enhanced Master Pipeline Wrapper initialized")
    
    async def enhanced_rss_collection(self):
        """Enhanced RSS collection that applies enhanced extraction"""
        try:
            # Run original RSS pipeline
            logger.info("Running enhanced RSS collection...")
            stats = await self.master_pipeline.rss_pipeline.process_funding_intelligence(
                search_mode="comprehensive",
                processing_mode="batch"
            )
            
            # Get recent RSS items for enhanced processing
            recent_items = await supabase_utils.get_recent_rss_items(hours=24, limit=100)
            
            if recent_items:
                # Apply enhanced extraction
                enhanced_opportunities = await self.enhanced_integrator.process_rss_data_enhanced(recent_items)
                
                logger.info(f"Enhanced RSS collection completed: {len(enhanced_opportunities)} opportunities processed")
                return {
                    'original_stats': stats,
                    'enhanced_opportunities': len(enhanced_opportunities),
                    'enhanced_stats': self.enhanced_integrator.get_stats()
                }
            else:
                logger.info("No recent RSS items found for enhanced processing")
                return {'original_stats': stats, 'enhanced_opportunities': 0}
                
        except Exception as e:
            logger.error(f"Enhanced RSS collection failed: {e}")
            return {'error': str(e)}
    
    async def enhanced_crawl4ai_processing(self, targets: List[CrawlTarget] = None):
        """Enhanced Crawl4AI processing that applies enhanced extraction"""
        try:
            # Use provided targets or default targets
            if not targets:
                targets = self.master_pipeline.crawl4ai_processor.crawl_targets[:10]  # Process first 10
            
            logger.info(f"Running enhanced Crawl4AI processing for {len(targets)} targets...")
            
            # Run original Crawl4AI processing
            crawl_results = await self.master_pipeline.crawl4ai_processor.process_high_volume_batch(targets)
            
            if crawl_results:
                # Apply enhanced extraction
                enhanced_opportunities = await self.enhanced_integrator.process_crawl4ai_data_enhanced(crawl_results)
                
                logger.info(f"Enhanced Crawl4AI processing completed: {len(enhanced_opportunities)} opportunities processed")
                return {
                    'crawl_results': len(crawl_results),
                    'enhanced_opportunities': len(enhanced_opportunities),
                    'enhanced_stats': self.enhanced_integrator.get_stats()
                }
            else:
                logger.info("No Crawl4AI results found for enhanced processing")
                return {'crawl_results': 0, 'enhanced_opportunities': 0}
                
        except Exception as e:
            logger.error(f"Enhanced Crawl4AI processing failed: {e}")
            return {'error': str(e)}
    
    async def enhanced_serper_search(self, search_queries: List[str] = None):
        """Enhanced Serper search that applies enhanced extraction"""
        try:
            # Use provided queries or default queries
            if not search_queries:
                search_queries = [
                    "AI funding opportunities Africa 2024",
                    "artificial intelligence grants Africa",
                    "technology funding African startups",
                    "machine learning research grants Africa"
                ]
            
            logger.info(f"Running enhanced Serper search for {len(search_queries)} queries...")
            
            all_enhanced_opportunities = []
            
            for query in search_queries:
                # Run original Serper search
                search_results = await self.master_pipeline.serper_search.search(query, num_results=10)
                
                if search_results:
                    # Apply enhanced extraction
                    enhanced_opportunities = await self.enhanced_integrator.process_serper_data_enhanced(
                        search_results, query
                    )
                    all_enhanced_opportunities.extend(enhanced_opportunities)
            
            logger.info(f"Enhanced Serper search completed: {len(all_enhanced_opportunities)} opportunities processed")
            return {
                'search_queries': len(search_queries),
                'enhanced_opportunities': len(all_enhanced_opportunities),
                'enhanced_stats': self.enhanced_integrator.get_stats()
            }
                
        except Exception as e:
            logger.error(f"Enhanced Serper search failed: {e}")
            return {'error': str(e)}
    
    async def run_full_enhanced_pipeline(self):
        """Run the full enhanced ETL pipeline"""
        logger.info("Starting full enhanced ETL pipeline...")
        
        results = {
            'start_time': datetime.utcnow().isoformat(),
            'rss_results': {},
            'crawl4ai_results': {},
            'serper_results': {},
            'total_opportunities': 0,
            'errors': []
        }
        
        try:
            # Enhanced RSS collection
            logger.info("Phase 1: Enhanced RSS collection")
            rss_results = await self.enhanced_rss_collection()
            results['rss_results'] = rss_results
            
            if 'error' not in rss_results:
                results['total_opportunities'] += rss_results.get('enhanced_opportunities', 0)
            else:
                results['errors'].append(f"RSS: {rss_results['error']}")
            
            # Enhanced Crawl4AI processing
            logger.info("Phase 2: Enhanced Crawl4AI processing")
            crawl4ai_results = await self.enhanced_crawl4ai_processing()
            results['crawl4ai_results'] = crawl4ai_results
            
            if 'error' not in crawl4ai_results:
                results['total_opportunities'] += crawl4ai_results.get('enhanced_opportunities', 0)
            else:
                results['errors'].append(f"Crawl4AI: {crawl4ai_results['error']}")
            
            # Enhanced Serper search
            logger.info("Phase 3: Enhanced Serper search")
            serper_results = await self.enhanced_serper_search()
            results['serper_results'] = serper_results
            
            if 'error' not in serper_results:
                results['total_opportunities'] += serper_results.get('enhanced_opportunities', 0)
            else:
                results['errors'].append(f"Serper: {serper_results['error']}")
            
            results['end_time'] = datetime.utcnow().isoformat()
            results['success'] = len(results['errors']) == 0
            
            logger.info(f"Full enhanced ETL pipeline completed: {results['total_opportunities']} total opportunities processed")
            
            return results
            
        except Exception as e:
            logger.error(f"Full enhanced ETL pipeline failed: {e}")
            results['errors'].append(f"Pipeline: {str(e)}")
            results['success'] = False
            return results


# Example usage and testing
async def test_enhanced_etl_integration():
    """Test the enhanced ETL integration"""
    
    # Create configuration
    config = EnhancedETLConfig(
        enable_enhanced_extraction=True,
        enable_field_validation=True,
        enable_data_enrichment=True,
        min_relevance_score=0.6
    )
    
    # Create integrator
    integrator = EnhancedETLIntegrator(config)
    
    # Test RSS data processing
    test_rss_items = [
        {
            'title': 'Gates Foundation Announces $5M AI for Africa Initiative',
            'description': 'The Gates Foundation is launching a new $5 million initiative to support AI startups across Africa, with grants ranging from $50,000 to $200,000 per project.',
            'link': 'https://gatesfoundation.org/ai-africa-initiative',
            'published': '2024-01-15T10:00:00Z'
        },
        {
            'title': 'African Development Bank Launches Tech Innovation Fund',
            'description': 'The AfDB announces a $10 million fund to support technology innovation across Africa, with particular focus on AI and fintech solutions.',
            'link': 'https://afdb.org/tech-innovation-fund',
            'published': '2024-01-10T14:30:00Z'
        }
    ]
    
    # Test enhanced RSS processing
    enhanced_rss_results = await integrator.process_rss_data_enhanced(test_rss_items)
    print(f"Enhanced RSS processing: {len(enhanced_rss_results)} opportunities extracted")
    
    # Test Crawl4AI data processing
    test_crawl4ai_results = [
        {
            'title': 'Mozilla Foundation AI Grant Program',
            'description': 'Mozilla Foundation offers grants up to $75,000 for AI projects that promote digital inclusion and privacy.',
            'source_url': 'https://mozilla.org/ai-grants',
            'extraction_strategy': 'intelligence_item',
            'relevance_score': 0.85,
            'crawl_metadata': {
                'target_type': 'foundation_website',
                'source_priority': 1
            }
        }
    ]
    
    # Test enhanced Crawl4AI processing
    enhanced_crawl4ai_results = await integrator.process_crawl4ai_data_enhanced(test_crawl4ai_results)
    print(f"Enhanced Crawl4AI processing: {len(enhanced_crawl4ai_results)} opportunities extracted")
    
    # Test Serper search data processing
    test_serper_results = [
        {
            'title': 'Google AI for Social Good Grants',
            'snippet': 'Google announces AI for Social Good grants supporting projects in Africa, with funding up to $100,000 per project.',
            'link': 'https://ai.google/social-good/grants',
            'position': 1
        }
    ]
    
    # Test enhanced Serper processing
    enhanced_serper_results = await integrator.process_serper_data_enhanced(
        test_serper_results, 
        'AI funding opportunities Africa'
    )
    print(f"Enhanced Serper processing: {len(enhanced_serper_results)} opportunities extracted")
    
    # Print statistics
    stats = integrator.get_stats()
    print(f"Processing statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_etl_integration())
