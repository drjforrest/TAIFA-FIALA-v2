"""
TAIFA-FIALA FastAPI Main Application
Innovation archive and data pipeline API
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session
from loguru import logger

from config.settings import settings
from config.database import get_db, get_supabase
from models.database import *
from models.schemas import *
from services.vector_service import get_vector_service, VectorService
from services.serper_service import search_african_innovations, search_funding_news
from services.crawl4ai_service import crawl_innovation_websites
from etl.academic.arxiv_scraper import scrape_arxiv_papers
from etl.news.rss_monitor import monitor_rss_feeds


# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for TAIFA-FIALA African AI Innovation Archive",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting TAIFA-FIALA API...")
    
    # Initialize vector service
    try:
        vector_service = await get_vector_service()
        logger.info("Vector service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize vector service: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down TAIFA-FIALA API...")


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": settings.APP_VERSION
    }


# Innovation Endpoints
@app.get("/api/innovations", response_model=InnovationSearchResponse)
@limiter.limit("30/minute")
async def get_innovations(
    request,
    params: InnovationSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """Get innovations with search and filtering"""
    try:
        query = db.query(Innovation)
        
        # Apply filters
        if params.innovation_type:
            query = query.filter(Innovation.innovation_type == params.innovation_type)
        
        if params.verification_status:
            query = query.filter(Innovation.verification_status == params.verification_status)
        
        if params.min_funding or params.max_funding:
            query = query.join(Funding)
            if params.min_funding:
                query = query.filter(Funding.amount >= params.min_funding)
            if params.max_funding:
                query = query.filter(Funding.amount <= params.max_funding)
        
        if params.date_from:
            query = query.filter(Innovation.created_at >= params.date_from)
        
        if params.date_to:
            query = query.filter(Innovation.created_at <= params.date_to)
        
        # Count total results
        total = query.count()
        
        # Apply sorting
        if params.sort_by == "title":
            query = query.order_by(Innovation.title.desc() if params.sort_order == "desc" else Innovation.title)
        elif params.sort_by == "updated_at":
            query = query.order_by(Innovation.updated_at.desc() if params.sort_order == "desc" else Innovation.updated_at)
        else:  # default: created_at
            query = query.order_by(Innovation.created_at.desc() if params.sort_order == "desc" else Innovation.created_at)
        
        # Apply pagination
        innovations = query.offset(params.offset).limit(params.limit).all()
        
        return InnovationSearchResponse(
            innovations=[InnovationResponse.from_orm(inn) for inn in innovations],
            total=total,
            limit=params.limit,
            offset=params.offset,
            has_more=params.offset + params.limit < total
        )
        
    except Exception as e:
        logger.error(f"Error getting innovations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/innovations/{innovation_id}", response_model=InnovationResponse)
@limiter.limit("60/minute")
async def get_innovation(request, innovation_id: UUID, db: Session = Depends(get_db)):
    """Get single innovation by ID"""
    innovation = db.query(Innovation).filter(Innovation.id == innovation_id).first()
    
    if not innovation:
        raise HTTPException(status_code=404, detail="Innovation not found")
    
    return InnovationResponse.from_orm(innovation)


@app.post("/api/innovations", response_model=InnovationResponse)
@limiter.limit("10/minute")
async def create_innovation(
    request,
    innovation_data: InnovationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create new innovation"""
    try:
        # Create innovation
        innovation = Innovation(
            title=innovation_data.title,
            description=innovation_data.description,
            innovation_type=innovation_data.innovation_type,
            creation_date=innovation_data.creation_date,
            problem_solved=innovation_data.problem_solved,
            solution_approach=innovation_data.solution_approach,
            impact_metrics=innovation_data.impact_metrics,
            tech_stack=innovation_data.tech_stack,
            tags=innovation_data.tags,
            website_url=str(innovation_data.website_url) if innovation_data.website_url else None,
            github_url=str(innovation_data.github_url) if innovation_data.github_url else None,
            demo_url=str(innovation_data.demo_url) if innovation_data.demo_url else None,
            source_type="manual",
            verification_status="pending"
        )
        
        db.add(innovation)
        db.commit()
        db.refresh(innovation)
        
        # Create community submission record
        submission = CommunitySubmission(
            innovation_id=innovation.id,
            submitter_name=innovation_data.submitter_name,
            submitter_email=innovation_data.submitter_email,
            submission_status="pending"
        )
        
        db.add(submission)
        db.commit()
        
        # Add to vector database in background
        background_tasks.add_task(
            add_innovation_to_vector_db,
            innovation.id,
            innovation.title,
            innovation.description,
            innovation.innovation_type,
            innovation_data.country
        )
        
        logger.info(f"Created innovation: {innovation.title}")
        return InnovationResponse.from_orm(innovation)
        
    except Exception as e:
        logger.error(f"Error creating innovation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create innovation")


# Search Endpoints
@app.get("/api/search", response_model=InnovationSearchResponse)
@limiter.limit("20/minute")
async def search_innovations(
    request,
    query: str = Query(..., min_length=3, description="Search query"),
    innovation_type: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    vector_service: VectorService = Depends(get_vector_service)
):
    """Search innovations using vector similarity"""
    try:
        # Perform vector search
        vector_results = await vector_service.search_innovations(
            query=query,
            innovation_type=innovation_type,
            country=country,
            top_k=limit
        )
        
        # Convert to response format
        innovations = []
        for result in vector_results:
            # This would need to fetch full innovation data from DB
            # For now, return basic info from metadata
            innovation_data = {
                "id": result.metadata.get("innovation_id"),
                "title": result.metadata.get("title", ""),
                "description": result.content,
                "innovation_type": result.metadata.get("innovation_type"),
                "verification_status": "verified",  # placeholder
                "visibility": "public",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "organizations": [],
                "individuals": [],
                "publications": [],
                "fundings": []
            }
            innovations.append(innovation_data)
        
        return InnovationSearchResponse(
            innovations=innovations,
            total=len(innovations),
            limit=limit,
            offset=0,
            has_more=False
        )
        
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


# ETL Endpoints
@app.post("/api/etl/academic")
@limiter.limit("5/minute")
async def trigger_academic_etl(
    request,
    background_tasks: BackgroundTasks,
    days_back: int = Query(7, ge=1, le=30),
    max_results: int = Query(100, ge=10, le=500)
):
    """Trigger academic paper scraping"""
    job_id = str(uuid4())
    
    background_tasks.add_task(
        run_academic_etl,
        job_id,
        days_back,
        max_results
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Academic ETL job started for last {days_back} days"
    }


@app.post("/api/etl/news")
@limiter.limit("5/minute")
async def trigger_news_etl(
    request,
    background_tasks: BackgroundTasks,
    hours_back: int = Query(24, ge=1, le=168)  # Max 1 week
):
    """Trigger news monitoring"""
    job_id = str(uuid4())
    
    background_tasks.add_task(
        run_news_etl,
        job_id,
        hours_back
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"News ETL job started for last {hours_back} hours"
    }


@app.post("/api/etl/serper-search")
@limiter.limit("3/minute")
async def trigger_serper_search(
    request,
    background_tasks: BackgroundTasks,
    innovation_type: Optional[str] = None,
    country: Optional[str] = None,
    num_results: int = Query(50, ge=10, le=100)
):
    """Trigger Serper.dev innovation search"""
    job_id = str(uuid4())
    
    background_tasks.add_task(
        run_serper_search,
        job_id,
        innovation_type,
        country,
        num_results
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Serper search job started"
    }


# Community Endpoints
@app.get("/api/community/submissions", response_model=List[CommunitySubmissionResponse])
@limiter.limit("20/minute")
async def get_community_submissions(
    request,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get community submissions for verification"""
    query = db.query(CommunitySubmission)
    
    if status:
        query = query.filter(CommunitySubmission.submission_status == status)
    
    submissions = query.limit(limit).all()
    
    return [CommunitySubmissionResponse.from_orm(sub) for sub in submissions]


@app.post("/api/community/vote")
@limiter.limit("50/minute")
async def submit_community_vote(
    request,
    vote: CommunityVote,
    db: Session = Depends(get_db)
):
    """Submit community vote for innovation verification"""
    # Implementation would update community_votes in submission
    # This is a simplified version
    return {"status": "vote_recorded", "message": "Thank you for your vote"}


# Statistics Endpoints
@app.get("/api/stats", response_model=InnovationStats)
@limiter.limit("10/minute")
async def get_statistics(request, db: Session = Depends(get_db)):
    """Get platform statistics"""
    try:
        total_innovations = db.query(Innovation).count()
        verified_innovations = db.query(Innovation).filter(
            Innovation.verification_status == "verified"
        ).count()
        pending_innovations = db.query(Innovation).filter(
            Innovation.verification_status == "pending"
        ).count()
        
        # Additional stats would be calculated here
        
        return InnovationStats(
            total_innovations=total_innovations,
            verified_innovations=verified_innovations,
            pending_innovations=pending_innovations,
            innovations_by_type={},  # Would be calculated
            innovations_by_country={},  # Would be calculated
            innovations_by_month={}  # Would be calculated
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# Background Task Functions
async def add_innovation_to_vector_db(innovation_id: UUID, title: str, description: str, 
                                    innovation_type: str, country: str):
    """Add innovation to vector database"""
    try:
        vector_service = await get_vector_service()
        success = await vector_service.add_innovation(
            innovation_id=innovation_id,
            title=title,
            description=description,
            innovation_type=innovation_type,
            country=country
        )
        
        if success:
            logger.info(f"Added innovation {innovation_id} to vector database")
        else:
            logger.error(f"Failed to add innovation {innovation_id} to vector database")
            
    except Exception as e:
        logger.error(f"Error adding innovation to vector DB: {e}")


async def run_academic_etl(job_id: str, days_back: int, max_results: int):
    """Run academic ETL job"""
    try:
        logger.info(f"Starting academic ETL job {job_id}")
        
        papers = await scrape_arxiv_papers(days_back, max_results)
        
        # Process and store papers (implementation would be more complex)
        logger.info(f"Academic ETL job {job_id} completed: {len(papers)} papers processed")
        
    except Exception as e:
        logger.error(f"Academic ETL job {job_id} failed: {e}")


async def run_news_etl(job_id: str, hours_back: int):
    """Run news ETL job"""
    try:
        logger.info(f"Starting news ETL job {job_id}")
        
        articles = await monitor_rss_feeds(hours_back)
        
        # Process and store articles (implementation would be more complex)
        logger.info(f"News ETL job {job_id} completed: {len(articles)} articles processed")
        
    except Exception as e:
        logger.error(f"News ETL job {job_id} failed: {e}")


async def run_serper_search(job_id: str, innovation_type: Optional[str], 
                          country: Optional[str], num_results: int):
    """Run Serper search job"""
    try:
        logger.info(f"Starting Serper search job {job_id}")
        
        results = await search_african_innovations(innovation_type, country, num_results)
        
        # Process and store results (implementation would be more complex)
        logger.info(f"Serper search job {job_id} completed: {len(results)} results processed")
        
    except Exception as e:
        logger.error(f"Serper search job {job_id} failed: {e}")


# ETL Monitoring Endpoints
@app.get("/api/etl/status")
@limiter.limit("30/minute")
async def get_etl_status(request):
    """Get comprehensive ETL system status"""
    try:
        from services.etl_monitor import etl_monitor
        dashboard_data = await etl_monitor.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting ETL status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ETL status")


@app.get("/api/etl/health")
@limiter.limit("60/minute")
async def get_etl_health(request):
    """Get ETL system health check"""
    try:
        from services.etl_monitor import etl_monitor
        health = await etl_monitor.get_system_health()
        return {
            "status": "healthy" if health.database_status == "healthy" else "unhealthy",
            "system_health": {
                "cpu_percent": health.cpu_percent,
                "memory_percent": health.memory_percent,
                "disk_usage": health.disk_usage,
                "database_status": health.database_status,
                "vector_db_status": health.vector_db_status
            },
            "timestamp": health.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ETL health: {e}")
        raise HTTPException(status_code=500, detail="ETL health check failed")


@app.get("/api/etl/jobs")
@limiter.limit("30/minute")
async def get_etl_jobs(request, active_only: bool = False):
    """Get ETL job statuses"""
    try:
        from services.etl_monitor import etl_monitor
        dashboard_data = await etl_monitor.get_dashboard_data()
        
        jobs = dashboard_data['job_statuses']
        if active_only:
            jobs = [job for job in jobs if job['is_running'] or job['health_status'] in ['healthy', 'failing']]
        
        return {
            "jobs": jobs,
            "summary": dashboard_data['job_summary'],
            "timestamp": dashboard_data['timestamp']
        }
    except Exception as e:
        logger.error(f"Error getting ETL jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ETL jobs")


@app.get("/api/etl/recent")
@limiter.limit("30/minute")
async def get_recent_etl_activity(request, hours: int = Query(24, ge=1, le=168)):
    """Get recent ETL activity"""
    try:
        from services.etl_monitor import etl_monitor
        activity = etl_monitor.get_recent_activity(hours)
        return {
            "activity": activity,
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent ETL activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ETL activity")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )