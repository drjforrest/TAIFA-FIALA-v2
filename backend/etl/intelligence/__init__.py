"""
TAIFA-FIALA Intelligence ETL Package
===================================

Enhanced data collection pipeline for African AI innovation discovery.
"""

from .perplexity_african_ai import PerplexityAfricanAIModule, IntelligenceType, IntelligenceReport
from .enhanced_crawl4ai import IntelligentCrawl4AIOrchestrator, ContentType, InnovationExtractionResult
from .data_collection_orchestrator import DataCollectionOrchestrator, CollectorType, PriorityLevel

__all__ = [
    'PerplexityAfricanAIModule',
    'IntelligenceType', 
    'IntelligenceReport',
    'IntelligentCrawl4AIOrchestrator',
    'ContentType',
    'InnovationExtractionResult',
    'DataCollectionOrchestrator',
    'CollectorType',
    'PriorityLevel'
]

__version__ = "1.0.0"
