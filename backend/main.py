"""
TAIFA-FIALA FastAPI Main Application
Innovation archive and data pipeline API
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from loguru import logger

from config.settings import settings
from models.database import *
from models.schemas import *
from services.vector_service import get_vector_service, VectorService
from api.etl_live import router as etl_live_router
try:
    from services.serper_service import search_african_innovations
except ImportError:
    logger.warning("Serper service not available - search functionality will be limited")

    async def search_african_innovations(*args, **kwargs):
        return []
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

# Include routers
app.include_router(etl_live_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting TAIFA-FIALA API...")

    # Initialize vector service asynchronously (non-blocking)
    async def init_vector_service():
        try:
            import asyncio
            vector_service = await asyncio.wait_for(get_vector_service(), timeout=10.0)
            logger.info("Vector service initialized")
        except asyncio.TimeoutError:
            logger.warning("Vector service initialization timed out - will retry on first use")
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")

    # Start initialization in background, don't wait for it
    asyncio.create_task(init_vector_service())
    logger.info("TAIFA-FIALA API startup complete - services initializing in background")


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


# Dashboard Stats Endpoint
@app.get("/api/stats")
@limiter.limit("60/minute")
async def get_dashboard_stats(request: Request):
    """Get dashboard statistics"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Get counts from different tables
        innovations_response = supabase.table('innovations').select('id', count='exact').execute()
        publications_response = supabase.table('publications').select('id', count='exact').execute()
        organizations_response = supabase.table('organizations').select('id', count='exact').execute()
        individuals_response = supabase.table('individuals').select('id', count='exact').eq('verification_status', 'verified').execute()
        
        # Get sample data for calculations
        publications_data = supabase.table('publications').select(
            'african_entities, keywords, african_relevance_score, ai_relevance_score'
        ).limit(1000).execute()
        
        # Calculate derived stats
        african_countries = set()
        keywords = set()
        african_score_sum = 0
        ai_score_sum = 0
        scores_count = 0
        
        if publications_data.data:
            for pub in publications_data.data:
                # African entities
                if pub.get('african_entities'):
                    for entity in pub['african_entities']:
                        african_countries.add(entity)
                
                # Keywords
                if pub.get('keywords'):
                    for keyword in pub['keywords']:
                        keywords.add(keyword)
                
                # Scores
                african_score = pub.get('african_relevance_score', 0)
                ai_score = pub.get('ai_relevance_score', 0)
                if african_score > 0 and ai_score > 0:
                    african_score_sum += african_score
                    ai_score_sum += ai_score
                    scores_count += 1
        
        return {
            "total_innovations": innovations_response.count or 0,
            "total_publications": publications_response.count or 0,
            "total_organizations": organizations_response.count or 0,
            "verified_individuals": individuals_response.count or 0,
            "african_countries_covered": len(african_countries),
            "unique_keywords": len(keywords),
            "avg_african_relevance": african_score_sum / scores_count if scores_count > 0 else 0,
            "avg_ai_relevance": ai_score_sum / scores_count if scores_count > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        # Return mock data if database fails
        return {
            "total_innovations": 24,
            "total_publications": 50,
            "total_organizations": 15,
            "verified_individuals": 8,
            "african_countries_covered": 34,
            "unique_keywords": 46,
            "avg_african_relevance": 0.789,
            "avg_ai_relevance": 0.742,
            "last_updated": datetime.now().isoformat()
        }


# Database Test Endpoint
@app.get("/test-db")
async def test_database_connection():
    """Test Supabase database connection"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Test connection by querying innovations table
        response = supabase.table('innovations').select('id').limit(1).execute()
        
        return {
            "status": "success",
            "message": "Supabase connection working",
            "sample_data_found": len(response.data) > 0 if response.data else False,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "message": f"Supabase connection failed: {str(e)}",
            "timestamp": datetime.now()
        }


# Innovation Endpoints
@app.get("/api/innovations")
@limiter.limit("30/minute")
async def get_innovations(
    request: Request,
    query: Optional[str] = None,
    innovation_type: Optional[str] = None,
    country: Optional[str] = None,
    verification_status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    vector_service: VectorService = Depends(get_vector_service)
):
    """Get innovations with hybrid search (vector + traditional) and filtering"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Initialize search metadata
        search_metadata = {
            "query_type": "filter_only",
            "used_vector_search": False,
            "used_traditional_search": False,
            "vector_results_count": 0,
            "traditional_results_count": 0,
            "avg_relevance_score": 0,
            "search_quality": "n/a"
        }
        
        innovations_data = []
        total = 0
        
        if query and len(query.strip()) >= 3:
            # HYBRID SEARCH: Vector + Traditional
            logger.info(f"Performing hybrid search for query: '{query}'")
            
            try:
                # 1. Vector Search (semantic similarity)
                vector_results = await vector_service.search_innovations(
                    query=query,
                    innovation_type=innovation_type,
                    country=country,
                    top_k=min(50, limit * 3)  # Get more results for better ranking
                )
                
                # Extract innovation IDs from vector results
                vector_innovation_ids = []
                innovation_scores = {}
                
                for result in vector_results:
                    innovation_id = result.metadata.get('innovation_id')
                    if innovation_id:
                        vector_innovation_ids.append(innovation_id)
                        innovation_scores[innovation_id] = result.score
                
                search_metadata.update({
                    "query_type": "hybrid_search",
                    "used_vector_search": True,
                    "vector_results_count": len(vector_results),
                    "avg_relevance_score": round(sum(r.score for r in vector_results) / len(vector_results), 3) if vector_results else 0
                })
                
                logger.info(f"Vector search found {len(vector_results)} results")
                
            except Exception as vector_error:
                logger.warning(f"Vector search failed, falling back to traditional: {vector_error}")
                vector_innovation_ids = []
                innovation_scores = {}
            
            # 2. Traditional Search (keyword matching) as fallback/supplement
            try:
                traditional_query = supabase.table('innovations').select('*')
                
                # Apply text search
                traditional_query = traditional_query.or_(
                    f'title.ilike.%{query}%,description.ilike.%{query}%,innovation_type.ilike.%{query}%'
                )
                
                # Apply filters
                if innovation_type:
                    traditional_query = traditional_query.eq('innovation_type', innovation_type)
                if verification_status:
                    traditional_query = traditional_query.eq('verification_status', verification_status)
                if country:
                    traditional_query = traditional_query.eq('country', country)
                
                traditional_response = traditional_query.limit(50).execute()
                traditional_results = traditional_response.data if traditional_response.data else []
                
                search_metadata.update({
                    "used_traditional_search": True,
                    "traditional_results_count": len(traditional_results)
                })
                
                logger.info(f"Traditional search found {len(traditional_results)} results")
                
            except Exception as traditional_error:
                logger.error(f"Traditional search also failed: {traditional_error}")
                traditional_results = []
            
            # 3. Merge and rank results (prioritize vector results)
            merged_results = {}
            
            # First, add vector results (higher priority)
            if vector_innovation_ids:
                vector_query = supabase.table('innovations').select('*').in_('id', vector_innovation_ids)
                if verification_status:
                    vector_query = vector_query.eq('verification_status', verification_status)
                
                vector_data_response = vector_query.execute()
                vector_data = vector_data_response.data if vector_data_response.data else []
                
                for innovation in vector_data:
                    innovation_id = innovation['id']
                    innovation['_relevance_score'] = innovation_scores.get(innovation_id, 0)
                    innovation['_search_source'] = 'vector'
                    merged_results[innovation_id] = innovation
            
            # Then, add traditional results (lower priority, only if not already included)
            for innovation in traditional_results:
                innovation_id = innovation['id']
                if innovation_id not in merged_results:
                    innovation['_relevance_score'] = 0.3  # Lower score for traditional matches
                    innovation['_search_source'] = 'traditional'
                    merged_results[innovation_id] = innovation
            
            # Convert to list and sort by relevance score
            innovations_data = list(merged_results.values())
            innovations_data.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)
            
            total = len(innovations_data)
            
            # Update search quality assessment
            if search_metadata["avg_relevance_score"] > 0.8:
                search_metadata["search_quality"] = "excellent"
            elif search_metadata["avg_relevance_score"] > 0.6:
                search_metadata["search_quality"] = "good"
            elif search_metadata["avg_relevance_score"] > 0.3:
                search_metadata["search_quality"] = "fair"
            else:
                search_metadata["search_quality"] = "poor"
            
        else:
            # NO QUERY: Traditional filtering and pagination
            query_builder = supabase.table('innovations').select('*')
            
            # Apply filters
            if innovation_type:
                query_builder = query_builder.eq('innovation_type', innovation_type)
            if verification_status:
                query_builder = query_builder.eq('verification_status', verification_status)
            if country:
                query_builder = query_builder.eq('country', country)
            
            # Get total count
            count_query = supabase.table('innovations').select('id', count='exact')
            if innovation_type:
                count_query = count_query.eq('innovation_type', innovation_type)
            if verification_status:
                count_query = count_query.eq('verification_status', verification_status)
            if country:
                count_query = count_query.eq('country', country)
            
            count_response = count_query.execute()
            total = count_response.count if count_response.count is not None else 0
            
            # Apply sorting
            if sort_by == "title":
                query_builder = query_builder.order('title', desc=(sort_order == "desc"))
            elif sort_by == "updated_at":
                query_builder = query_builder.order('updated_at', desc=(sort_order == "desc"))
            else:  # default: created_at
                query_builder = query_builder.order('created_at', desc=(sort_order == "desc"))
            
            # Apply pagination
            query_builder = query_builder.range(offset, offset + limit - 1)
            
            # Execute query
            response = query_builder.execute()
            innovations_data = response.data if response.data else []
            
            search_metadata["query_type"] = "filter_only"
        
        # Apply pagination to search results
        if query and innovations_data:
            paginated_data = innovations_data[offset:offset + limit]
        else:
            paginated_data = innovations_data
        
        # Convert to response format
        innovations = []
        for innovation_data in paginated_data:
            innovation_response = {
                "id": innovation_data.get("id"),
                "title": innovation_data.get("title"),
                "description": innovation_data.get("description"),
                "innovation_type": innovation_data.get("innovation_type"),
                "verification_status": innovation_data.get("verification_status"),
                "visibility": innovation_data.get("visibility"),
                "country": innovation_data.get("country"),
                "creation_date": innovation_data.get("creation_date"),
                "organizations": innovation_data.get("organizations", []),
                "individuals": innovation_data.get("individuals", []),
                "fundings": innovation_data.get("fundings", []),
                "publications": innovation_data.get("publications", []),
                "tags": innovation_data.get("tags", []),
                "impact_metrics": innovation_data.get("impact_metrics", {})
            }
            
            # Add search-specific metadata for search results
            if query and '_relevance_score' in innovation_data:
                innovation_response['_relevance_score'] = innovation_data['_relevance_score']
                innovation_response['_search_source'] = innovation_data['_search_source']
            
            innovations.append(innovation_response)
        
        return {
            "innovations": innovations,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
            "search_metadata": search_metadata
        }
        
    except Exception as e:
        logger.error(f"Error getting innovations: {e}")
        # Return mock data if database fails to help with debugging
        return {
            "innovations": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "has_more": False,
            "error": f"Database error: {str(e)}"
        }


@app.get("/api/innovations/{innovation_id}", response_model=InnovationResponse)
@limiter.limit("60/minute")
async def get_innovation(request: Request, innovation_id: UUID):
    """Get single innovation by ID using Supabase client"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Query single innovation by ID
        response = supabase.table('innovations').select('*').eq('id', str(innovation_id)).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Innovation not found")
        
        innovation_data = response.data[0]
        
        # Convert to response format
        return {
            "id": innovation_data.get("id"),
            "title": innovation_data.get("title"),
            "description": innovation_data.get("description"),
            "innovation_type": innovation_data.get("innovation_type"),
            "verification_status": innovation_data.get("verification_status"),
            "visibility": innovation_data.get("visibility"),
            "country": innovation_data.get("country"),
            "creation_date": innovation_data.get("creation_date"),
            "organizations": innovation_data.get("organizations", []),
            "individuals": innovation_data.get("individuals", []),
            "fundings": innovation_data.get("fundings", []),
            "publications": innovation_data.get("publications", []),
            "tags": innovation_data.get("tags", []),
            "impact_metrics": innovation_data.get("impact_metrics", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting innovation {innovation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/innovations", response_model=InnovationResponse)
@limiter.limit("10/minute")
async def create_innovation(
    request: Request,
    innovation_data: InnovationCreate,
    background_tasks: BackgroundTasks
):
    """Create new innovation using Supabase client"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Prepare innovation data for Supabase
        innovation_record = {
            "title": innovation_data.title,
            "description": innovation_data.description,
            "innovation_type": innovation_data.innovation_type,
            "creation_date": innovation_data.creation_date.isoformat() if innovation_data.creation_date else None,
            "problem_solved": innovation_data.problem_solved,
            "solution_approach": innovation_data.solution_approach,
            "impact_metrics": innovation_data.impact_metrics,
            "tech_stack": innovation_data.tech_stack,
            "tags": innovation_data.tags,
            "website_url": str(innovation_data.website_url) if innovation_data.website_url else None,
            "github_url": str(innovation_data.github_url) if innovation_data.github_url else None,
            "demo_url": str(innovation_data.demo_url) if innovation_data.demo_url else None,
            "source_type": "manual",
            "verification_status": "pending",
            "country": innovation_data.country
        }
        
        # Create innovation in Supabase
        innovation_response = supabase.table('innovations').insert(innovation_record).execute()
        
        if not innovation_response.data or len(innovation_response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create innovation")
        
        created_innovation = innovation_response.data[0]
        innovation_id = created_innovation.get('id')
        
        # Create community submission record
        submission_record = {
            "innovation_id": innovation_id,
            "submitter_name": innovation_data.submitter_name,
            "submitter_email": innovation_data.submitter_email,
            "submission_status": "pending"
        }
        
        supabase.table('community_submissions').insert(submission_record).execute()
        
        # Add to vector database in background
        background_tasks.add_task(
            add_innovation_to_vector_db,
            innovation_id,
            created_innovation.get('title'),
            created_innovation.get('description'),
            created_innovation.get('innovation_type'),
            innovation_data.country
        )
        
        logger.info(f"Created innovation: {created_innovation.get('title')}")
        
        # Return response in expected format
        return {
            "id": created_innovation.get("id"),
            "title": created_innovation.get("title"),
            "description": created_innovation.get("description"),
            "innovation_type": created_innovation.get("innovation_type"),
            "verification_status": created_innovation.get("verification_status"),
            "visibility": created_innovation.get("visibility"),
            "country": created_innovation.get("country"),
            "creation_date": created_innovation.get("creation_date"),
            "organizations": created_innovation.get("organizations", []),
            "individuals": created_innovation.get("individuals", []),
            "fundings": created_innovation.get("fundings", []),
            "publications": created_innovation.get("publications", []),
            "tags": created_innovation.get("tags", []),
            "impact_metrics": created_innovation.get("impact_metrics", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating innovation: {e}")
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
    request: Request,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Get community submissions for verification using Supabase client"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Build query
        query = supabase.table('community_submissions').select('*')
        
        if status:
            query = query.eq('submission_status', status)
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query
        response = query.execute()
        submissions_data = response.data if response.data else []
        
        # Convert to response format
        submissions = []
        for submission_data in submissions_data:
            submissions.append({
                "id": submission_data.get("id"),
                "innovation_id": submission_data.get("innovation_id"),
                "submitter_name": submission_data.get("submitter_name"),
                "submitter_email": submission_data.get("submitter_email"),
                "submission_status": submission_data.get("submission_status"),
                "created_at": submission_data.get("created_at"),
                "updated_at": submission_data.get("updated_at")
            })
        
        return submissions
        
    except Exception as e:
        logger.error(f"Error getting community submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get community submissions")


@app.post("/api/community/vote")
@limiter.limit("50/minute")
async def submit_community_vote(
    request: Request,
    vote: CommunityVote
):
    """Submit community vote for innovation verification using Supabase client"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Create vote record in Supabase
        vote_record = {
            "innovation_id": str(vote.innovation_id),
            "voter_id": vote.voter_id,
            "vote_type": vote.vote_type,
            "comment": vote.comment if hasattr(vote, 'comment') else None
        }
        
        supabase.table('community_votes').insert(vote_record).execute()
        
        return {"status": "vote_recorded", "message": "Thank you for your vote"}
        
    except Exception as e:
        logger.error(f"Error submitting community vote: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit vote")


# Statistics Endpoints
@app.get("/api/stats", response_model=InnovationStats)
@limiter.limit("10/minute")
async def get_statistics(request: Request):
    """Get platform statistics using Supabase client"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Start with basic response structure
        result = {
            "total_innovations": 0,
            "verified_innovations": 0,
            "pending_innovations": 0,
            "innovations_by_type": {},
            "innovations_by_country": {},
            "innovations_by_month": {},
            "total_funding": None,
            "average_funding": None
        }
        
        # Try to get basic count first
        try:
            total_response = supabase.table('innovations').select('*', count='exact').execute()
            result["total_innovations"] = total_response.count if total_response.count is not None else 0
            
            # If we have data, process it
            if total_response.data:
                verified_count = 0
                pending_count = 0
                type_counts = {}
                country_counts = {}
                
                for item in total_response.data:
                    # Count by verification status
                    status = item.get('verification_status', 'unknown')
                    if status == 'verified':
                        verified_count += 1
                    elif status == 'pending':
                        pending_count += 1
                    
                    # Count by type
                    innovation_type = item.get('innovation_type', 'Unknown')
                    type_counts[innovation_type] = type_counts.get(innovation_type, 0) + 1
                    
                    # Count by country
                    country = item.get('country', 'Unknown')
                    country_counts[country] = country_counts.get(country, 0) + 1
                
                result["verified_innovations"] = verified_count
                result["pending_innovations"] = pending_count
                result["innovations_by_type"] = type_counts
                result["innovations_by_country"] = country_counts
                
        except Exception as query_error:
            logger.error(f"Error in statistics query: {query_error}")
            # Return basic structure even if query fails
            pass
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


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
    """Get comprehensive ETL validation system status"""
    try:
        from services.etl_monitor import etl_monitor
        dashboard_data = etl_monitor.get_dashboard_data()
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
        health = etl_monitor.get_system_health()
        return {
            "status": "healthy" if health.database_status == "healthy" else "degraded",
            "system_health": {
                "cpu_percent": health.cpu_percent,
                "memory_percent": health.memory_percent,
                "disk_usage": health.disk_usage,
                "database_status": health.database_status,
                "vector_db_status": health.vector_db_status
            },
            "last_check": health.last_check.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ETL health: {e}")
        raise HTTPException(status_code=500, detail="ETL health check failed")


@app.get("/api/validation/summary")
@limiter.limit("20/minute")
async def get_validation_summary(request: Request):
    """Get validation system summary for homepage using Supabase client"""
    try:
        from services.etl_monitor import etl_monitor
        summary = etl_monitor.get_validation_summary()

        # Add database counts using Supabase
        from config.database import get_supabase
        supabase = get_supabase()
        
        try:
            # Get total innovations count
            total_response = supabase.table('innovations').select('id', count='exact').execute()
            total_innovations = total_response.count if total_response.count is not None else 0
            
            # Get verified innovations count
            verified_response = supabase.table('innovations').select('id', count='exact').eq('verification_status', 'verified').execute()
            verified_innovations = verified_response.count if verified_response.count is not None else 0

            summary.update({
                "innovations_tracked": total_innovations,
                "innovations_verified": verified_innovations,
                "validation_rate": round((verified_innovations / max(1, total_innovations)) * 100, 1)
            })
        except Exception as db_error:
            logger.error(f"Error getting database counts for validation summary: {db_error}")
            # Continue with ETL summary even if database counts fail
            summary.update({
                "innovations_tracked": 0,
                "innovations_verified": 0,
                "validation_rate": 0.0
            })

        return summary

    except Exception as e:
        logger.error(f"Error getting validation summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation summary")


@app.get("/api/etl/jobs")
@limiter.limit("30/minute")
async def get_etl_jobs(request, active_only: bool = False):
    """Get ETL job statuses"""
    try:
        from services.etl_monitor import etl_monitor
        dashboard_data = etl_monitor.get_dashboard_data()

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
        activity = etl_monitor.get_recent_discoveries(hours)
        return {
            "activity": activity,
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent ETL activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ETL activity")


# Vector Database Monitoring Endpoints
@app.get("/api/vector/stats")
@limiter.limit("20/minute")
async def get_vector_stats(
    request: Request,
    vector_service: VectorService = Depends(get_vector_service)
):
    """Get vector database statistics and coverage"""
    try:
        # Get vector database stats
        vector_stats = await vector_service.get_stats()
        
        # Get database counts from Supabase
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Count total innovations and publications
        innovations_response = supabase.table('innovations').select('id', count='exact').execute()
        publications_response = supabase.table('publications').select('id', count='exact').execute()
        
        total_innovations = innovations_response.count if innovations_response.count is not None else 0
        total_publications = publications_response.count if publications_response.count is not None else 0
        total_documents = total_innovations + total_publications
        
        # Calculate coverage (approximate)
        total_vectors = vector_stats.get('total_vectors', 0)
        coverage_percentage = round((total_vectors / max(1, total_documents)) * 100, 1) if total_documents > 0 else 0
        
        return {
            "vector_database": vector_stats,
            "coverage": {
                "total_documents_in_db": total_documents,
                "innovations_in_db": total_innovations,
                "publications_in_db": total_publications,
                "total_vectors": total_vectors,
                "coverage_percentage": coverage_percentage,
                "estimated_missing": max(0, total_documents - total_vectors)
            },
            "status": "healthy" if total_vectors > 0 else "needs_rebuild",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting vector statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get vector statistics")


@app.get("/api/vector/search-quality")
@limiter.limit("30/minute")
async def test_search_quality(
    request: Request,
    test_queries: List[str] = Query(["AI agriculture", "machine learning healthcare", "fintech innovation"]),
    vector_service: VectorService = Depends(get_vector_service)
):
    """Test search quality with sample queries"""
    try:
        results = {}
        
        for query in test_queries[:5]:  # Limit to 5 queries
            try:
                # Test vector search
                vector_results = await vector_service.search_innovations(query, top_k=5)
                
                # Calculate quality metrics
                avg_score = sum(r.score for r in vector_results) / len(vector_results) if vector_results else 0
                
                results[query] = {
                    "results_count": len(vector_results),
                    "avg_relevance_score": round(avg_score, 3),
                    "top_results": [
                        {
                            "title": r.metadata.get('title', 'No title'),
                            "score": round(r.score, 3),
                            "type": r.metadata.get('innovation_type', 'Unknown')
                        }
                        for r in vector_results[:3]
                    ]
                }
            except Exception as query_error:
                results[query] = {
                    "error": str(query_error),
                    "results_count": 0,
                    "avg_relevance_score": 0
                }
        
        # Calculate overall quality
        total_results = sum(r.get('results_count', 0) for r in results.values())
        avg_quality = sum(r.get('avg_relevance_score', 0) for r in results.values()) / len(results)
        
        return {
            "test_results": results,
            "overall_quality": {
                "total_test_queries": len(test_queries),
                "total_results_found": total_results,
                "average_relevance_score": round(avg_quality, 3),
                "quality_rating": "excellent" if avg_quality > 0.8 else "good" if avg_quality > 0.6 else "needs_improvement"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing search quality: {e}")
        raise HTTPException(status_code=500, detail="Failed to test search quality")


@app.post("/api/vector/rebuild")
@limiter.limit("2/hour")  # Very limited - this is an expensive operation
async def trigger_vector_rebuild(
    request: Request,
    background_tasks: BackgroundTasks,
    document_types: List[str] = Query(["innovations", "publications"])
):
    """Trigger vector database rebuild (admin only)"""
    try:
        job_id = str(uuid4())
        
        # Add rebuild task to background
        background_tasks.add_task(
            run_vector_rebuild,
            job_id,
            document_types
        )
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Vector rebuild started for: {', '.join(document_types)}",
            "estimated_duration": "5-15 minutes",
            "warning": "This will regenerate all embeddings and may affect search temporarily"
        }
        
    except Exception as e:
        logger.error(f"Error triggering vector rebuild: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger vector rebuild")


async def run_vector_rebuild(job_id: str, document_types: List[str]):
    """Run vector database rebuild in background"""
    try:
        logger.info(f"Starting vector rebuild job {job_id} for types: {document_types}")
        
        # Import the rebuilder
        from scripts.rebuild_vectors import VectorRebuilder
        
        rebuilder = VectorRebuilder()
        
        if not await rebuilder.initialize():
            logger.error(f"Vector rebuild job {job_id} failed to initialize")
            return
        
        success = True
        
        if "innovations" in document_types:
            if not await rebuilder.rebuild_innovations():
                success = False
        
        if "publications" in document_types:
            if not await rebuilder.rebuild_publications():
                success = False
        
        await rebuilder.save_stats()
        
        if success:
            logger.info(f"Vector rebuild job {job_id} completed successfully")
        else:
            logger.warning(f"Vector rebuild job {job_id} completed with errors")
        
    except Exception as e:
        logger.error(f"Vector rebuild job {job_id} failed: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
