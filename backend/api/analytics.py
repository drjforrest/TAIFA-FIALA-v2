"""
Analytics API Endpoints
======================

Provides analytics data for the dashboard including charts, metrics, and trends.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/innovations")
@limiter.limit("30/minute")
async def get_innovation_analytics(
    request: Request,
    days_back: int = Query(30, ge=7, le=365, description="Days to look back for analytics"),
    country: Optional[str] = Query(None, description="Filter by country"),
    innovation_type: Optional[str] = Query(None, description="Filter by innovation type")
):
    """Get comprehensive innovation analytics for dashboard charts"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Base query
        query = supabase.table('innovations').select('*')
        
        # Apply filters
        if country:
            query = query.eq('country', country)
        if innovation_type:
            query = query.eq('innovation_type', innovation_type)
        
        # Execute query
        response = query.execute()
        innovations = response.data or []
        
        # Process analytics
        analytics = {
            "summary": {
                "total_innovations": len(innovations),
                "verified_innovations": len([i for i in innovations if i.get('verification_status') == 'verified']),
                "countries_represented": len(set(i.get('country') for i in innovations if i.get('country'))),
                "avg_verification_rate": 0,
                "period_days": days_back,
                "last_updated": datetime.now().isoformat()
            },
            "by_country": {},
            "by_type": {},
            "by_verification_status": {},
            "timeline": [],
            "funding_analytics": {
                "total_funding": 0,
                "funded_innovations": 0,
                "avg_funding": 0,
                "by_funding_type": {}
            },
            "trending_tags": [],
            "impact_metrics": {
                "total_users_reached": 0,
                "innovations_with_metrics": 0
            }
        }
        
        # Calculate verification rate
        if innovations:
            verified_count = len([i for i in innovations if i.get('verification_status') == 'verified'])
            analytics["summary"]["avg_verification_rate"] = round((verified_count / len(innovations)) * 100, 1)
        
        # Group by country
        country_counts = defaultdict(int)
        for innovation in innovations:
            country = innovation.get('country', 'Unknown')
            country_counts[country] += 1
        
        analytics["by_country"] = dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Group by type
        type_counts = defaultdict(int)
        for innovation in innovations:
            itype = innovation.get('innovation_type', 'Unknown')
            type_counts[itype] += 1
        
        analytics["by_type"] = dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Group by verification status
        status_counts = defaultdict(int)
        for innovation in innovations:
            status = innovation.get('verification_status', 'pending')
            status_counts[status] += 1
        
        analytics["by_verification_status"] = dict(status_counts)
        
        # Calculate funding analytics
        total_funding = 0
        funded_innovations = 0
        funding_type_counts = defaultdict(int)
        
        for innovation in innovations:
            fundings = innovation.get('fundings', [])
            if fundings:
                funded_innovations += 1
                for funding in fundings:
                    amount = funding.get('amount', 0)
                    if amount and isinstance(amount, (int, float)):
                        total_funding += amount
                    
                    funding_type = funding.get('funding_type', 'unknown')
                    funding_type_counts[funding_type] += 1
        
        analytics["funding_analytics"] = {
            "total_funding": total_funding,
            "funded_innovations": funded_innovations,
            "avg_funding": round(total_funding / funded_innovations, 2) if funded_innovations > 0 else 0,
            "by_funding_type": dict(funding_type_counts)
        }
        
        # Calculate impact metrics
        total_users = 0
        innovations_with_metrics = 0
        
        for innovation in innovations:
            impact_metrics = innovation.get('impact_metrics', {})
            if impact_metrics:
                innovations_with_metrics += 1
                users_reached = impact_metrics.get('users_reached', 0)
                if users_reached and isinstance(users_reached, (int, float)):
                    total_users += users_reached
        
        analytics["impact_metrics"] = {
            "total_users_reached": total_users,
            "innovations_with_metrics": innovations_with_metrics
        }
        
        # Generate trending tags
        tag_counts = defaultdict(int)
        for innovation in innovations:
            tags = innovation.get('tags', [])
            for tag in tags:
                if tag:
                    tag_counts[tag] += 1
        
        # Sort tags by frequency and take top 10
        trending_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        analytics["trending_tags"] = [{"tag": tag, "count": count} for tag, count in trending_tags]
        
        # Generate timeline data (grouped by month for the period)
        timeline_data = defaultdict(int)
        for innovation in innovations:
            created_at = innovation.get('created_at')
            if created_at:
                try:
                    # Parse date and group by month
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if date >= start_date:
                        month_key = date.strftime('%Y-%m')
                        timeline_data[month_key] += 1
                except Exception:
                    pass
        
        # Convert timeline to sorted list
        timeline = []
        for month, count in sorted(timeline_data.items()):
            timeline.append({
                "period": month,
                "count": count,
                "label": datetime.strptime(month, '%Y-%m').strftime('%b %Y')
            })
        
        analytics["timeline"] = timeline
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting innovation analytics: {e}")
        # Return sample data if database fails
        return JSONResponse(content={
            "summary": {
                "total_innovations": 0,
                "verified_innovations": 0,
                "countries_represented": 0,
                "avg_verification_rate": 0,
                "period_days": days_back,
                "last_updated": datetime.now().isoformat()
            },
            "by_country": {},
            "by_type": {},
            "by_verification_status": {"pending": 0, "verified": 0},
            "timeline": [],
            "funding_analytics": {
                "total_funding": 0,
                "funded_innovations": 0,
                "avg_funding": 0,
                "by_funding_type": {}
            },
            "trending_tags": [],
            "impact_metrics": {
                "total_users_reached": 0,
                "innovations_with_metrics": 0
            },
            "error": str(e)
        })


@router.get("/publications")
@limiter.limit("30/minute")
async def get_publication_analytics(
    request: Request,
    days_back: int = Query(30, ge=7, le=365),
    source: Optional[str] = Query(None, description="Filter by publication source")
):
    """Get publication analytics for research trends"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Base query
        query = supabase.table('publications').select('*')
        
        if source:
            query = query.eq('source', source)
        
        response = query.execute()
        publications = response.data or []
        
        analytics = {
            "summary": {
                "total_publications": len(publications),
                "avg_african_relevance": 0,
                "avg_ai_relevance": 0,
                "sources_count": len(set(p.get('source') for p in publications if p.get('source'))),
                "period_days": days_back
            },
            "by_source": {},
            "by_african_relevance": {
                "high": 0,    # > 0.7
                "medium": 0,  # 0.4 - 0.7
                "low": 0      # < 0.4
            },
            "timeline": [],
            "trending_keywords": [],
            "african_entities": {}
        }
        
        # Calculate averages and distributions
        african_scores = []
        ai_scores = []
        source_counts = defaultdict(int)
        keyword_counts = defaultdict(int)
        entity_counts = defaultdict(int)
        
        for pub in publications:
            # African relevance
            african_score = pub.get('african_relevance_score', 0)
            if african_score and isinstance(african_score, (int, float)):
                african_scores.append(african_score)
                
                if african_score > 0.7:
                    analytics["by_african_relevance"]["high"] += 1
                elif african_score > 0.4:
                    analytics["by_african_relevance"]["medium"] += 1
                else:
                    analytics["by_african_relevance"]["low"] += 1
            
            # AI relevance
            ai_score = pub.get('ai_relevance_score', 0)
            if ai_score and isinstance(ai_score, (int, float)):
                ai_scores.append(ai_score)
            
            # Source counts
            source = pub.get('source', 'Unknown')
            source_counts[source] += 1
            
            # Keywords
            keywords = pub.get('keywords', [])
            for keyword in keywords:
                if keyword:
                    keyword_counts[keyword] += 1
            
            # African entities
            entities = pub.get('african_entities', [])
            for entity in entities:
                if entity:
                    entity_counts[entity] += 1
        
        # Calculate averages
        if african_scores:
            analytics["summary"]["avg_african_relevance"] = round(sum(african_scores) / len(african_scores), 3)
        if ai_scores:
            analytics["summary"]["avg_ai_relevance"] = round(sum(ai_scores) / len(ai_scores), 3)
        
        # Top sources
        analytics["by_source"] = dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Trending keywords (top 15)
        trending_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        analytics["trending_keywords"] = [{"keyword": kw, "count": count} for kw, count in trending_keywords]
        
        # African entities (top 10)
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        analytics["african_entities"] = dict(top_entities)
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting publication analytics: {e}")
        return JSONResponse(content={
            "summary": {
                "total_publications": 0,
                "avg_african_relevance": 0,
                "avg_ai_relevance": 0,
                "sources_count": 0,
                "period_days": days_back
            },
            "by_source": {},
            "by_african_relevance": {"high": 0, "medium": 0, "low": 0},
            "timeline": [],
            "trending_keywords": [],
            "african_entities": {},
            "error": str(e)
        })


@router.get("/etl-performance")
@limiter.limit("30/minute")
async def get_etl_performance_analytics(request: Request):
    """Get ETL pipeline performance analytics"""
    try:
        from services.etl_monitor import etl_monitor
        
        # Get ETL dashboard data
        dashboard_data = etl_monitor.get_dashboard_data()
        
        # Get cache performance
        cache_performance = {}
        try:
            from services.unified_cache import unified_cache
            from services.null_result_cache import null_result_cache
            
            async with unified_cache as u_cache:
                unified_stats = await u_cache.get_cache_stats()
            
            async with null_result_cache as n_cache:
                null_stats = await n_cache.get_cache_stats()
            
            cache_performance = {
                "unified_cache": {
                    "hit_rate": unified_stats.get("hit_rate", 0),
                    "total_operations": unified_stats.get("performance", {}).get("hits", 0) + unified_stats.get("performance", {}).get("misses", 0),
                    "memory_usage": unified_stats.get("redis_cache", {}).get("memory_usage_human", "0B")
                },
                "null_cache": {
                    "cached_items": null_stats.get("total_cached_items", 0),
                    "permanent_cache": null_stats.get("permanent_cache_count", 0)
                }
            }
        except Exception as cache_error:
            logger.warning(f"Could not get cache performance: {cache_error}")
            cache_performance = {"error": "Cache metrics unavailable"}
        
        analytics = {
            "pipeline_status": {
                "active_pipelines": len([job for job in dashboard_data["job_statuses"] if job["is_running"]]),
                "healthy_pipelines": len([job for job in dashboard_data["job_statuses"] if job["health_status"] == "healthy"]),
                "total_pipelines": len(dashboard_data["job_statuses"])
            },
            "job_performance": dashboard_data["job_statuses"],
            "recent_activity": dashboard_data["recent_discoveries"],
            "cache_performance": cache_performance,
            "system_health": dashboard_data.get("system_health", {}),
            "last_updated": dashboard_data["timestamp"]
        }
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting ETL performance analytics: {e}")
        return JSONResponse(content={
            "pipeline_status": {
                "active_pipelines": 0,
                "healthy_pipelines": 0,
                "total_pipelines": 0
            },
            "job_performance": [],
            "recent_activity": [],
            "cache_performance": {"error": "Unavailable"},
            "system_health": {},
            "error": str(e)
        })


@router.get("/research-trends")
@limiter.limit("20/minute")
async def get_research_trends(
    request: Request,
    months_back: int = Query(12, ge=3, le=24)
):
    """Get research trends and citation network analytics"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Get recent publications
        response = supabase.table('publications').select('*').limit(1000).execute()
        publications = response.data or []
        
        analytics = {
            "research_focus_areas": {},
            "collaboration_networks": {},
            "emerging_topics": [],
            "citation_impact": {
                "total_citations": 0,
                "avg_citations_per_paper": 0,
                "high_impact_papers": []
            },
            "geographic_distribution": {},
            "methodology_trends": {}
        }
        
        # Analyze research focus areas (from keywords)
        focus_areas = defaultdict(int)
        geographic_dist = defaultdict(int)
        
        for pub in publications:
            keywords = pub.get('keywords', [])
            for keyword in keywords:
                if keyword and len(keyword) > 2:
                    focus_areas[keyword] += 1
            
            # Geographic distribution from African entities
            entities = pub.get('african_entities', [])
            for entity in entities:
                if entity:
                    geographic_dist[entity] += 1
        
        # Top focus areas
        top_focus_areas = sorted(focus_areas.items(), key=lambda x: x[1], reverse=True)[:20]
        analytics["research_focus_areas"] = dict(top_focus_areas)
        
        # Geographic distribution
        analytics["geographic_distribution"] = dict(sorted(geographic_dist.items(), key=lambda x: x[1], reverse=True)[:15])
        
        # Emerging topics (keywords that appear frequently in recent papers)
        recent_keywords = defaultdict(int)
        cutoff_date = datetime.now() - timedelta(days=90)  # Last 3 months
        
        for pub in publications:
            pub_date = pub.get('publication_date')
            if pub_date:
                try:
                    date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    if date >= cutoff_date:
                        keywords = pub.get('keywords', [])
                        for keyword in keywords:
                            if keyword and len(keyword) > 2:
                                recent_keywords[keyword] += 1
                except Exception:
                    pass
        
        emerging_topics = sorted(recent_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        analytics["emerging_topics"] = [{"topic": topic, "mentions": count} for topic, count in emerging_topics]
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting research trends: {e}")
        return JSONResponse(content={
            "research_focus_areas": {},
            "collaboration_networks": {},
            "emerging_topics": [],
            "citation_impact": {
                "total_citations": 0,
                "avg_citations_per_paper": 0,
                "high_impact_papers": []
            },
            "geographic_distribution": {},
            "methodology_trends": {},
            "error": str(e)
        })