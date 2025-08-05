"""
Live ETL API Endpoints for TAIFA-FIALA Dashboard
Real-time pipeline triggers for interactive dashboard with comprehensive metrics
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from config.database import get_supabase
from etl.academic.arxiv_scraper import scrape_arxiv_papers
from etl.intelligence.perplexity_african_ai import (
    IntelligenceType,
    PerplexityAfricanAIModule,
)
from etl.news.rss_monitor import monitor_rss_feeds
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel
from services.enrichment_scheduler import get_enrichment_scheduler
from services.etl_monitor import ETLMetrics, etl_monitor
from services.vector_service import get_vector_service

router = APIRouter(prefix="/api/etl", tags=["ETL Live"])

class ETLResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

@router.get("/status")
async def get_etl_status():
    """Get current ETL pipeline status in format expected by frontend"""
    try:
        # Get unified status from enhanced monitor
        unified_status = etl_monitor.get_unified_status()
        dashboard_data = etl_monitor.get_dashboard_data()
        
        return {
            "success": True,
            "data": {
                # Frontend-compatible format
                "pipelines": {
                    "academic_pipeline": {
                        "status": "running" if unified_status.academic_pipeline_active else "idle",
                        "last_run": unified_status.last_academic_run,
                        "items_processed": next((job["items_processed"] for job in dashboard_data["job_statuses"] if job["name"] == "academic_pipeline"), 0),
                        "errors": next((job["error_count"] for job in dashboard_data["job_statuses"] if job["name"] == "academic_pipeline"), 0)
                    },
                    "news_pipeline": {
                        "status": "running" if unified_status.news_pipeline_active else "idle",
                        "last_run": unified_status.last_news_run,
                        "items_processed": next((job["items_processed"] for job in dashboard_data["job_statuses"] if job["name"] == "news_pipeline"), 0),
                        "errors": next((job["error_count"] for job in dashboard_data["job_statuses"] if job["name"] == "news_pipeline"), 0)
                    },
                    "discovery_pipeline": {
                        "status": "running" if unified_status.serper_pipeline_active else "idle",
                        "last_run": unified_status.last_serper_run,
                        "items_processed": next((job["items_processed"] for job in dashboard_data["job_statuses"] if job["name"] == "serper_pipeline"), 0),
                        "errors": next((job["error_count"] for job in dashboard_data["job_statuses"] if job["name"] == "serper_pipeline"), 0)
                    },
                    "enrichment_pipeline": {
                        "status": "running" if unified_status.enrichment_pipeline_active else "idle",
                        "last_run": unified_status.last_enrichment_run,
                        "items_processed": next((job["items_processed"] for job in dashboard_data["job_statuses"] if job["name"] == "enrichment_pipeline"), 0),
                        "errors": next((job["error_count"] for job in dashboard_data["job_statuses"] if job["name"] == "enrichment_pipeline"), 0)
                    }
                },
                "system_health": unified_status.system_health,
                "last_updated": unified_status.last_updated,
                # Additional metrics for dashboard
                "total_processed_today": unified_status.total_processed_today,
                "errors_today": unified_status.errors_today,
                "recent_discoveries": dashboard_data["recent_discoveries"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting ETL status: {e}")
        return {
            "success": False,
            "message": f"Error retrieving ETL status: {str(e)}",
            "data": {
                "pipelines": {},
                "system_health": "error",
                "last_updated": datetime.now().isoformat()
            }
        }

@router.post("/trigger/news")
async def trigger_news_pipeline(background_tasks: BackgroundTasks):
    """Trigger RSS news monitoring pipeline - FREE operation"""
    
    # Check if pipeline is already running using enhanced monitor
    if not etl_monitor.start_job("news_pipeline"):
        return ETLResponse(
            success=False,
            message="News pipeline is already running"
        )
    
    # Start the background task
    background_tasks.add_task(run_news_pipeline)
    
    return ETLResponse(
        success=True,
        message="News pipeline started - monitoring African tech feeds",
        data={"pipeline": "news", "status": "started"}
    )

@router.post("/trigger/academic")
async def trigger_academic_pipeline(background_tasks: BackgroundTasks, days_back: int = 3, max_results: int = 10):
    """Trigger academic paper scraping pipeline - FREE operation"""
    
    # Check if pipeline is already running using enhanced monitor
    if not etl_monitor.start_job("academic_pipeline"):
        return ETLResponse(
            success=False,
            message="Academic pipeline is already running"
        )
    
    # Start the background task
    background_tasks.add_task(run_academic_pipeline, days_back, max_results)
    
    return ETLResponse(
        success=True,
        message="Academic pipeline started - scanning recent AI research",
        data={"pipeline": "academic", "status": "started", "params": {"days_back": days_back, "max_results": max_results}}
    )

@router.post("/trigger/discovery")
async def trigger_discovery_pipeline(background_tasks: BackgroundTasks, query: str = "African AI innovation"):
    """Trigger innovation discovery pipeline - RATE LIMITED operation"""
    
    # Check if pipeline is already running using enhanced monitor
    if not etl_monitor.start_job("serper_pipeline"):
        return ETLResponse(
            success=False,
            message="Discovery pipeline is already running"
        )
    
    # For now, we'll just do vector search to demonstrate
    background_tasks.add_task(run_discovery_pipeline, query)
    
    return ETLResponse(
        success=True,
        message="Discovery pipeline started - searching innovation database",
        data={"pipeline": "discovery", "status": "started", "query": query}
    )

@router.post("/trigger/enrichment")
async def trigger_enrichment_pipeline(
    background_tasks: BackgroundTasks, 
    intelligence_types: List[str] = ["innovation_discovery", "funding_landscape"],
    time_period: str = "last_7_days",
    geographic_focus: List[str] = None,
    provider: str = "perplexity"
):
    """Trigger AI intelligence enrichment - supports multiple providers (Perplexity, OpenAI, etc.) - RATE LIMITED operation"""
    
    # Check if pipeline is already running using enhanced monitor
    if not etl_monitor.start_job("enrichment_pipeline"):
        return ETLResponse(
            success=False,
            message="AI enrichment pipeline is already running"
        )
    
    # Convert string intelligence types to enum values
    try:
        intel_types = []
        for intel_type_str in intelligence_types:
            if hasattr(IntelligenceType, intel_type_str.upper()):
                intel_types.append(IntelligenceType(intel_type_str))
            else:
                # Fallback mapping
                intel_types.append(IntelligenceType.INNOVATION_DISCOVERY)
    except Exception:
        intel_types = [IntelligenceType.INNOVATION_DISCOVERY, IntelligenceType.FUNDING_LANDSCAPE]
    
    # Start the background task
    background_tasks.add_task(run_enrichment_pipeline, intel_types, time_period, geographic_focus, provider)
    
    return ETLResponse(
        success=True,
        message=f"AI intelligence enrichment started with {provider} - analyzing African AI ecosystem",
        data={
            "pipeline": "enrichment", 
            "status": "started", 
            "provider": provider,
            "intelligence_types": intelligence_types,
            "time_period": time_period,
            "geographic_focus": geographic_focus or ["Nigeria", "Kenya", "South Africa", "Ghana", "Egypt"]
        }
    )

@router.get("/results/news")
async def get_recent_news_results(limit: int = 10):
    """Get recent news pipeline results"""
    try:
        # Get recent articles from vector database
        vector_service = await get_vector_service()
        results = await vector_service.search_similar("African technology news", top_k=limit)
        
        articles = []
        for result in results:
            if result.metadata.get("content_type") == "news_article":
                articles.append({
                    "title": result.metadata.get("title", "No title"),
                    "source": result.metadata.get("source", "Unknown"),
                    "url": result.metadata.get("url", ""),
                    "published_date": result.metadata.get("published_date"),
                    "score": result.score
                })
        
        return ETLResponse(
            success=True,
            message=f"Found {len(articles)} recent articles",
            data={"articles": articles}
        )
        
    except Exception as e:
        logger.error(f"Error getting news results: {e}")
        return ETLResponse(
            success=False,
            message=f"Error retrieving news results: {str(e)}"
        )

@router.get("/results/academic")
async def get_recent_academic_results(limit: int = 10):
    """Get recent academic pipeline results"""
    try:
        # Get recent papers from database
        supabase = get_supabase()
        response = supabase.table('publications').select(
            'id, title, authors, publication_date, source, african_relevance_score, ai_relevance_score, url'
        ).order('created_at', desc=True).limit(limit).execute()
        
        papers = response.data or []
        
        return ETLResponse(
            success=True,
            message=f"Found {len(papers)} recent papers",
            data={"papers": papers}
        )
        
    except Exception as e:
        logger.error(f"Error getting academic results: {e}")
        return ETLResponse(
            success=False,
            message=f"Error retrieving academic results: {str(e)}"
        )

@router.get("/results/innovations")
async def get_recent_innovations(limit: int = 10):
    """Get recent innovations from database"""
    try:
        supabase = get_supabase()
        response = supabase.table('innovations').select(
            'id, title, description, domain, development_stage, countries_deployed, verification_status'
        ).eq('visibility', 'public').order('created_at', desc=True).limit(limit).execute()
        
        innovations = response.data or []
        
        return ETLResponse(
            success=True,
            message=f"Found {len(innovations)} recent innovations",
            data={"innovations": innovations}
        )
        
    except Exception as e:
        logger.error(f"Error getting innovations: {e}")
        return ETLResponse(
            success=False,
            message=f"Error retrieving innovations: {str(e)}"
        )

@router.get("/results/enrichment")
async def get_recent_enrichment_results(limit: int = 10):
    """Get recent AI enrichment intelligence reports"""
    try:
        # Try to get from vector database first for semantic search
        vector_service = await get_vector_service()
        results = await vector_service.search_similar("AI intelligence report", top_k=limit)
        
        reports = []
        for result in results:
            if result.metadata.get("content_type") == "enrichment_report":
                reports.append({
                    "report_id": result.metadata.get("report_id", "No ID"),
                    "title": result.metadata.get("title", "No title"),
                    "report_type": result.metadata.get("report_type", "Unknown"),
                    "provider": result.metadata.get("provider", "Unknown"),
                    "confidence_score": result.metadata.get("confidence_score", 0),
                    "generation_timestamp": result.metadata.get("generation_timestamp"),
                    "geographic_focus": result.metadata.get("geographic_focus", []),
                    "key_findings_count": len(result.metadata.get("key_findings", [])),
                    "score": result.score
                })
        
        return ETLResponse(
            success=True,
            message=f"Found {len(reports)} recent AI enrichment reports",
            data={"reports": reports}
        )
        
    except Exception as e:
        logger.error(f"Error getting AI enrichment results: {e}")
        return ETLResponse(
            success=False,
            message=f"Error retrieving AI enrichment results: {str(e)}"
        )

# Background task functions
async def run_news_pipeline():
    """Background task for news monitoring with comprehensive metrics"""
    start_time = time.time()
    try:
        logger.info("Starting news pipeline...")
        
        # Monitor RSS feeds (FREE operation)
        articles = await monitor_rss_feeds(hours_back=24)
        
        logger.info(f"News pipeline found {len(articles)} articles")
        
        # Track metrics
        duplicates_removed = 0
        items_processed = 0
        items_failed = 0
        
        # Store results in vector database for semantic search
        if articles:
            vector_service = await get_vector_service()
            
            # Create documents for vector storage
            from services.vector_service import VectorDocument
            
            for i, article in enumerate(articles[:5]):  # Limit to 5 for demo
                try:
                    doc = VectorDocument(
                        id=f"news_{uuid4()}",
                        content=f"{article.title} {article.content or ''}",
                        metadata={
                            "content_type": "news_article",
                            "title": article.title,
                            "source": article.source,
                            "url": str(article.url),
                            "published_date": article.published_date.isoformat() if article.published_date else None,
                            "ai_relevance_score": article.ai_relevance_score,
                            "african_relevance_score": article.african_relevance_score
                        }
                    )
                    
                    # Add to vector database
                    await vector_service.upsert_documents([doc])
                    items_processed += 1
                except Exception as doc_error:
                    logger.warning(f"Failed to process article {i}: {doc_error}")
                    items_failed += 1
        
        # Calculate metrics
        runtime = time.time() - start_time
        metrics = ETLMetrics(
            batch_size=len(articles),
            duplicates_removed=duplicates_removed,
            processing_time_ms=int(runtime * 1000),
            success_rate=100.0 if items_failed == 0 else (items_processed / (items_processed + items_failed)) * 100,
            items_processed=items_processed,
            items_failed=items_failed
        )
        
        # Complete job with metrics
        etl_monitor.complete_job("news_pipeline", True, runtime, items_processed, metrics=metrics)
        
        logger.info("News pipeline completed successfully")
        
    except Exception as e:
        runtime = time.time() - start_time
        logger.error(f"News pipeline error: {e}")
        etl_monitor.complete_job("news_pipeline", False, runtime, 0, str(e))

async def run_academic_pipeline(days_back: int = 3, max_results: int = 10):
    """Background task for academic paper scraping with comprehensive metrics"""
    start_time = time.time()
    try:
        logger.info(f"Starting academic pipeline (days_back={days_back}, max_results={max_results})")
        
        # Scrape ArXiv papers (FREE operation)
        papers = await scrape_arxiv_papers(days_back=days_back, max_results=max_results)
        
        logger.info(f"Academic pipeline found {len(papers)} papers")
        
        # Track metrics
        duplicates_removed = 0
        items_processed = 0
        items_failed = 0
        
        # Store in database
        if papers:
            supabase = get_supabase()
            for paper in papers:
                try:
                    paper_data = {
                        "id": str(uuid4()),
                        "title": paper.title,
                        "abstract": paper.abstract,
                        "authors": paper.authors,
                        "publication_date": paper.published_date.date().isoformat(),
                        "updated_date": paper.updated_date.date().isoformat() if paper.updated_date else None,
                        "url": paper.url,
                        "source": "arxiv",
                        "source_id": paper.arxiv_id,
                        "keywords": paper.keywords,
                        "african_relevance_score": paper.african_relevance_score,
                        "ai_relevance_score": 0.8,  # Assume high AI relevance for ArXiv AI papers
                        "verification_status": "pending"
                    }
                    
                    supabase.table('publications').insert(paper_data).execute()
                    items_processed += 1
                except Exception as insert_error:
                    logger.warning(f"Error inserting paper {paper.title}: {insert_error}")
                    items_failed += 1
        
        # Calculate metrics
        runtime = time.time() - start_time
        metrics = ETLMetrics(
            batch_size=len(papers),
            duplicates_removed=duplicates_removed,
            processing_time_ms=int(runtime * 1000),
            success_rate=100.0 if items_failed == 0 else (items_processed / (items_processed + items_failed)) * 100,
            items_processed=items_processed,
            items_failed=items_failed
        )
        
        # Complete job with metrics
        etl_monitor.complete_job("academic_pipeline", True, runtime, items_processed, metrics=metrics)
        
        logger.info("Academic pipeline completed successfully")
        
    except Exception as e:
        runtime = time.time() - start_time
        logger.error(f"Academic pipeline error: {e}")
        etl_monitor.complete_job("academic_pipeline", False, runtime, 0, str(e))

async def run_discovery_pipeline(query: str):
    """Background task for innovation discovery with comprehensive metrics"""
    start_time = time.time()
    try:
        logger.info(f"Starting discovery pipeline with query: {query}")
        
        # Perform vector search
        vector_service = await get_vector_service()
        results = await vector_service.search_similar(query, top_k=10)
        
        logger.info(f"Discovery pipeline found {len(results)} results")
        
        # Calculate metrics
        runtime = time.time() - start_time
        metrics = ETLMetrics(
            batch_size=10,  # top_k parameter
            duplicates_removed=0,  # Vector search handles deduplication
            processing_time_ms=int(runtime * 1000),
            success_rate=100.0,  # Vector search typically succeeds
            items_processed=len(results),
            items_failed=0
        )
        
        # Complete job with metrics
        etl_monitor.complete_job("serper_pipeline", True, runtime, len(results), metrics=metrics)
        
        logger.info("Discovery pipeline completed successfully")
        
    except Exception as e:
        runtime = time.time() - start_time
        logger.error(f"Discovery pipeline error: {e}")
        etl_monitor.complete_job("serper_pipeline", False, runtime, 0, str(e))

async def run_enrichment_pipeline(
    intelligence_types: List[IntelligenceType],
    time_period: str = "last_7_days",
    geographic_focus: List[str] = None,
    provider: str = "perplexity"
):
    """Background task for AI intelligence enrichment with comprehensive metrics"""
    start_time = time.time()
    try:
        logger.info(f"Starting AI enrichment pipeline with {provider} using {len(intelligence_types)} intelligence types")
        
        # Route to appropriate provider
        if provider == "perplexity":
            reports_count = await run_perplexity_enrichment(intelligence_types, time_period, geographic_focus)
            
            # Calculate metrics
            runtime = time.time() - start_time
            metrics = ETLMetrics(
                batch_size=len(intelligence_types),
                duplicates_removed=0,
                processing_time_ms=int(runtime * 1000),
                success_rate=100.0,
                items_processed=reports_count,
                items_failed=0
            )
            
            # Complete job with metrics
            etl_monitor.complete_job("enrichment_pipeline", True, runtime, reports_count, metrics=metrics)
            logger.info("AI enrichment pipeline completed successfully")
        else:
            logger.error(f"Unsupported enrichment provider: {provider}")
            etl_monitor.complete_job("enrichment_pipeline", False, 0, 0, f"Unsupported provider: {provider}")
        
    except Exception as e:
        runtime = time.time() - start_time
        logger.error(f"Enrichment pipeline error: {e}")
        etl_monitor.complete_job("enrichment_pipeline", False, runtime, 0, str(e))

async def run_perplexity_enrichment(
    intelligence_types: List[IntelligenceType],
    time_period: str = "last_7_days",
    geographic_focus: List[str] = None
) -> int:
    """Run Perplexity-specific enrichment and return number of reports generated"""
    # Get Perplexity API key from environment
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        logger.error("PERPLEXITY_API_KEY not found in environment variables")
        raise Exception("PERPLEXITY_API_KEY not configured")
    
    # Run Perplexity intelligence synthesis
    async with PerplexityAfricanAIModule(api_key) as perplexity_module:
            reports = await perplexity_module.synthesize_intelligence(
                intelligence_types=intelligence_types,
                time_period=time_period,
                geographic_focus=geographic_focus
        )
        
    logger.info(f"Perplexity enrichment generated {len(reports)} intelligence reports")
        
    # Store reports in vector database for semantic search
    if reports:
        vector_service = await get_vector_service()
            
        # Create documents for vector storage
        from services.vector_service import VectorDocument
            
        for report in reports:
        # Create a comprehensive content string for embedding
            content = f"{report.title}\n\n{report.summary}\n\nKey Findings:\n"
            content += "\n".join([f"- {finding}" for finding in report.key_findings])
                
        doc = VectorDocument(
            id=f"enrichment_{report.report_id}",
            content=content,
            metadata={
                "content_type": "enrichment_report",
                "provider": "perplexity",
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
                
        # Add to vector database
        await vector_service.upsert_documents([doc])
            
        # Also store structured data in Supabase for detailed access
        supabase = get_supabase()
        for report in reports:
                try:
                    report_data = {
                        "id": report.report_id,
                        "title": report.title,
                        "provider": "perplexity",
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
                    
                    # Store in intelligence_reports table (create if needed)
                    supabase.table('intelligence_reports').insert(report_data).execute()
                    
                except Exception as db_error:
                    logger.warning(f"Could not store report {report.report_id} in database: {db_error}")
                    # Continue with other reports even if one fails
        
        logger.info("Perplexity enrichment completed successfully")
    
    return len(reports) if reports else 0


# Enrichment Scheduler Endpoints

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get enrichment scheduler status"""
    try:
        scheduler = get_enrichment_scheduler()
        schedule_info = scheduler.get_schedule_info()
        
        return ETLResponse(
            success=True,
            message="Scheduler status retrieved successfully",
            data=schedule_info
        )
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        return ETLResponse(
            success=False,
            message=f"Error retrieving scheduler status: {str(e)}"
        )

@router.post("/scheduler/configure")
async def configure_scheduler(
    interval_hours: int = 6,
    enabled: bool = True,
    intelligence_types: List[str] = ["innovation_discovery", "funding_landscape"],
    provider: str = "perplexity",
    geographic_focus: List[str] = None
):
    """Configure enrichment scheduler settings"""
    try:
        scheduler = get_enrichment_scheduler()
        
        scheduler.update_schedule(
            interval_hours=interval_hours,
            enabled=enabled,
            intelligence_types=intelligence_types,
            provider=provider,
            geographic_focus=geographic_focus
        )
        
        return ETLResponse(
            success=True,
            message=f"Scheduler configured: {interval_hours}h intervals, enabled={enabled}",
            data={
                "interval_hours": interval_hours,
                "enabled": enabled,
                "provider": provider,
                "intelligence_types": intelligence_types,
                "geographic_focus": geographic_focus or ["Nigeria", "Kenya", "South Africa", "Ghana", "Egypt"]
            }
        )
    except Exception as e:
        logger.error(f"Error configuring scheduler: {e}")
        return ETLResponse(
            success=False,
            message=f"Error configuring scheduler: {str(e)}"
        )

@router.post("/scheduler/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Start the enrichment scheduler"""
    try:
        scheduler = get_enrichment_scheduler()
        
        # Start scheduler in background
        background_tasks.add_task(scheduler.start_scheduler)
        
        return ETLResponse(
            success=True,
            message="Enrichment scheduler started successfully",
            data={"status": "starting"}
        )
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        return ETLResponse(
            success=False,
            message=f"Error starting scheduler: {str(e)}"
        )

@router.post("/scheduler/stop")
async def stop_scheduler(background_tasks: BackgroundTasks):
    """Stop the enrichment scheduler"""
    try:
        scheduler = get_enrichment_scheduler()
        
        # Stop scheduler in background
        background_tasks.add_task(scheduler.stop_scheduler)
        
        return ETLResponse(
            success=True,
            message="Enrichment scheduler stopped successfully",
            data={"status": "stopping"}
        )
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        return ETLResponse(
            success=False,
            message=f"Error stopping scheduler: {str(e)}"
        )
