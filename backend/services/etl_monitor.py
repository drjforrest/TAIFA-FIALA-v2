"""
Enhanced ETL Monitoring Service
Comprehensive status tracking and metrics collection for TAIFA-FIALA ETL pipelines
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import psutil
from config.database import get_db

logger = logging.getLogger(__name__)

@dataclass
class ETLMetrics:
    """Comprehensive ETL metrics for each pipeline run"""
    batch_size: int = 0
    duplicates_removed: int = 0
    processing_time_ms: int = 0
    success_rate: float = 0.0
    items_processed: int = 0
    items_failed: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

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
    status: str  # idle, running, completed, error
    metrics: ETLMetrics
    pipeline_active: bool  # For frontend compatibility

@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    database_status: str
    vector_db_status: str
    last_check: datetime

@dataclass
class UnifiedETLStatus:
    """Unified status format matching frontend expectations"""
    academic_pipeline_active: bool
    news_pipeline_active: bool
    serper_pipeline_active: bool
    enrichment_pipeline_active: bool
    last_academic_run: Optional[str]
    last_news_run: Optional[str]
    last_serper_run: Optional[str]
    last_enrichment_run: Optional[str]
    total_processed_today: int
    errors_today: int
    system_health: str
    last_updated: str

class ETLMonitor:
    def __init__(self):
        self.status_file = Path("backend/data/etl_status.json")
        self.job_statuses: Dict[str, ETLJobStatus] = {}
        self.initialize_jobs()
        self.load_status()
        
    def initialize_jobs(self):
        """Initialize known ETL jobs with enhanced tracking"""
        jobs = {
            "academic_pipeline": "Academic publication discovery (ArXiv, PubMed)",
            "news_pipeline": "Innovation news monitoring (RSS feeds)", 
            "serper_pipeline": "Web search for AI projects and startups",
            "enrichment_pipeline": "AI intelligence enrichment (Perplexity, OpenAI)",
            "crawl4ai": "Project website analysis and content extraction",
            "startup_tracker": "Startup database monitoring and updates",
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
                    items_processed=0,
                    status="idle",
                    metrics=ETLMetrics(),
                    pipeline_active=False
                )
    
    def load_status(self):
        """Load persisted job status with enhanced error handling"""
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
                            status.status = "idle"  # Reset on startup
                            status.pipeline_active = False  # Reset on startup
                            
                            # Load metrics if available
                            metrics_data = status_data.get('metrics', {})
                            status.metrics = ETLMetrics(
                                batch_size=metrics_data.get('batch_size', 0),
                                duplicates_removed=metrics_data.get('duplicates_removed', 0),
                                processing_time_ms=metrics_data.get('processing_time_ms', 0),
                                success_rate=metrics_data.get('success_rate', 0.0),
                                items_processed=metrics_data.get('items_processed', 0),
                                items_failed=metrics_data.get('items_failed', 0),
                                memory_usage_mb=metrics_data.get('memory_usage_mb', 0.0),
                                cpu_usage_percent=metrics_data.get('cpu_usage_percent', 0.0)
                            )
            except Exception as e:
                logger.error(f"Error loading ETL status: {e}")
    
    def save_status(self):
        """Persist current status with comprehensive metrics"""
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
                    'items_processed': status.items_processed,
                    'status': status.status,
                    'pipeline_active': status.pipeline_active,
                    'metrics': asdict(status.metrics)
                }
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving ETL status: {e}")
    
    def start_job(self, job_name: str) -> bool:
        """Mark job as running with proper state transitions"""
        if job_name not in self.job_statuses:
            logger.error(f"Unknown job: {job_name}")
            return False
            
        status = self.job_statuses[job_name]
        
        if status.is_running:
            logger.warning(f"Job {job_name} is already running")
            return False
            
        status.is_running = True
        status.pipeline_active = True
        status.status = "running"
        status.last_run = datetime.now()
        
        # Reset metrics for new run
        status.metrics = ETLMetrics()
        
        self.save_status()
        logger.info(f"Started ETL job: {job_name}")
        return True
    
    def complete_job(self, job_name: str, success: bool, runtime: float = 0, 
                    items_processed: int = 0, error_msg: str = None,
                    metrics: Optional[ETLMetrics] = None):
        """Update job status after completion with comprehensive metrics"""
        if job_name not in self.job_statuses:
            logger.error(f"Unknown job: {job_name}")
            return
            
        status = self.job_statuses[job_name]
        now = datetime.now()
        status.last_run = now
        status.is_running = False
        status.pipeline_active = False
        
        # Update metrics
        if metrics:
            status.metrics = metrics
        else:
            status.metrics.processing_time_ms = int(runtime * 1000)
            status.metrics.items_processed = items_processed
        
        if success:
            status.last_success = now
            status.success_count += 1
            status.items_processed += items_processed
            status.last_error = None
            status.status = "completed"
            
            # Update average runtime
            if status.success_count == 1:
                status.avg_runtime = runtime
            else:
                status.avg_runtime = (status.avg_runtime + runtime) / 2
            
            # Calculate success rate
            total_runs = status.success_count + status.error_count
            status.metrics.success_rate = (status.success_count / total_runs) * 100 if total_runs > 0 else 0
                
            logger.info(f"ETL job {job_name} completed successfully: {items_processed} items processed in {runtime:.1f}s")
        else:
            status.error_count += 1
            status.last_error = error_msg
            status.status = "error"
            status.metrics.items_failed += 1
            
            # Calculate success rate
            total_runs = status.success_count + status.error_count
            status.metrics.success_rate = (status.success_count / total_runs) * 100 if total_runs > 0 else 0
            
            logger.error(f"ETL job {job_name} failed: {error_msg}")
        
        # Transition back to idle after a delay for completed jobs
        if success:
            asyncio.create_task(self._transition_to_idle(job_name, delay=5))
        
        self.save_status()
    
    async def _transition_to_idle(self, job_name: str, delay: int = 5):
        """Transition job status from completed to idle after delay"""
        await asyncio.sleep(delay)
        if job_name in self.job_statuses:
            status = self.job_statuses[job_name]
            if status.status == "completed":
                status.status = "idle"
                self.save_status()
                logger.info(f"Job {job_name} transitioned to idle")
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health with enhanced monitoring"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Test database connectivity
            db_status = "healthy"
            try:
                db = next(get_db())
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
                db.close()
            except Exception as e:
                db_status = f"error: {str(e)[:50]}"
            
            # Vector DB status (placeholder - would test actual vector DB)
            vector_status = "healthy"
            
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
    
    def get_unified_status(self) -> UnifiedETLStatus:
        """Get status in format expected by frontend"""
        self.load_status()
        
        # Calculate today's totals
        today = datetime.now().date()
        total_processed_today = 0
        errors_today = 0
        
        for status in self.job_statuses.values():
            if status.last_run and status.last_run.date() == today:
                if status.last_success and status.last_success.date() == today:
                    total_processed_today += status.metrics.items_processed
                if status.last_error and status.last_run.date() == today:
                    errors_today += 1
        
        # Get system health
        system_health = self.get_system_health()
        health_status = "healthy"
        if system_health.database_status != "healthy" or system_health.vector_db_status != "healthy":
            health_status = "degraded"
        if system_health.cpu_percent > 90 or system_health.memory_percent > 90:
            health_status = "degraded"
        
        return UnifiedETLStatus(
            academic_pipeline_active=self.job_statuses.get("academic_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).pipeline_active,
            news_pipeline_active=self.job_statuses.get("news_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).pipeline_active,
            serper_pipeline_active=self.job_statuses.get("serper_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).pipeline_active,
            enrichment_pipeline_active=self.job_statuses.get("enrichment_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).pipeline_active,
            last_academic_run=self.job_statuses.get("academic_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run.isoformat() if self.job_statuses.get("academic_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run else None,
            last_news_run=self.job_statuses.get("news_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run.isoformat() if self.job_statuses.get("news_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run else None,
            last_serper_run=self.job_statuses.get("serper_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run.isoformat() if self.job_statuses.get("serper_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run else None,
            last_enrichment_run=self.job_statuses.get("enrichment_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run.isoformat() if self.job_statuses.get("enrichment_pipeline", ETLJobStatus("", None, None, None, 0, 0, 0, False, 0, "", "idle", ETLMetrics(), False)).last_run else None,
            total_processed_today=total_processed_today,
            errors_today=errors_today,
            system_health=health_status,
            last_updated=datetime.now().isoformat()
        )
    
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
        """Get recent ETL discoveries with enhanced metrics"""
        cutoff = datetime.now() - timedelta(hours=hours)
        discoveries = []
        
        for name, status in self.job_statuses.items():
            if status.last_success and status.last_success > cutoff and status.items_processed > 0:
                discoveries.append({
                    "job_name": name,
                    "description": status.description,
                    "items_found": status.metrics.items_processed,
                    "duplicates_removed": status.metrics.duplicates_removed,
                    "processing_time_ms": status.metrics.processing_time_ms,
                    "success_rate": status.metrics.success_rate,
                    "discovered_at": status.last_success,
                    "runtime": status.avg_runtime
                })
        
        return sorted(discoveries, key=lambda x: x['discovered_at'], reverse=True)
    
    def get_job_health(self, status: ETLJobStatus) -> str:
        """Determine job health status with enhanced logic"""
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
        """Get complete dashboard data with enhanced metrics"""
        self.load_status()
        
        system_health = self.get_system_health()
        validation_summary = self.get_validation_summary()
        recent_discoveries = self.get_recent_discoveries()
        unified_status = self.get_unified_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": asdict(system_health),
            "validation_summary": validation_summary,
            "unified_status": asdict(unified_status),
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
