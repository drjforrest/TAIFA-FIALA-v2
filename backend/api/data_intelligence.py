"""
Data Intelligence API Endpoints for TAIFA-FIALA
Provides enhanced data analysis and competitive intelligence features
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from services.citations_analysis_service import citations_service
from services.enhanced_publication_service import enhanced_publication_service

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/data-intelligence", tags=["Data Intelligence"])


# CITATION NETWORK ENDPOINTS
@router.get("/citations/extract")
@limiter.limit("5/minute")
async def trigger_citation_extraction(
    request: Request,
    background_tasks: BackgroundTasks,
    batch_size: int = Query(50, ge=10, le=200, description="Number of publications to process per batch")
):
    """Trigger citation extraction and analysis"""
    try:
        if not await citations_service.initialize():
            raise HTTPException(status_code=500, detail="Failed to initialize citations service")
        
        # Run citation extraction in background
        background_tasks.add_task(run_citation_extraction_job, batch_size)
        
        return {
            "status": "started",
            "message": f"Citation extraction started for batch size {batch_size}",
            "estimated_duration": "5-15 minutes",
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering citation extraction: {e}")
        raise HTTPException(status_code=500, detail="Failed to start citation extraction")


@router.get("/citations/impact-scores")
@limiter.limit("10/minute")
async def calculate_impact_scores(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Calculate publication impact scores"""
    try:
        if not await citations_service.initialize():
            raise HTTPException(status_code=500, detail="Citations service not available")
        
        background_tasks.add_task(run_impact_scoring_job)
        
        return {
            "status": "started",
            "message": "Impact scoring calculation started",
            "estimated_duration": "3-10 minutes",
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering impact scoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to start impact scoring")


@router.get("/citations/knowledge-flows")
@limiter.limit("10/minute")
async def map_knowledge_flows(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Map research-to-innovation knowledge flows"""
    try:
        if not await citations_service.initialize():
            raise HTTPException(status_code=500, detail="Citations service not available")
        
        background_tasks.add_task(run_knowledge_flow_mapping)
        
        return {
            "status": "started",
            "message": "Knowledge flow mapping started",
            "estimated_duration": "5-15 minutes",
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering knowledge flow mapping: {e}")
        raise HTTPException(status_code=500, detail="Failed to start knowledge flow mapping")


@router.get("/citations/network-analytics")
@limiter.limit("20/minute")
async def get_citation_network_analytics(request: Request):
    """Get comprehensive citation network analytics"""
    try:
        if not await citations_service.initialize():
            raise HTTPException(status_code=500, detail="Citations service not available")
        
        analytics = await citations_service.generate_citation_network_analytics()
        
        if not analytics:
            return JSONResponse(content={
                "message": "No citation data available yet",
                "suggestion": "Run citation extraction first using /citations/extract endpoint",
                "network_overview": {
                    "total_publications": 0,
                    "total_citations": 0,
                    "citation_density": 0
                }
            })
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting citation analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get citation analytics")


# ENHANCED PUBLICATION ENDPOINTS
@router.get("/publications/enhance-metadata")
@limiter.limit("5/minute")
async def trigger_metadata_enhancement(
    request: Request,
    background_tasks: BackgroundTasks,
    batch_size: int = Query(100, ge=50, le=500, description="Number of publications to process per batch")
):
    """Trigger enhanced metadata extraction for publications"""
    try:
        background_tasks.add_task(run_metadata_enhancement_job, batch_size)
        
        return {
            "status": "started",
            "message": f"Metadata enhancement started for batch size {batch_size}",
            "estimated_duration": "10-30 minutes",
            "features": [
                "Author affiliation extraction",
                "Institutional connection mapping",
                "Development stage detection",
                "Business model identification",
                "Technology extraction"
            ],
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering metadata enhancement: {e}")
        raise HTTPException(status_code=500, detail="Failed to start metadata enhancement")


@router.get("/publications/intelligence-report")
@limiter.limit("10/minute")
async def get_publication_intelligence_report(request: Request):
    """Get comprehensive publication intelligence report"""
    try:
        report = await enhanced_publication_service.generate_publication_intelligence_report()
        
        if not report:
            return JSONResponse(content={
                "message": "No enhanced publication data available yet",
                "suggestion": "Run metadata enhancement first using /publications/enhance-metadata endpoint",
                "overview": {
                    "total_publications_analyzed": 0,
                    "publications_with_stage_info": 0,
                    "publications_with_business_model": 0
                }
            })
        
        return JSONResponse(content=report)
        
    except Exception as e:
        logger.error(f"Error getting publication intelligence report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get publication intelligence")


# COMPETITIVE INTELLIGENCE ENDPOINTS
@router.get("/competitive/first-movers")
@limiter.limit("20/minute")
async def get_first_movers(
    request: Request,
    domain: Optional[str] = Query(None, description="Filter by domain (e.g., 'agriculture', 'healthcare')"),
    limit: int = Query(20, ge=5, le=100)
):
    """Get first movers in emerging domains"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Get publications with development stages
        query = supabase.table('publications').select(
            'id, title, abstract, publication_date, development_stage, extracted_technologies, target_markets'
        ).eq('development_stage', 'research').order('publication_date', desc=False)
        
        if domain:
            # Filter by domain in target markets or technologies
            query = query.contains('target_markets', [domain])
        
        response = query.limit(limit * 2).execute()  # Get more to filter
        publications = response.data if response.data else []
        
        # Group by technology/domain and find earliest
        domain_first_movers = {}
        
        for pub in publications:
            technologies = pub.get('extracted_technologies', [])
            markets = pub.get('target_markets', [])
            
            for tech in technologies:
                if isinstance(tech, dict):
                    tech_name = tech.get('technology', '').lower()
                    category = tech.get('category', 'unknown')
                    
                    if tech_name not in domain_first_movers:
                        domain_first_movers[tech_name] = {
                            'publication': pub,
                            'category': category
                        }
            
            for market in markets:
                if market not in domain_first_movers:
                    domain_first_movers[market] = {
                        'publication': pub,
                        'category': 'market'
                    }
        
        # Format response
        first_movers = []
        for domain_key, data in list(domain_first_movers.items())[:limit]:
            pub = data['publication']
            first_movers.append({
                'domain': domain_key,
                'category': data['category'],
                'publication_id': pub['id'],
                'title': pub['title'],
                'publication_date': pub['publication_date'],
                'abstract': pub.get('abstract', '')[:200] + '...' if pub.get('abstract') else '',
                'first_mover_score': 1.0  # Could be enhanced with more sophisticated scoring
            })
        
        return {
            'first_movers': first_movers,
            'total_domains': len(domain_first_movers),
            'analysis_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting first movers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get first movers")


@router.get("/competitive/collaboration-opportunities")
@limiter.limit("20/minute")
async def get_collaboration_opportunities(
    request: Request,
    country: Optional[str] = Query(None, description="Focus country for collaboration opportunities"),
    limit: int = Query(15, ge=5, le=50)
):
    """Identify collaboration opportunities between institutions/countries"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Get institutional connections
        connections_response = supabase.table('institutional_connections').select('*').execute()
        affiliations_response = supabase.table('author_affiliations').select('*').execute()
        
        connections = connections_response.data if connections_response.data else []
        affiliations = affiliations_response.data if affiliations_response.data else []
        
        if not connections and not affiliations:
            return JSONResponse(content={
                "message": "No institutional data available",
                "suggestion": "Run metadata enhancement to extract institutional information",
                "collaboration_opportunities": []
            })
        
        # Analyze gaps and opportunities
        opportunities = []
        
        # Group affiliations by country and institution
        country_institutions = {}
        for aff in affiliations:
            country = aff.get('country', 'Unknown')
            institution = aff.get('institution', '')
            
            if country not in country_institutions:
                country_institutions[country] = set()
            country_institutions[country].add(institution)
        
        # Find countries/institutions with complementary expertise but no connections
        existing_connections = set()
        for conn in connections:
            pair = tuple(sorted([conn['institution_1'], conn['institution_2']]))
            existing_connections.add(pair)
        
        # Identify potential new collaborations
        countries = list(country_institutions.keys())
        for i, country1 in enumerate(countries):
            for country2 in countries[i+1:]:
                if country and country.lower() not in [country1.lower(), country2.lower()]:
                    continue
                
                # Check for institutions that could collaborate
                for inst1 in country_institutions[country1]:
                    for inst2 in country_institutions[country2]:
                        pair = tuple(sorted([inst1, inst2]))
                        
                        if pair not in existing_connections and inst1 != inst2:
                            opportunities.append({
                                'institution_1': inst1,
                                'country_1': country1,
                                'institution_2': inst2,
                                'country_2': country2,
                                'opportunity_type': 'cross_border_collaboration',
                                'potential_strength': 0.7,  # Could be calculated based on expertise overlap
                                'suggested_areas': ['AI research', 'Technology transfer', 'Student exchange']
                            })
        
        # Sort by potential and limit
        opportunities.sort(key=lambda x: x['potential_strength'], reverse=True)
        
        return {
            'collaboration_opportunities': opportunities[:limit],
            'analysis_scope': {
                'countries_analyzed': len(countries),
                'institutions_analyzed': sum(len(insts) for insts in country_institutions.values()),
                'existing_connections': len(existing_connections)
            },
            'analysis_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting collaboration opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collaboration opportunities")


@router.get("/competitive/commercialization-ready")
@limiter.limit("20/minute")
async def get_commercialization_ready_research(
    request: Request,
    min_readiness_score: float = Query(0.7, ge=0.0, le=1.0),
    limit: int = Query(20, ge=5, le=100)
):
    """Get research with high commercialization potential"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Get publications with development stage and business model info
        response = supabase.table('publications').select(
            'id, title, abstract, development_stage, business_model, target_markets, stage_confidence, business_model_confidence'
        ).execute()
        
        publications = response.data if response.data else []
        
        if not publications:
            return JSONResponse(content={
                "message": "No publication data available",
                "commercialization_ready": []
            })
        
        commercialization_candidates = []
        
        for pub in publications:
            # Calculate commercialization readiness score
            readiness_score = 0.0
            factors = []
            
            # Stage factor
            stage = pub.get('development_stage')
            stage_confidence = pub.get('stage_confidence', 0)
            
            if stage in ['prototype', 'pilot', 'scaling']:
                readiness_score += 0.4 * stage_confidence
                factors.append(f"Advanced stage: {stage}")
            
            # Business model factor
            business_model = pub.get('business_model')
            bm_confidence = pub.get('business_model_confidence', 0)
            
            if business_model in ['B2B', 'B2C']:
                readiness_score += 0.3 * bm_confidence
                factors.append(f"Clear business model: {business_model}")
            
            # Market factor
            markets = pub.get('target_markets', [])
            if markets:
                readiness_score += 0.2
                factors.append(f"Identified markets: {', '.join(markets)}")
            
            # Abstract analysis for commercial indicators
            abstract = pub.get('abstract', '').lower()
            commercial_indicators = ['product', 'service', 'commercial', 'market', 'customer', 'business']
            commercial_score = sum(1 for indicator in commercial_indicators if indicator in abstract)
            
            if commercial_score > 0:
                readiness_score += min(0.1 * commercial_score, 0.1)
                factors.append(f"Commercial language present")
            
            if readiness_score >= min_readiness_score:
                commercialization_candidates.append({
                    'publication_id': pub['id'],
                    'title': pub['title'],
                    'readiness_score': round(readiness_score, 3),
                    'development_stage': stage,
                    'business_model': business_model,
                    'target_markets': markets,
                    'readiness_factors': factors,
                    'abstract_preview': pub.get('abstract', '')[:200] + '...' if pub.get('abstract') else ''
                })
        
        # Sort by readiness score
        commercialization_candidates.sort(key=lambda x: x['readiness_score'], reverse=True)
        
        return {
            'commercialization_ready': commercialization_candidates[:limit],
            'analysis_criteria': {
                'min_readiness_score': min_readiness_score,
                'factors_considered': [
                    'Development stage (40% weight)',
                    'Business model clarity (30% weight)',
                    'Target market identification (20% weight)',
                    'Commercial language (10% weight)'
                ]
            },
            'total_candidates': len(commercialization_candidates),
            'analysis_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting commercialization-ready research: {e}")
        raise HTTPException(status_code=500, detail="Failed to get commercialization-ready research")


@router.get("/competitive/research-leaders")
@limiter.limit("20/minute")
async def get_research_leaders(
    request: Request,
    metric: str = Query("influence_score", description="Ranking metric: influence_score, citation_count, h_index_contribution"),
    limit: int = Query(25, ge=5, le=100)
):
    """Get leading researchers and institutions by various metrics"""
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        
        # Get publications with impact metrics
        response = supabase.table('publications').select(
            'id, title, authors, impact_metrics, publication_date'
        ).execute()
        
        publications = response.data if response.data else []
        
        # Get author affiliations
        affiliations_response = supabase.table('author_affiliations').select('*').execute()
        affiliations = affiliations_response.data if affiliations_response.data else []
        
        if not publications:
            return JSONResponse(content={
                "message": "No publication impact data available",
                "suggestion": "Run impact scoring first",
                "research_leaders": []
            })
        
        # Aggregate metrics by author and institution
        author_metrics = {}
        institution_metrics = {}
        
        # Create author-institution mapping
        author_institutions = {}
        for aff in affiliations:
            author_institutions[aff['author_name']] = {
                'institution': aff['institution'],
                'country': aff['country']
            }
        
        for pub in publications:
            impact_metrics = pub.get('impact_metrics', {})
            if not impact_metrics:
                continue
            
            authors = pub.get('authors', [])
            
            for author in authors:
                if isinstance(author, str):
                    if author not in author_metrics:
                        author_metrics[author] = {
                            'name': author,
                            'publication_count': 0,
                            'total_influence': 0,
                            'total_citations': 0,
                            'h_index_contribution': 0,
                            'institution': author_institutions.get(author, {}).get('institution', 'Unknown'),
                            'country': author_institutions.get(author, {}).get('country', 'Unknown')
                        }
                    
                    author_metrics[author]['publication_count'] += 1
                    author_metrics[author]['total_influence'] += impact_metrics.get('influence_score', 0)
                    author_metrics[author]['total_citations'] += impact_metrics.get('citation_count', 0)
                    author_metrics[author]['h_index_contribution'] += impact_metrics.get('h_index_contribution', 0)
        
        # Aggregate by institution
        for author_data in author_metrics.values():
            institution = author_data['institution']
            if institution != 'Unknown':
                if institution not in institution_metrics:
                    institution_metrics[institution] = {
                        'institution': institution,
                        'country': author_data['country'],
                        'author_count': 0,
                        'publication_count': 0,
                        'total_influence': 0,
                        'total_citations': 0
                    }
                
                institution_metrics[institution]['author_count'] += 1
                institution_metrics[institution]['publication_count'] += author_data['publication_count']
                institution_metrics[institution]['total_influence'] += author_data['total_influence']
                institution_metrics[institution]['total_citations'] += author_data['total_citations']
        
        # Sort by requested metric
        metric_map = {
            'influence_score': 'total_influence',
            'citation_count': 'total_citations',
            'h_index_contribution': 'h_index_contribution'
        }
        
        sort_key = metric_map.get(metric, 'total_influence')
        
        top_authors = sorted(
            author_metrics.values(),
            key=lambda x: x.get(sort_key, 0),
            reverse=True
        )[:limit]
        
        top_institutions = sorted(
            institution_metrics.values(),
            key=lambda x: x.get(sort_key, 0),
            reverse=True
        )[:limit]
        
        return {
            'research_leaders': {
                'top_authors': top_authors,
                'top_institutions': top_institutions
            },
            'ranking_criteria': {
                'metric_used': metric,
                'total_authors_analyzed': len(author_metrics),
                'total_institutions_analyzed': len(institution_metrics)
            },
            'analysis_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting research leaders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get research leaders")


# BACKGROUND TASK FUNCTIONS
async def run_citation_extraction_job(batch_size: int):
    """Background job for citation extraction"""
    try:
        logger.info(f"Starting citation extraction job with batch size {batch_size}")
        
        if not await citations_service.initialize():
            logger.error("Failed to initialize citations service for background job")
            return
        
        citations = await citations_service.extract_citations_from_publications(batch_size)
        
        logger.info(f"Citation extraction job completed: {len(citations)} citations extracted")
        
    except Exception as e:
        logger.error(f"Citation extraction job failed: {e}")


async def run_impact_scoring_job():
    """Background job for impact scoring"""
    try:
        logger.info("Starting impact scoring job")
        
        if not await citations_service.initialize():
            logger.error("Failed to initialize citations service for impact scoring")
            return
        
        impact_metrics = await citations_service.calculate_publication_impact_scores()
        
        logger.info(f"Impact scoring job completed: {len(impact_metrics)} publications scored")
        
    except Exception as e:
        logger.error(f"Impact scoring job failed: {e}")


async def run_knowledge_flow_mapping():
    """Background job for knowledge flow mapping"""
    try:
        logger.info("Starting knowledge flow mapping job")
        
        if not await citations_service.initialize():
            logger.error("Failed to initialize citations service for knowledge flow mapping")
            return
        
        flows = await citations_service.map_research_to_innovation_flows()
        
        logger.info(f"Knowledge flow mapping completed: {len(flows)} flows mapped")
        
    except Exception as e:
        logger.error(f"Knowledge flow mapping job failed: {e}")


async def run_metadata_enhancement_job(batch_size: int):
    """Background job for metadata enhancement"""
    try:
        logger.info(f"Starting metadata enhancement job with batch size {batch_size}")
        
        results = await enhanced_publication_service.enhance_publication_metadata(batch_size)
        
        total_processed = results.get('total_processed', 0)
        logger.info(f"Metadata enhancement job completed: {total_processed} publications processed")
        
    except Exception as e:
        logger.error(f"Metadata enhancement job failed: {e}")