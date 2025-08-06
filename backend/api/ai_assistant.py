"""
AI Assistant API Endpoints for TAIFA-FIALA
Provides intelligent Q&A and insights using Pinecone Assistant RAG capabilities
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from services.pinecone_assistant_service import pinecone_assistant_service
from config.database import get_supabase

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/ai-assistant", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    innovation_id: Optional[str] = None
    context_filter: Optional[Dict[str, Any]] = None


class FileUploadRequest(BaseModel):
    file_path: str
    timeout: Optional[int] = None


@router.post("/initialize")
@limiter.limit("5/minute")
async def initialize_assistant(request: Request):
    """Initialize the Pinecone Assistant"""
    try:
        success = await pinecone_assistant_service.initialize()
        
        if success:
            return {
                "status": "initialized",
                "assistant_name": "ai-innovations",
                "message": "Pinecone Assistant ready for African AI ecosystem queries"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize assistant")
            
    except Exception as e:
        logger.error(f"Error initializing assistant: {e}")
        raise HTTPException(status_code=500, detail="Assistant initialization failed")


@router.post("/upload-data")
@limiter.limit("3/minute")
async def upload_database_content(
    request: Request,
    background_tasks: BackgroundTasks,
    data_type: str = Query("all", description="Type of data to upload: publications, innovations, or all"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to upload")
):
    """Upload database content to Pinecone Assistant for RAG"""
    try:
        if not await pinecone_assistant_service.initialize():
            raise HTTPException(status_code=500, detail="Assistant not initialized")
        
        background_tasks.add_task(upload_data_job, data_type, limit)
        
        return {
            "status": "started",
            "message": f"Uploading {data_type} data to assistant",
            "data_type": data_type,
            "limit": limit,
            "estimated_duration": "5-15 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting data upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to start data upload")


@router.post("/chat")
@limiter.limit("30/minute")
async def chat_with_assistant(request: Request, chat_request: ChatRequest):
    """Chat with the AI assistant about African AI ecosystem"""
    try:
        if not await pinecone_assistant_service.initialize():
            raise HTTPException(status_code=500, detail="Assistant not initialized")
        
        # If innovation_id is provided, enhance the message with innovation context
        enhanced_message = chat_request.message
        if chat_request.innovation_id:
            innovation_data = await get_innovation_context(chat_request.innovation_id)
            if innovation_data:
                enhanced_message = await pinecone_assistant_service.enhance_message_with_innovation_context(
                    message=chat_request.message,
                    innovation=innovation_data
                )
        
        response = await pinecone_assistant_service.chat(
            message=enhanced_message,
            conversation_id=chat_request.conversation_id
        )
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return {
            "response": response["message"],
            "conversation_id": response.get("conversation_id"),
            "innovation_id": chat_request.innovation_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in assistant chat: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")


@router.get("/insights/{domain}")
@limiter.limit("10/minute")
async def get_domain_insights(
    request: Request,
    domain: str = "artificial intelligence"
):
    """Get research insights for a specific domain"""
    try:
        if not await pinecone_assistant_service.initialize():
            raise HTTPException(status_code=500, detail="Assistant not initialized")
        
        response = await pinecone_assistant_service.get_research_insights(domain)
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return {
            "domain": domain,
            "insights": response["message"],
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting domain insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")


@router.post("/ask-ecosystem")
@limiter.limit("20/minute")
async def ask_about_ecosystem(request: Request, chat_request: ChatRequest):
    """Ask specific questions about the African AI ecosystem"""
    try:
        if not await pinecone_assistant_service.initialize():
            raise HTTPException(status_code=500, detail="Assistant not initialized")
        
        response = await pinecone_assistant_service.ask_about_african_ai_ecosystem(
            chat_request.message
        )
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return {
            "question": chat_request.message,
            "answer": response["message"],
            "conversation_id": response.get("conversation_id"),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error asking about ecosystem: {e}")
        raise HTTPException(status_code=500, detail="Ecosystem query failed")


@router.get("/suggested-questions")
@limiter.limit("20/minute")
async def get_suggested_questions(request: Request):
    """Get suggested questions for the AI assistant"""
    
    suggested_questions = [
        {
            "category": "Research Trends",
            "questions": [
                "What are the top 5 AI research trends in Africa?",
                "Which African countries are leading in machine learning research?",
                "What are the most promising AI applications for African challenges?",
                "How has African AI research evolved over the past 5 years?"
            ]
        },
        {
            "category": "Institutions & Collaboration",
            "questions": [
                "Which universities are the most active in African AI research?",
                "What collaboration patterns exist between African institutions?",
                "Which researchers are most influential in African AI?",
                "How do African institutions collaborate with international partners?"
            ]
        },
        {
            "category": "Innovation & Commercialization",
            "questions": [
                "What AI innovations are closest to commercial deployment?",
                "Which African AI startups show the most promise?",
                "How is AI research being translated into products in Africa?",
                "What funding patterns exist for African AI innovations?"
            ]
        },
        {
            "category": "Technology & Methods",
            "questions": [
                "What are the most commonly used AI technologies in African research?",
                "How are researchers addressing data scarcity challenges?",
                "What novel AI approaches are being developed in Africa?",
                "Which programming languages and frameworks are most popular?"
            ]
        },
        {
            "category": "Impact & Applications",
            "questions": [
                "How is AI being applied to healthcare challenges in Africa?",
                "What agricultural AI solutions are being developed?",
                "How is AI addressing financial inclusion in Africa?",
                "What are the social impacts of AI research in Africa?"
            ]
        }
    ]
    
    return {
        "suggested_questions": suggested_questions,
        "total_categories": len(suggested_questions),
        "generated_at": datetime.now().isoformat()
    }


@router.get("/status")
@limiter.limit("30/minute")
async def get_assistant_status(request: Request):
    """Get current assistant status and data availability"""
    try:
        # Check if assistant is initialized
        initialized = await pinecone_assistant_service.initialize()
        
        # Get database counts
        supabase = get_supabase()
        
        pubs_response = supabase.table('publications').select('id', count='exact').execute()
        innovations_response = supabase.table('innovations').select('id', count='exact').execute()
        
        pub_count = pubs_response.count if pubs_response.count else 0
        innovation_count = innovations_response.count if innovations_response.count else 0
        
        return {
            "assistant_initialized": initialized,
            "assistant_name": "ai-innovations",
            "data_availability": {
                "publications_in_db": pub_count,
                "innovations_in_db": innovation_count,
                "total_documents": pub_count + innovation_count
            },
            "capabilities": [
                "African AI ecosystem Q&A",
                "Research trend analysis",
                "Institution and researcher insights",
                "Innovation commercialization analysis",
                "Technology and methodology insights"
            ],
            "status_checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking assistant status: {e}")
        return {
            "assistant_initialized": False,
            "error": str(e),
            "status_checked_at": datetime.now().isoformat()
        }


# Helper functions
async def get_innovation_context(innovation_id: str) -> Optional[Dict[str, Any]]:
    """Get innovation context from database including related data"""
    try:
        supabase = get_supabase()
        
        # Get innovation details
        innovation_response = supabase.table('innovations').select('*').eq('id', innovation_id).execute()
        
        if not innovation_response.data:
            logger.warning(f"Innovation {innovation_id} not found")
            return None
            
        innovation = innovation_response.data[0]
        
        # Get related publications (if any relationships exist)
        publications_response = supabase.table('innovation_publications').select(
            'publication_id, publications(*)'
        ).eq('innovation_id', innovation_id).execute()
        
        related_publications = []
        if publications_response.data:
            for rel in publications_response.data:
                if rel.get('publications'):
                    related_publications.append(rel['publications'])
        
        # Get organizations
        organizations_response = supabase.table('innovation_organizations').select(
            'organization_id, organizations(*)'
        ).eq('innovation_id', innovation_id).execute()
        
        related_organizations = []
        if organizations_response.data:
            for rel in organizations_response.data:
                if rel.get('organizations'):
                    related_organizations.append(rel['organizations'])
        
        # Get fundings
        fundings_response = supabase.table('fundings').select('*').eq('innovation_id', innovation_id).execute()
        related_fundings = fundings_response.data if fundings_response.data else []
        
        # Combine all context
        innovation_context = {
            **innovation,
            'related_publications': related_publications,
            'related_organizations': related_organizations, 
            'fundings': related_fundings
        }
        
        logger.info(f"Retrieved context for innovation {innovation_id}: {len(related_publications)} publications, {len(related_organizations)} organizations, {len(related_fundings)} fundings")
        
        return innovation_context
        
    except Exception as e:
        logger.error(f"Error getting innovation context for {innovation_id}: {e}")
        return None


# Background job functions
async def upload_data_job(data_type: str, limit: int):
    """Background job to upload database content to assistant"""
    try:
        logger.info(f"Starting assistant data upload job: {data_type}, limit: {limit}")
        
        supabase = get_supabase()
        uploaded_count = 0
        
        if data_type in ["publications", "all"]:
            # Upload publications
            response = supabase.table('publications').select('*').limit(limit).execute()
            publications = response.data if response.data else []
            
            for pub in publications:
                try:
                    result = await pinecone_assistant_service.upload_publication_content(pub)
                    if "error" not in result:
                        uploaded_count += 1
                except Exception as e:
                    logger.error(f"Error uploading publication {pub.get('id')}: {e}")
                    continue
            
            logger.info(f"Uploaded {len(publications)} publications to assistant")
        
        if data_type in ["innovations", "all"]:
            # Upload innovations
            innovation_limit = limit if data_type == "innovations" else limit // 2
            response = supabase.table('innovations').select('*').limit(innovation_limit).execute()
            innovations = response.data if response.data else []
            
            for innovation in innovations:
                try:
                    result = await pinecone_assistant_service.upload_innovation_content(innovation)
                    if "error" not in result:
                        uploaded_count += 1
                except Exception as e:
                    logger.error(f"Error uploading innovation {innovation.get('id')}: {e}")
                    continue
            
            logger.info(f"Uploaded {len(innovations)} innovations to assistant")
        
        logger.info(f"Assistant data upload job completed: {uploaded_count} documents uploaded")
        
    except Exception as e:
        logger.error(f"Assistant data upload job failed: {e}")
        

# Example usage in comments:
"""
# Initialize assistant
curl -X POST "http://localhost:8000/api/ai-assistant/initialize"

# Upload data
curl -X POST "http://localhost:8000/api/ai-assistant/upload-data?data_type=all&limit=100"

# Chat with assistant
curl -X POST "http://localhost:8000/api/ai-assistant/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the top AI research trends in Africa?"}'

# Get domain insights
curl "http://localhost:8000/api/ai-assistant/insights/healthcare"

# Ask about ecosystem
curl -X POST "http://localhost:8000/api/ai-assistant/ask-ecosystem" \
  -H "Content-Type: application/json" \
  -d '{"message": "Which African universities are leading in AI research?"}'

# Check status
curl "http://localhost:8000/api/ai-assistant/status"
"""