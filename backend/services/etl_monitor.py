"""
ETL Monitoring Service
Tracks what validation jobs are working/failing
"""

import asyncio
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from config.database import get_db

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
    description: str

@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    database_status: str
    vector_db_status: str
    last_check: datetime

class ETLMonitor:
    def __init__(self):
        self.status_file = Path("data/etl_status.json")
        self.job_statuses: Dict[str, ETLJobStatus] = {}
        self.initialize_jobs()
        
    def initialize_jobs(self):
        """Initialize known ETL jobs"""
        jobs = {
            "arxiv_scraper": "Academic publication discovery",
            "news_monitor": "Innovation news monitoring", 
            "serper_search": "Web search for AI projects",
            "crawl4ai": "Project website analysis",
            "startup_tracker": "Startup database monitoring",
            "funding_tracker": "Investment announcement tracking"
        }
        
        for name, description in jobs.items():
            if name not in self.job_statuses:
                self.job_statuses[name] = ETLJobStatus(
                    name=name,
                    description=description,
                    last_run=None,
                    last_success=None,
                    last_error=None,
                    success_count=0,
                    error_count=0,
                    avg_runtime=0.0,
                    is_running=False,
                    items_processed=0
                )
    
    def load_status(self):
        """Load persisted job status"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    for name, status_data in data.items():
                        if name in self.job_statuses:
                            status = self.job_statuses[name]
                            status.last_run = datetime.fromisoformat(status_data.get('last_run')) if status_data.get('last_run') else None
                            status.last_success = datetime.fromisoformat(status_data.get('last_success')) if status_data.get('last_success') else None
                            status.last_error = status_data.get('last_error')
                            status.success_count = status_data.get('success_count', 0)
                            status.error_count = status_data.get('error_count', 0)
                            status.avg_runtime = status_data.get('avg_runtime', 0.0)
                            status.items_processed = status_data.get('items_processed', 0)
                            status.is_running = False  # Reset on startup
            except Exception as e:
                logger.error(f"Error loading ETL status: {e}")
    
    def save_status(self):
        """Persist current status"""
        try:
            self.status_file.parent.mkdir(exist_ok=True)
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
        """Mark job as running"""
        if job_name in self.job_statuses:
            self.job_statuses[job_name].is_running = True
            logger.info(f"Started ETL job: {job_name}")
    
    def complete_job(self, job_name: str, success: bool, runtime: float = 0, 
                    items_processed: int = 0, error_msg: str = None):
        """Update job status after completion"""
        if job_name not in self.job_statuses:
            return
            
        status = self.job_statuses[job_name]
        status.last_run = datetime.now()
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
                status.avg_runtime = (status.avg_runtime + runtime) / 2
                
            logger.info(f"ETL job {job_name} completed successfully: {items_processed} items processed in {runtime:.1f}s")
        else:
            status.error_count += 1
            status.last_error = error_msg
            logger.error(f"ETL job {job_name} failed: {error_msg}")
        
        self.save_status()
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Test database connectivity
            db_status = "healthy"
            try:
                db = next(get_db())
                db.execute("SELECT 1")
                db.close()
            except Exception as e:
                db_status = f"error: {str(e)[:50]}"
            
            # Vector DB status (placeholder)
            vector_status = "healthy"  # Would test actual vector DB
            
            return SystemHealth(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk.percent,
                database_status=db_status,
                vector_db_status=vector_status,
                last_check=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(0, 0, 0, "error", "error", datetime.now())
    
    def get_validation_summary(self) -> Dict:
        """Get summary of validation system performance"""
        self.load_status()
        
        total_items = sum(s.items_processed for s in self.job_statuses.values())
        active_jobs = sum(1 for s in self.job_statuses.values() if s.is_running)
        failed_jobs = sum(1 for s in self.job_statuses.values() 
                         if s.last_run and s.error_count > 0 and 
                         (not s.last_success or s.last_success < s.last_run))
        
        success_rate = 0
        total_runs = sum(s.success_count + s.error_count for s in self.job_statuses.values())
        if total_runs > 0:
            success_rate = (sum(s.success_count for s in self.job_statuses.values()) / total_runs) * 100
        
        return {
            "validation_system_status": "active" if active_jobs > 0 else "idle",
            "total_discoveries": total_items,
            "active_jobs": active_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": round(success_rate, 1),
            "last_activity": max([s.last_run for s in self.job_statuses.values() if s.last_run], default=None)
        }
    
    def get_recent_discoveries(self, hours: int = 24) -> List[Dict]:
        """Get recent ETL discoveries"""
        cutoff = datetime.now() - timedelta(hours=hours)
        discoveries = []
        
        for name, status in self.job_statuses.items():
            if status.last_success and status.last_success > cutoff and status.items_processed > 0:
                discoveries.append({
                    "job_name": name,
                    "description": status.description,
                    "items_found": status.items_processed,
                    "discovered_at": status.last_success,
                    "runtime": status.avg_runtime
                })
        
        return sorted(discoveries, key=lambda x: x['discovered_at'], reverse=True)
    
    def get_job_health(self, status: ETLJobStatus) -> str:
        """Determine job health status"""
        if status.is_running:
            return "running"
        
        if not status.last_run:
            return "never_run"
        
        # If last run was more than 48 hours ago for critical jobs
        if datetime.now() - status.last_run > timedelta(hours=48):
            return "stale"
        
        # If last success was not the last run
        if status.last_success and status.last_run and status.last_success < status.last_run:
            return "failing"
        
        if not status.last_success:
            return "failing"
        
        return "healthy"
    
    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        self.load_status()
        
        system_health = self.get_system_health()
        validation_summary = self.get_validation_summary()
        recent_discoveries = self.get_recent_discoveries()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": asdict(system_health),
            "validation_summary": validation_summary,
            "job_statuses": [
                {
                    **asdict(status),
                    "last_run": status.last_run.isoformat() if status.last_run else None,
                    "last_success": status.last_success.isoformat() if status.last_success else None,
                    "health_status": self.get_job_health(status)
                }
                for status in self.job_statuses.values()
            ],
            "recent_discoveries": [
                {
                    **disc,
                    "discovered_at": disc["discovered_at"].isoformat()
                }
                for disc in recent_discoveries
            ]
        }

# Global monitor instance
etl_monitor = ETLMonitor()
