"""
Integration Guide for AI Backfilling Services
============================================

This guide shows how to integrate the new AI backfilling services into the existing ETL pipeline.
The services are designed to run on a scheduled basis (e.g., every 3 hours) to cost-efficiently
enrich existing innovation records with missing properties.

Architecture:
1. AI Backfill Service: Main orchestrator using Perplexity + OpenAI
2. Targeted Search Service: Serper.dev for specific missing values
3. Integration with existing deduplication and enrichment services

Cost Management:
- Daily budget limits to prevent unexpected costs
- Conditional triggering to avoid unnecessary searches
- Priority-based processing for maximum value
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from loguru import logger

from services.ai_backfill_service import ai_backfill_service, create_backfill_jobs_for_innovations
from services.targeted_search_service import run_targeted_searches_for_innovations
from database.supabase_client import supabase


class BackfillIntegrationService:
    """Service to integrate AI backfilling into the existing ETL pipeline"""
    
    def __init__(self):
        self.last_backfill_run = None
        self.backfill_interval = timedelta(hours=3)  # Run every 3 hours
        
    async def should_run_backfill(self) -> bool:
        """Check if it's time to run the backfill process"""
        
        if not self.last_backfill_run:
            return True
        
        return datetime.now() - self.last_backfill_run >= self.backfill_interval
    
    async def get_innovations_needing_backfill(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get innovations that need backfilling, prioritized by verification status and recency"""
        
        try:
            # Query for innovations with missing critical fields
            response = supabase.table('innovations').select(
                'id, title, description, verification_status, created_at, '
                'fundings, website_url, github_url, demo_url, source_url, '
                'organizations, individuals, impact_metrics'
            ).order('verification_status', desc=True).order('created_at', desc=False).limit(limit).execute()
            
            if response.data:
                logger.info(f"Found {len(response.data)} innovations for potential backfilling")
                return response.data
            
        except Exception as e:
            logger.error(f"Error fetching innovations for backfill: {e}")
        
        return []
    
    async def run_scheduled_backfill(self) -> Dict[str, Any]:
        """Run the complete scheduled backfill process"""
        
        if not await self.should_run_backfill():
            logger.info("Backfill not due yet, skipping")
            return {'status': 'skipped', 'reason': 'not_due'}
        
        logger.info("🤖 Starting scheduled AI backfill process")
        start_time = datetime.now()
        
        try:
            # Get innovations needing backfill
            innovations = await self.get_innovations_needing_backfill(limit=30)
            
            if not innovations:
                logger.info("No innovations need backfilling")
                return {'status': 'completed', 'innovations_processed': 0}
            
            # Phase 1: Create comprehensive backfill jobs (Perplexity + OpenAI)
            logger.info("Phase 1: Creating comprehensive backfill jobs")
            backfill_jobs = await create_backfill_jobs_for_innovations(innovations)
            
            # Process high-priority jobs first
            high_priority_jobs = [job for job in backfill_jobs if job.priority.value in ['critical', 'high']]
            processed_jobs = await ai_backfill_service.run_scheduled_backfill(max_jobs=min(10, len(high_priority_jobs)))
            
            # Phase 2: Run targeted searches for specific missing values
            logger.info("Phase 2: Running targeted searches for missing values")
            targeted_results = await run_targeted_searches_for_innovations(innovations, max_searches=15)
            
            # Phase 3: Apply results to database
            logger.info("Phase 3: Applying backfill results to database")
            update_results = await self.apply_backfill_results(processed_jobs, targeted_results)
            
            self.last_backfill_run = datetime.now()
            duration = (datetime.now() - start_time).total_seconds()
            
            # Calculate costs
            total_cost = sum(job.total_cost for job in processed_jobs) + sum(result.search_cost for result in targeted_results)
            
            summary = {
                'status': 'completed',
                'duration_seconds': duration,
                'innovations_processed': len(innovations),
                'backfill_jobs_completed': len([job for job in processed_jobs if job.status.value == 'completed']),
                'targeted_searches_completed': len(targeted_results),
                'database_updates': update_results['successful_updates'],
                'total_cost': total_cost,
                'cost_savings_estimate': self.estimate_manual_cost_savings(processed_jobs, targeted_results)
            }
            
            logger.info(f"✅ Backfill completed: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error in scheduled backfill: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def apply_backfill_results(self, backfill_jobs: List, targeted_results: List) -> Dict[str, Any]:
        """Apply backfill results to the database"""
        
        successful_updates = 0
        failed_updates = 0
        
        # Process comprehensive backfill results
        for job in backfill_jobs:
            if job.status.value == 'completed' and job.results:
                try:
                    updates = await self.create_database_updates_from_job(job)
                    if updates:
                        await self.apply_innovation_updates(job.innovation_id, updates)
                        successful_updates += 1
                        logger.info(f"Applied backfill updates for innovation {job.innovation_id}")
                
                except Exception as e:
                    logger.error(f"Error applying backfill for {job.innovation_id}: {e}")
                    failed_updates += 1
        
        # Process targeted search results
        for result in targeted_results:
            try:
                update_data = await self.create_database_update_from_targeted_result(result)
                if update_data:
                    await self.apply_innovation_updates(result.innovation_id, update_data)
                    successful_updates += 1
                    logger.info(f"Applied targeted search result for {result.innovation_id}: {result.field_name}")
            
            except Exception as e:
                logger.error(f"Error applying targeted result for {result.innovation_id}: {e}")
                failed_updates += 1
        
        return {
            'successful_updates': successful_updates,
            'failed_updates': failed_updates
        }
    
    async def create_database_updates_from_job(self, job) -> Optional[Dict[str, Any]]:
        """Convert backfill job results to database update format"""
        
        updates = {}
        
        for field_name, result in job.results.items():
            if isinstance(result, dict) and 'error' not in result:
                
                # Only apply high-confidence results
                confidence = result.get('confidence_score', 0.0)
                if confidence < 0.6:
                    continue
                
                value = result.get('new_value')
                if not value:
                    continue
                
                # Map field names to database columns
                if field_name == 'funding_amount' and isinstance(value, dict):
                    # Create funding record
                    funding_data = {
                        'amount': value.get('amount'),
                        'currency': value.get('currency', 'USD'),
                        'funding_type': 'ai_backfilled',
                        'funder_name': 'AI Discovered',
                        'verified': False  # Mark as unverified for human review
                    }
                    updates['fundings'] = [funding_data]
                
                elif field_name == 'website_url':
                    updates['website_url'] = value
                
                elif field_name == 'github_url':
                    updates['github_url'] = value
                
                elif field_name == 'demo_url':
                    updates['demo_url'] = value
                
                elif field_name == 'key_team_members' and isinstance(value, dict):
                    # Create individual records
                    team_data = []
                    for member in value.get('team_members', []):
                        team_data.append({
                            'name': member,
                            'role': 'ai_discovered',
                            'country': None
                        })
                    updates['individuals'] = team_data
                
                elif field_name == 'user_metrics' and isinstance(value, dict):
                    updates['impact_metrics'] = value
        
        return updates if updates else None
    
    async def create_database_update_from_targeted_result(self, result) -> Optional[Dict[str, Any]]:
        """Convert targeted search result to database update format"""
        
        if result.confidence_score < 0.6:
            return None
        
        updates = {}
        
        if result.field_name == 'funding_amount' and isinstance(result.extracted_value, dict):
            funding_data = {
                'amount': result.extracted_value.get('amount'),
                'currency': result.extracted_value.get('currency', 'USD'),
                'funding_type': 'targeted_search',
                'funder_name': 'Serper Discovered',
                'verified': False
            }
            updates['fundings'] = [funding_data]
        
        elif result.field_name == 'website_url':
            updates['website_url'] = result.extracted_value
        
        elif result.field_name == 'user_metrics' and isinstance(result.extracted_value, dict):
            updates['impact_metrics'] = result.extracted_value
        
        return updates if updates else None
    
    async def apply_innovation_updates(self, innovation_id: str, updates: Dict[str, Any]):
        """Apply updates to innovation record in database"""
        
        try:
            # Add metadata about the AI backfill
            updates['ai_backfill_metadata'] = {
                'last_backfill': datetime.now().isoformat(),
                'backfill_version': '1.0',
                'requires_human_review': True
            }
            
            response = supabase.table('innovations').update(updates).eq('id', innovation_id).execute()
            
            if response.data:
                logger.info(f"Successfully updated innovation {innovation_id}")
            else:
                logger.warning(f"No data returned for innovation update {innovation_id}")
        
        except Exception as e:
            logger.error(f"Database update failed for {innovation_id}: {e}")
            raise
    
    def estimate_manual_cost_savings(self, backfill_jobs: List, targeted_results: List) -> float:
        """Estimate the cost savings compared to manual research"""
        
        # Assume each successful backfill saves 30 minutes of manual research at $25/hour
        manual_research_cost_per_hour = 25.0
        time_saved_per_result = 0.5  # 30 minutes
        
        successful_backfills = len([job for job in backfill_jobs if job.status.value == 'completed'])
        successful_targeted = len(targeted_results)
        
        total_time_saved = (successful_backfills + successful_targeted) * time_saved_per_result
        manual_cost_saved = total_time_saved * manual_research_cost_per_hour
        
        ai_cost = sum(job.total_cost for job in backfill_jobs) + sum(result.search_cost for result in targeted_results)
        
        return manual_cost_saved - ai_cost
    
    def get_backfill_status(self) -> Dict[str, Any]:
        """Get current status of the backfill system"""
        
        return {
            'last_run': self.last_backfill_run.isoformat() if self.last_backfill_run else None,
            'next_run_due': (self.last_backfill_run + self.backfill_interval).isoformat() if self.last_backfill_run else 'now',
            'backfill_interval_hours': self.backfill_interval.total_seconds() / 3600,
            'ai_backfill_stats': ai_backfill_service.get_backfill_stats()
        }


# Global integration service instance
backfill_integration = BackfillIntegrationService()


# Main function for use in scheduled jobs (e.g., cron, celery)
async def run_scheduled_ai_backfill() -> Dict[str, Any]:
    """Main entry point for scheduled AI backfill process"""
    return await backfill_integration.run_scheduled_backfill()


# Function to check system status
def get_ai_backfill_system_status() -> Dict[str, Any]:
    """Get comprehensive status of the AI backfill system"""
    return backfill_integration.get_backfill_status()


# Integration with existing ETL pipeline
async def integrate_with_etl_pipeline():
    """
    Example of how to integrate with existing ETL pipeline
    
    Add this to your main ETL orchestrator:
    """
    
    # After processing new articles and before final database commit
    logger.info("Running AI backfill as part of ETL pipeline")
    
    # Run backfill if due
    backfill_result = await run_scheduled_ai_backfill()
    
    if backfill_result['status'] == 'completed':
        logger.info(f"AI backfill completed: {backfill_result['innovations_processed']} innovations processed")
        logger.info(f"Cost: ${backfill_result['total_cost']:.2f}, Savings: ${backfill_result['cost_savings_estimate']:.2f}")
    
    return backfill_result


if __name__ == "__main__":
    # Test the integration
    async def test_integration():
        print("🔗 Testing AI Backfill Integration")
        
        # Get status
        status = get_ai_backfill_system_status()
        print(f"System status: {status}")
        
        # Test backfill (would run actual process in production)
        # result = await run_scheduled_ai_backfill()
        # print(f"Backfill result: {result}")
    
    asyncio.run(test_integration())