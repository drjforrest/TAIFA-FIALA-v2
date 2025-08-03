"""
Live ETL API Endpoints for TAIFA-FIALA Dashboard
Real-time pipeline triggers for interactive dashboard
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from etl.news.rss_monitor import monitor_rss_feeds
from etl.academic.arxiv_scraper import scrape_arxiv_papers
from services.vector_service import get_vector_service
from config.database import get_supabase

router = APIRouter(prefix="/api/etl", tags=["ETL Live"])

class ETLResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class ETLStatus(BaseModel):
    pipeline: str
    status: str
    last_run: Optional[datetime] = None
    items_processed: int = 0
    errors: int = 0

# In-memory tracking for demo purposes
etl_status = {
    "news_pipeline": ETLStatus(pipeline="news", status="idle"),
    "academic_pipeline": ETLStatus(pipeline="academic", status="idle"),
    "discovery_pipeline": ETLStatus(pipeline="discovery", status="idle")
}

@router.get("/status")
async def get_etl_status():
    """Get current ETL pipeline status"""
    return {
        "success": True,
        "data": {
            "pipelines": etl_status,
            "system_health": "healthy",
            "last_updated": datetime.now().isoformat()
        }
    }

@router.post("/trigger/news")
async def trigger_news_pipeline(background_tasks: BackgroundTasks):
    """Trigger RSS news monitoring pipeline - FREE operation"""
    
    if etl_status["news_pipeline"].status == "running":
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
    
    if etl_status["academic_pipeline"].status == "running":
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
    
    if etl_status["discovery_pipeline"].status == "running":
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

# Background task functions
async def run_news_pipeline():
    """Background task for news monitoring"""
    try:
        etl_status["news_pipeline"].status = "running"
        etl_status["news_pipeline"].last_run = datetime.now()
        
        logger.info("Starting news pipeline...")
        
        # Monitor RSS feeds (FREE operation)
        articles = await monitor_rss_feeds(hours_back=24)
        
        logger.info(f"News pipeline found {len(articles)} articles")
        
        # Store results in vector database for semantic search
        if articles:
            vector_service = await get_vector_service()
            
            # Create documents for vector storage
            from services.vector_service import VectorDocument
            
            for i, article in enumerate(articles[:5]):  # Limit to 5 for demo
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
        
        etl_status["news_pipeline"].status = "completed"
        etl_status["news_pipeline"].items_processed = len(articles)
        
        logger.info("News pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"News pipeline error: {e}")
        etl_status["news_pipeline"].status = "error"
        etl_status["news_pipeline"].errors += 1

async def run_academic_pipeline(days_back: int = 3, max_results: int = 10):
    """Background task for academic paper scraping"""
    try:
        etl_status["academic_pipeline"].status = "running"
        etl_status["academic_pipeline"].last_run = datetime.now()
        
        logger.info(f"Starting academic pipeline (days_back={days_back}, max_results={max_results})")
        
        # Scrape ArXiv papers (FREE operation)
        papers = await scrape_arxiv_papers(days_back=days_back, max_results=max_results)
        
        logger.info(f"Academic pipeline found {len(papers)} papers")
        
        # Store in database
        if papers:
            supabase = get_supabase()
            for paper in papers:
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
                
                try:
                    supabase.table('publications').insert(paper_data).execute()
                except Exception as insert_error:
                    logger.warning(f"Error inserting paper {paper.title}: {insert_error}")
        
        etl_status["academic_pipeline"].status = "completed"
        etl_status["academic_pipeline"].items_processed = len(papers)
        
        logger.info("Academic pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Academic pipeline error: {e}")
        etl_status["academic_pipeline"].status = "error"
        etl_status["academic_pipeline"].errors += 1

async def run_discovery_pipeline(query: str):
    """Background task for innovation discovery"""
    try:
        etl_status["discovery_pipeline"].status = "running"
        etl_status["discovery_pipeline"].last_run = datetime.now()
        
        logger.info(f"Starting discovery pipeline with query: {query}")
        
        # Perform vector search
        vector_service = await get_vector_service()
        results = await vector_service.search_similar(query, top_k=10)
        
        logger.info(f"Discovery pipeline found {len(results)} results")
        
        etl_status["discovery_pipeline"].status = "completed"
        etl_status["discovery_pipeline"].items_processed = len(results)
        
        logger.info("Discovery pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Discovery pipeline error: {e}")
        etl_status["discovery_pipeline"].status = "error"
        etl_status["discovery_pipeline"].errors += 1
