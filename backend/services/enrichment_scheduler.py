"""
AI Enrichment Scheduler Service
Manages timer-based enrichment execution with configurable intervals
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger

from etl.intelligence.perplexity_african_ai import PerplexityAfricanAIModule, IntelligenceType


@dataclass
class EnrichmentSchedule:
    """Configuration for scheduled enrichment"""
    provider: str = "perplexity"
    intelligence_types: List[str] = None
    time_period: str = "last_7_days"
    geographic_focus: List[str] = None
    interval_hours: int = 6  # Run every 6 hours by default
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

    def __post_init__(self):
        if self.intelligence_types is None:
            self.intelligence_types = ["innovation_discovery", "funding_landscape"]
        if self.geographic_focus is None:
            self.geographic_focus = ["Nigeria", "Kenya", "South Africa", "Ghana", "Egypt"]
        if self.next_run is None:
            self.next_run = datetime.now() + timedelta(hours=self.interval_hours)


class EnrichmentScheduler:
    """Manages timer-based AI enrichment execution"""
    
    def __init__(self):
        self.schedule = EnrichmentSchedule()
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
    def update_schedule(
        self,
        interval_hours: Optional[int] = None,
        enabled: Optional[bool] = None,
        intelligence_types: Optional[List[str]] = None,
        provider: Optional[str] = None,
        geographic_focus: Optional[List[str]] = None
    ):
        """Update the enrichment schedule configuration"""
        if interval_hours is not None:
            self.schedule.interval_hours = interval_hours
            # Recalculate next run time
            if self.schedule.last_run:
                self.schedule.next_run = self.schedule.last_run + timedelta(hours=interval_hours)
            else:
                self.schedule.next_run = datetime.now() + timedelta(hours=interval_hours)
                
        if enabled is not None:
            self.schedule.enabled = enabled
            
        if intelligence_types is not None:
            self.schedule.intelligence_types = intelligence_types
            
        if provider is not None:
            self.schedule.provider = provider
            
        if geographic_focus is not None:
            self.schedule.geographic_focus = geographic_focus
            
        logger.info(f"Updated enrichment schedule: interval={self.schedule.interval_hours}h, "
                   f"enabled={self.schedule.enabled}, provider={self.schedule.provider}")
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """Get current schedule information"""
        return {
            "enabled": self.schedule.enabled,
            "provider": self.schedule.provider,
            "interval_hours": self.schedule.interval_hours,
            "intelligence_types": self.schedule.intelligence_types,
            "geographic_focus": self.schedule.geographic_focus,
            "last_run": self.schedule.last_run.isoformat() if self.schedule.last_run else None,
            "next_run": self.schedule.next_run.isoformat() if self.schedule.next_run else None,
            "running": self.running,
            "time_until_next_run": self._get_time_until_next_run()
        }
    
    def _get_time_until_next_run(self) -> Optional[str]:
        """Get human-readable time until next run"""
        if not self.schedule.next_run or not self.schedule.enabled:
            return None
            
        time_diff = self.schedule.next_run - datetime.now()
        if time_diff.total_seconds() <= 0:
            return "Due now"
            
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    async def start_scheduler(self):
        """Start the enrichment scheduler"""
        if self.running:
            logger.warning("Enrichment scheduler is already running")
            return
            
        self.running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        logger.info("Enrichment scheduler started")
    
    async def stop_scheduler(self):
        """Stop the enrichment scheduler"""
        if not self.running:
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Enrichment scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        try:
            while self.running:
                # Check if it's time to run enrichment
                if (self.schedule.enabled and 
                    self.schedule.next_run and 
                    datetime.now() >= self.schedule.next_run):
                    
                    logger.info("Triggering scheduled enrichment")
                    await self._run_scheduled_enrichment()
                
                # Sleep for 1 minute before checking again
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            logger.info("Enrichment scheduler loop cancelled")
        except Exception as e:
            logger.error(f"Error in enrichment scheduler loop: {e}")
            self.running = False
    
    async def _run_scheduled_enrichment(self):
        """Execute scheduled enrichment"""
        try:
            # Update timestamps
            self.schedule.last_run = datetime.now()
            self.schedule.next_run = self.schedule.last_run + timedelta(hours=self.schedule.interval_hours)
            
            # Route to appropriate provider
            if self.schedule.provider == "perplexity":
                await self._run_perplexity_enrichment()
            else:
                logger.error(f"Unsupported enrichment provider: {self.schedule.provider}")
                
        except Exception as e:
            logger.error(f"Error in scheduled enrichment: {e}")
    
    async def _run_perplexity_enrichment(self):
        """Run Perplexity enrichment"""
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            logger.error("PERPLEXITY_API_KEY not found - skipping scheduled enrichment")
            return
        
        # Convert string intelligence types to enum values
        try:
            intel_types = []
            for intel_type_str in self.schedule.intelligence_types:
                if hasattr(IntelligenceType, intel_type_str.upper()):
                    intel_types.append(IntelligenceType(intel_type_str))
                else:
                    intel_types.append(IntelligenceType.INNOVATION_DISCOVERY)
        except Exception:
            intel_types = [IntelligenceType.INNOVATION_DISCOVERY, IntelligenceType.FUNDING_LANDSCAPE]
        
        logger.info(f"Running scheduled Perplexity enrichment with {len(intel_types)} intelligence types")
        
        async with PerplexityAfricanAIModule(api_key) as perplexity_module:
            reports = await perplexity_module.synthesize_intelligence(
                intelligence_types=intel_types,
                time_period=self.schedule.time_period,
                geographic_focus=self.schedule.geographic_focus
            )
            
            logger.info(f"Scheduled enrichment generated {len(reports)} intelligence reports")
            
            # Store reports (same logic as the API endpoint)
            if reports:
                await self._store_reports(reports)
                
    async def _store_reports(self, reports):
        """Store enrichment reports in vector database and Supabase"""
        try:
            from services.vector_service import get_vector_service, VectorDocument
            from config.database import get_supabase
            
            vector_service = await get_vector_service()
            supabase = get_supabase()
            
            for report in reports:
                # Store in vector database
                content = f"{report.title}\n\n{report.summary}\n\nKey Findings:\n"
                content += "\n".join([f"- {finding}" for finding in report.key_findings])
                
                doc = VectorDocument(
                    id=f"enrichment_scheduled_{report.report_id}",
                    content=content,
                    metadata={
                        "content_type": "enrichment_report",
                        "provider": "perplexity",
                        "source": "scheduled",
                        "report_id": report.report_id,
                        "title": report.title,
                        "report_type": report.report_type.value,
                        "confidence_score": report.confidence_score,
                        "generation_timestamp": report.generation_timestamp.isoformat(),
                        "geographic_focus": report.geographic_focus,
                        "key_findings": report.key_findings,
                        "sources_count": len(report.sources),
                        "innovations_mentioned_count": len(report.innovations_mentioned),
                        "funding_updates_count": len(report.funding_updates)
                    }
                )
                
                await vector_service.upsert_documents([doc])
                
                # Store in Supabase
                try:
                    report_data = {
                        "id": report.report_id,
                        "title": report.title,
                        "provider": "perplexity",
                        "source": "scheduled",
                        "report_type": report.report_type.value,
                        "summary": report.summary,
                        "key_findings": report.key_findings,
                        "innovations_mentioned": report.innovations_mentioned,
                        "funding_updates": report.funding_updates,
                        "policy_developments": report.policy_developments,
                        "confidence_score": report.confidence_score,
                        "sources": report.sources,
                        "geographic_focus": report.geographic_focus,
                        "follow_up_actions": report.follow_up_actions,
                        "generation_timestamp": report.generation_timestamp.isoformat(),
                        "time_period_analyzed": report.time_period_analyzed,
                        "validation_flags": report.validation_flags
                    }
                    
                    supabase.table('intelligence_reports').insert(report_data).execute()
                    
                except Exception as db_error:
                    logger.warning(f"Could not store scheduled report {report.report_id} in database: {db_error}")
                    
        except Exception as e:
            logger.error(f"Error storing scheduled enrichment reports: {e}")


# Global scheduler instance
enrichment_scheduler = EnrichmentScheduler()


async def start_enrichment_scheduler():
    """Start the global enrichment scheduler"""
    await enrichment_scheduler.start_scheduler()


async def stop_enrichment_scheduler():
    """Stop the global enrichment scheduler"""
    await enrichment_scheduler.stop_scheduler()


def get_enrichment_scheduler() -> EnrichmentScheduler:
    """Get the global enrichment scheduler instance"""
    return enrichment_scheduler