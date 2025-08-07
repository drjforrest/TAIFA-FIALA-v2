"""
Pinecone Assistant Service for TAIFA-FIALA
Advanced RAG capabilities using Pinecone Assistant API for intelligent document processing
"""

import asyncio
import tempfile
import os
from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path
from uuid import uuid4

from pinecone import Pinecone
from loguru import logger

from config.settings import settings


class PineconeAssistantService:
    """Service for advanced document processing using Pinecone Assistant"""
    
    def __init__(self):
        self.pc = None
        self.assistant = None
        self.assistant_name = "ai-innovations"  # Your assistant name
        
    async def initialize(self):
        """Initialize Pinecone Assistant"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Get assistant instance
            self.assistant = self.pc.assistant.Assistant(
                assistant_name=self.assistant_name
            )
            
            logger.info(f"Pinecone Assistant '{self.assistant_name}' initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone Assistant: {e}")
            return False
    
    async def upload_file(self, file_path: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Upload a file to the assistant for processing"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logger.info(f"Uploading file to Pinecone Assistant: {file_path}")
            
            response = self.assistant.upload_file(
                file_path=file_path,
                timeout=timeout
            )
            
            logger.info(f"File uploaded successfully: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error uploading file to assistant: {e}")
            return {"error": str(e)}
    
    async def upload_text_content(self, content: str, filename: str = None) -> Dict[str, Any]:
        """Upload text content as a temporary file to the assistant"""
        try:
            # Create temporary file
            if not filename:
                filename = f"content_{uuid4().hex[:8]}.txt"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                # Upload the temporary file
                response = await self.upload_file(tmp_file_path)
                return response
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            logger.error(f"Error uploading text content: {e}")
            return {"error": str(e)}
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message to the assistant"""
        try:
            # Modern Pinecone API uses simple message format
            msg = {"role": "user", "content": message}
            
            response = self.assistant.chat(messages=[msg])
            
            return {
                "message": response.get("message", {}).get("content", ""),
                "conversation_id": conversation_id,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error in assistant chat: {e}")
            return {"error": str(e)}
    
    async def chat_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Send a chat message with streaming response"""
        try:
            # Modern Pinecone API uses simple message format
            msg = {"role": "user", "content": message}
            
            chunks = self.assistant.chat(messages=[msg], stream=True)
            
            for chunk in chunks:
                if chunk:
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"Error: {str(e)}"
    
    async def upload_publication_content(self, publication: Dict[str, Any]) -> Dict[str, Any]:
        """Upload publication content for RAG processing"""
        try:
            # Format publication content
            content = self._format_publication_content(publication)
            
            filename = f"pub_{publication.get('id', uuid4().hex[:8])}.txt"
            
            return await self.upload_text_content(content, filename)
            
        except Exception as e:
            logger.error(f"Error uploading publication: {e}")
            return {"error": str(e)}
    
    async def upload_innovation_content(self, innovation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload innovation content for RAG processing"""
        try:
            # Format innovation content
            content = self._format_innovation_content(innovation)
            
            filename = f"innovation_{innovation.get('id', uuid4().hex[:8])}.txt"
            
            return await self.upload_text_content(content, filename)
            
        except Exception as e:
            logger.error(f"Error uploading innovation: {e}")
            return {"error": str(e)}
    
    def _format_publication_content(self, publication: Dict[str, Any]) -> str:
        """Format publication data for assistant processing"""
        content_parts = []
        
        # Title
        if publication.get('title'):
            content_parts.append(f"TITLE: {publication['title']}")
        
        # Authors
        if publication.get('authors'):
            authors = publication['authors']
            if isinstance(authors, list):
                content_parts.append(f"AUTHORS: {', '.join(authors)}")
            else:
                content_parts.append(f"AUTHORS: {authors}")
        
        # Abstract
        if publication.get('abstract'):
            content_parts.append(f"ABSTRACT: {publication['abstract']}")
        
        # Content
        if publication.get('content'):
            content_parts.append(f"CONTENT: {publication['content']}")
        
        # Keywords
        if publication.get('keywords'):
            keywords = publication['keywords']
            if isinstance(keywords, list):
                content_parts.append(f"KEYWORDS: {', '.join(keywords)}")
        
        # African entities
        if publication.get('african_entities'):
            entities = publication['african_entities']
            if isinstance(entities, list):
                content_parts.append(f"AFRICAN_ENTITIES: {', '.join(entities)}")
        
        # Publication date
        if publication.get('publication_date'):
            content_parts.append(f"PUBLICATION_DATE: {publication['publication_date']}")
        
        # DOI
        if publication.get('doi'):
            content_parts.append(f"DOI: {publication['doi']}")
        
        # Source URL
        if publication.get('source_url'):
            content_parts.append(f"SOURCE_URL: {publication['source_url']}")
        
        # Enhanced metadata (if available)
        if publication.get('development_stage'):
            content_parts.append(f"DEVELOPMENT_STAGE: {publication['development_stage']}")
        
        if publication.get('business_model'):
            content_parts.append(f"BUSINESS_MODEL: {publication['business_model']}")
        
        if publication.get('target_markets'):
            markets = publication['target_markets']
            if isinstance(markets, list):
                content_parts.append(f"TARGET_MARKETS: {', '.join(markets)}")
        
        if publication.get('extracted_technologies'):
            technologies = publication['extracted_technologies']
            if isinstance(technologies, list):
                tech_names = [tech.get('technology', '') for tech in technologies if isinstance(tech, dict)]
                if tech_names:
                    content_parts.append(f"TECHNOLOGIES: {', '.join(tech_names)}")
        
        return "\n\n".join(content_parts)
    
    def _format_innovation_content(self, innovation: Dict[str, Any]) -> str:
        """Format innovation data for assistant processing"""
        content_parts = []
        
        # Title
        if innovation.get('title'):
            content_parts.append(f"INNOVATION_TITLE: {innovation['title']}")
        
        # Description
        if innovation.get('description'):
            content_parts.append(f"DESCRIPTION: {innovation['description']}")
        
        # Innovation type
        if innovation.get('innovation_type'):
            content_parts.append(f"TYPE: {innovation['innovation_type']}")
        
        # Country
        if innovation.get('country'):
            content_parts.append(f"COUNTRY: {innovation['country']}")
        
        # Problem solved
        if innovation.get('problem_solved'):
            content_parts.append(f"PROBLEM_SOLVED: {innovation['problem_solved']}")
        
        # Solution approach
        if innovation.get('solution_approach'):
            content_parts.append(f"SOLUTION_APPROACH: {innovation['solution_approach']}")
        
        # Tech stack
        if innovation.get('tech_stack'):
            tech_stack = innovation['tech_stack']
            if isinstance(tech_stack, list):
                content_parts.append(f"TECH_STACK: {', '.join(tech_stack)}")
            else:
                content_parts.append(f"TECH_STACK: {tech_stack}")
        
        # Tags
        if innovation.get('tags'):
            tags = innovation['tags']
            if isinstance(tags, list):
                content_parts.append(f"TAGS: {', '.join(tags)}")
        
        # Organizations
        if innovation.get('organizations'):
            orgs = innovation['organizations']
            if isinstance(orgs, list):
                org_names = [org.get('name', '') for org in orgs if isinstance(org, dict)]
                if org_names:
                    content_parts.append(f"ORGANIZATIONS: {', '.join(org_names)}")
        
        # Individuals
        if innovation.get('individuals'):
            individuals = innovation['individuals']
            if isinstance(individuals, list):
                names = [ind.get('name', '') for ind in individuals if isinstance(ind, dict)]
                if names:
                    content_parts.append(f"TEAM_MEMBERS: {', '.join(names)}")
        
        # Fundings
        if innovation.get('fundings'):
            fundings = innovation['fundings']
            if isinstance(fundings, list):
                funding_info = []
                for funding in fundings:
                    if isinstance(funding, dict):
                        amount = funding.get('amount')
                        funder = funding.get('funder_name', '')
                        if amount and funder:
                            funding_info.append(f"{funder}: {amount}")
                if funding_info:
                    content_parts.append(f"FUNDING: {', '.join(funding_info)}")
        
        # Impact metrics
        if innovation.get('impact_metrics'):
            metrics = innovation['impact_metrics']
            if isinstance(metrics, dict):
                metric_strs = []
                for key, value in metrics.items():
                    metric_strs.append(f"{key}: {value}")
                if metric_strs:
                    content_parts.append(f"IMPACT_METRICS: {', '.join(metric_strs)}")
        
        # URLs
        if innovation.get('website_url'):
            content_parts.append(f"WEBSITE: {innovation['website_url']}")
        
        if innovation.get('github_url'):
            content_parts.append(f"GITHUB: {innovation['github_url']}")
        
        if innovation.get('demo_url'):
            content_parts.append(f"DEMO: {innovation['demo_url']}")
        
        # Creation date
        if innovation.get('creation_date'):
            content_parts.append(f"CREATION_DATE: {innovation['creation_date']}")
        
        # Verification status
        if innovation.get('verification_status'):
            content_parts.append(f"VERIFICATION_STATUS: {innovation['verification_status']}")
        
        return "\n\n".join(content_parts)
    
    async def enhance_message_with_innovation_context(self, message: str, innovation: Dict[str, Any]) -> str:
        """Enhance user message with specific innovation context for focused RAG retrieval"""
        try:
            # Create a comprehensive context about the specific innovation
            innovation_context = f"""
INNOVATION CONTEXT (Priority Document):
Innovation: {innovation.get('title', 'Unknown')}
ID: {innovation.get('id', '')}
Description: {innovation.get('description', 'No description available')}
Type: {innovation.get('innovation_type', 'Unknown')}
Country: {innovation.get('country', 'Unknown')}
Development Stage: {innovation.get('development_stage', 'Unknown')}

"""
            
            # Add related organizations context if available
            if innovation.get('related_organizations'):
                org_names = [org.get('name', '') for org in innovation['related_organizations']]
                innovation_context += f"Related Organizations: {', '.join(org_names)}\n"
            
            # Add funding context if available
            if innovation.get('fundings'):
                funding_info = []
                for funding in innovation['fundings']:
                    amount = funding.get('amount', 0)
                    funder = funding.get('funder_name', 'Unknown')
                    if amount > 0:
                        funding_info.append(f"{funder}: ${amount:,}")
                if funding_info:
                    innovation_context += f"Funding: {', '.join(funding_info)}\n"
            
            # Add related publications context if available
            if innovation.get('related_publications'):
                pub_titles = [pub.get('title', '')[:100] for pub in innovation['related_publications']]
                innovation_context += f"Related Publications: {'; '.join(pub_titles)}\n"
            
            enhanced_message = f"""
{innovation_context}

SPECIFIC QUESTION ABOUT THIS INNOVATION:
{message}

Please focus your response on the specific innovation mentioned above. Use the uploaded data to provide detailed insights about this particular innovation, including:
- Technical details and implementation approaches
- Market positioning and competitive landscape
- Funding history and investment attractiveness  
- Team and organizational relationships
- Related research and academic connections
- Impact metrics and success indicators
- Similar innovations in the ecosystem

If you reference other innovations or research, please explain how they relate to this specific innovation.
"""
            
            return enhanced_message
            
        except Exception as e:
            logger.error(f"Error enhancing message with innovation context: {e}")
            return message  # Fallback to original message
    
    async def ask_about_african_ai_ecosystem(self, question: str) -> Dict[str, Any]:
        """Ask questions about the African AI ecosystem using uploaded data"""
        try:
            # Enhance the question with context
            enhanced_question = f"""
            Based on the uploaded African AI research publications and innovations data, please answer this question:
            
            {question}
            
            Please provide specific examples from the data when possible, including:
            - Specific publications, innovations, or researchers mentioned
            - Countries, institutions, or organizations involved  
            - Technologies, methodologies, or approaches used
            - Dates, funding amounts, or other quantitative details
            - Connections or patterns you observe in the data
            
            If you don't have sufficient data to answer completely, please indicate what additional information would be helpful.
            """
            
            return await self.chat(enhanced_question)
            
        except Exception as e:
            logger.error(f"Error asking about ecosystem: {e}")
            return {"error": str(e)}
    
    async def get_research_insights(self, domain: str = "artificial intelligence") -> Dict[str, Any]:
        """Get research insights for a specific domain"""
        try:
            question = f"""
            Analyze the African {domain} research landscape based on the uploaded data. Please provide insights on:
            
            1. Key research trends and themes
            2. Leading researchers and institutions
            3. Most innovative approaches or technologies
            4. Collaboration patterns between countries/institutions
            5. Commercial applications and market readiness
            6. Gaps or opportunities for future research
            7. Funding patterns and investment trends
            
            Please cite specific examples from the data and provide quantitative insights where available.
            """
            
            return await self.ask_about_african_ai_ecosystem(question)
            
        except Exception as e:
            logger.error(f"Error getting research insights: {e}")
            return {"error": str(e)}


# Global service instance
pinecone_assistant_service = PineconeAssistantService()