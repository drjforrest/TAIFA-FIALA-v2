"""
ETL Monitoring Service
Tracks ETL job performance, system health, and provides status APIs
"""

import asyncio
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

from config.database import get_db
from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class ETLJobStatus:
    name: str
    last_run: Optional[datetime]
    last_success: Optional[datetime]
    last_error: Optional[str]
    success_count: int
    error_count: int
    avg_runtime: float
    is_running: bool
    items_processed: int
    health_status: str

@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    database_status: str
    vector_db_status: str
    timestamp: datetime

class ETLMonitor:
    def __init__(self):
        self.status_file = Path("data/etl_status.json")
        self.job_statuses: Dict[str, ETLJobStatus] = {}
        self.status_file.parent.mkdir(exist_ok=True)
        self.load_status()
        
    def load_status(self):
        """Load ETL job statuses from persistent storage"""
        if not self.status_file.exists():
            return
            
        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
                for name, status_data in data.items():
                    self.job_statuses[name] = ETLJobStatus(
                        name=name,
                        last_run=datetime.fromisoformat(status_data['last_run']) if status_data.get('last_run') else None,
                        last_success=datetime.fromisoformat(status_data['last_success']) if status_data.get('last_success') else None,
                        last_error=status_data.get('last_error'),
                        success_count=status_data.get('success_count', 0),
                        error_count=status_data.get('error_count', 0),
                        avg_runtime=status_data.get('avg_runtime', 0.0),
                        is_running=False,  # Always reset on startup
                        items_processed=status_data.get('items_processed', 0),
                        health_status="unknown"
                    )
        except Exception as e:
            logger.error(f"Error loading ETL status: {e}")
    
    def save_status(self):
        """Save current status to persistent storage"""
        try:
            data = {}
            for name, status in self.job_statuses.items():
                data[name] = {
                    'last_run': status.last_run.isoformat() if status.last_run else None,
                    'last_success': status.last_success.isoformat() if status.last_success else None,
                    'last_error': status.last_error,
                    'success_count': status.success_count,
                    'error_count': status.error_count,
                    'avg_runtime': status.avg_runtime,
                    'items_processed': status.items_processed
                }
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving ETL status: {e}")
    
    def start_job(self, job_name: str):
        """Mark job as starting"""
        if job_name not in self.job_statuses:
            self.job_statuses[job_name] = ETLJobStatus(
                name=job_name,
                last_run=None,
                last_success=None,
                last_error=None,
                success_count=0,
                error_count=0,
                avg_runtime=0.0,
                is_running=False,
                items_processed=0,
                health_status="unknown"
            )
        
        self.job_statuses[job_name].is_running = True
        self.job_statuses[job_name].last_run = datetime.now()
        logger.info(f"ETL job started: {job_name}")
        self.save_status()
    
    def complete_job(self, job_name: str, success: bool, runtime: float = 0, 
                    items_processed: int = 0, error_msg: str = None):
        """Mark job as completed"""
        if job_name not in self.job_statuses:
            return
        
        status = self.job_statuses[job_name]
        status.is_running = False
        
        if success:
            status.last_success = datetime.now()
            status.success_count += 1
            status.items_processed += items_processed
            status.last_error = None
            
            # Update average runtime
            if status.success_count == 1:
                status.avg_runtime = runtime
            else:
                status.avg_runtime = (status.avg_runtime * (status.success_count - 1) + runtime) / status.success_count
                
            logger.info(f"ETL job completed successfully: {job_name} ({items_processed} items, {runtime:.1f}s)")
        else:
            status.error_count += 1
            status.last_error = error_msg
            logger.error(f"ETL job failed: {job_name} - {error_msg}")
        
        # Update health status
        status.health_status = self._calculate_health_status(status)
        self.save_status()
    
    def _calculate_health_status(self, status: ETLJobStatus) -> str:
        """Calculate job health status"""
        if status.is_running:
            return "running"
        
        if not status.last_run:
            return "never_run"
        
        # Check if job is stale (no run in 24 hours for regular jobs)
        if datetime.now() - status.last_run > timedelta(hours=24):
            return "stale"
        
        # Check if recent runs are failing
        if status.last_success is None:
            return "failing"
        
        if status.last_run > status.last_success:
            return "failing"
        
        return "healthy"
    
    async def get_system_health(self) -> SystemHealth:
        """Get current system health metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health check
            database_status = await self._check_database_health()
            
            # Vector DB health check (placeholder)
            vector_db_status = "healthy"  # Would implement actual Pinecone check
            
            return SystemHealth(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk.percent,
                database_status=database_status,
                vector_db_status=vector_db_status,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(0, 0, 0, "error", "error", datetime.now())
    
    async def _check_database_health(self) -> str:
        """Check database connectivity and health"""
        try:
            db = next(get_db())
            result = db.execute(text("SELECT 1")).fetchone()
            db.close()
            return "healthy" if result else "error"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "error"
    
    def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent ETL activity"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_jobs = []
        
        for name, status in self.job_statuses.items():
            if status.last_run and status.last_run > cutoff:
                recent_jobs.append({
                    'name': name,
                    'last_run': status.last_run.isoformat(),
                    'success': status.last_success and status.last_success >= status.last_run,
                    'items_processed': status.items_processed,
                    'error': status.last_error,
                    'runtime': status.avg_runtime
                })
        
        return sorted(recent_jobs, key=lambda x: x['last_run'], reverse=True)
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data for monitoring dashboard"""
        # Refresh health status for all jobs
        for status in self.job_statuses.values():
            status.health_status = self._calculate_health_status(status)
        
        system_health = await self.get_system_health()
        recent_activity = self.get_recent_activity()
        
        # Calculate summary stats
        total_jobs = len(self.job_statuses)
        running_jobs = sum(1 for s in self.job_statuses.values() if s.is_running)
        healthy_jobs = sum(1 for s in self.job_statuses.values() if s.health_status == "healthy")
        failed_jobs = sum(1 for s in self.job_statuses.values() if s.health_status == "failing")
        
        total_runs = sum(s.success_count + s.error_count for s in self.job_statuses.values())
        total_successes = sum(s.success_count for s in self.job_statuses.values())
        success_rate = (total_successes / max(1, total_runs)) * 100
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_health': asdict(system_health),
            'job_summary': {
                'total_jobs': total_jobs,
                'running_jobs': running_jobs,
                'healthy_jobs': healthy_jobs,
                'failed_jobs': failed_jobs,
                'success_rate': round(success_rate, 1)
            },
            'job_statuses': [
                {
                    **asdict(status),
                    'last_run': status.last_run.isoformat() if status.last_run else None,
                    'last_success': status.last_success.isoformat() if status.last_success else None,
                }
                for status in self.job_statuses.values()
            ],
            'recent_activity': recent_activity[:10]  # Last 10 activities
        }

# Global monitor instance
etl_monitor = ETLMonitor()

# Context manager for ETL job monitoring
class ETLJobContext:
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.start_time = None
        self.items_processed = 0
    
    def __enter__(self):
        self.start_time = datetime.now()
        etl_monitor.start_job(self.job_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        runtime = (datetime.now() - self.start_time).total_seconds()
        success = exc_type is None
        error_msg = str(exc_val) if exc_val else None
        
        etl_monitor.complete_job(
            self.job_name, 
            success, 
            runtime, 
            self.items_processed, 
            error_msg
        )
    
    def add_processed_items(self, count: int):
        """Add to the count of items processed"""
        self.items_processed += count

# Usage example:
# with ETLJobContext("arxiv_scraper") as job:
#     # Do ETL work
#     papers = scrape_papers()
#     job.add_processed_items(len(papers))
#     # If exception occurs, it's automatically logged as failure
