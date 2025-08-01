"""
ETL Job Context Manager
Integrates monitoring into ETL jobs
"""

import time
from contextlib import contextmanager
from typing import Optional
from services.etl_monitor import etl_monitor

class ETLJobContext:
    """Context manager for ETL job monitoring"""
    
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.start_time = None
        self.items_processed = 0
        
    def __enter__(self):
        self.start_time = time.time()
        etl_monitor.start_job(self.job_name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        runtime = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            # Success
            etl_monitor.complete_job(
                job_name=self.job_name,
                success=True,
                runtime=runtime,
                items_processed=self.items_processed
            )
        else:
            # Failure
            error_msg = str(exc_val) if exc_val else "Unknown error"
            etl_monitor.complete_job(
                job_name=self.job_name,
                success=False,
                runtime=runtime,
                items_processed=self.items_processed,
                error_msg=error_msg
            )
        
        return False  # Don't suppress exceptions
    
    def add_processed_items(self, count: int):
        """Add to the count of items processed"""
        self.items_processed += count
