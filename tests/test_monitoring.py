#!/usr/bin/env python3
"""
Test ETL monitoring system
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('/Users/drjforrest/dev/devprojects/TAIFA-FIALA/backend')

from services.etl_monitor import etl_monitor
from services.etl_context import ETLJobContext
import time
import random

async def test_monitoring():
    """Test the ETL monitoring system"""
    print("Testing ETL Monitoring System...")
    
    # Simulate some ETL jobs
    jobs = [
        ("arxiv_scraper", True, 45.2, 25),
        ("news_monitor", False, 12.1, 0),
        ("serper_search", True, 23.5, 50),
        ("startup_tracker", True, 67.8, 15)
    ]
    
    print("\n1. Simulating ETL job runs...")
    for job_name, success, runtime, items in jobs:
        with ETLJobContext(job_name) as job:
            # Simulate work
            await asyncio.sleep(0.1)
            job.add_processed_items(items)
            
            if not success:
                raise Exception("Simulated job failure")
            
        print(f"   ✓ {job_name}: {items} items in {runtime:.1f}s")
    
    print("\n2. Getting dashboard data...")
    dashboard_data = etl_monitor.get_dashboard_data()
    
    print(f"\nValidation System Summary:")
    print(f"- Total discoveries: {dashboard_data['validation_summary']['total_discoveries']}")
    print(f"- Success rate: {dashboard_data['validation_summary']['success_rate']}%")
    print(f"- Active jobs: {dashboard_data['validation_summary']['active_jobs']}")
    print(f"- Failed jobs: {dashboard_data['validation_summary']['failed_jobs']}")
    
    print(f"\nSystem Health:")
    health = dashboard_data['system_health']
    print(f"- CPU: {health['cpu_percent']:.1f}%")
    print(f"- Memory: {health['memory_percent']:.1f}%")
    print(f"- Database: {health['database_status']}")
    
    print(f"\nJob Statuses:")
    for job in dashboard_data['job_statuses']:
        status_icon = "✅" if job['health_status'] == 'healthy' else "❌"
        print(f"   {status_icon} {job['name']}: {job['items_processed']} items, {job['success_count']} successes")
    
    print("\n✅ Monitoring system is working!")
    return dashboard_data

if __name__ == "__main__":
    asyncio.run(test_monitoring())
