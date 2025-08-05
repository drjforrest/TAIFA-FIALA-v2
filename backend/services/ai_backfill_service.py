"""
AI-Powered Backfilling Service for TAIFA-FIALA
==============================================

Double-hit team approach for enriching innovation records with missing properties:
1. Perplexity query for comprehensive data gathering
2. OpenAI parsing and structuring into database format
3. Serper.dev targeted searches for specific missing values

This service runs scheduled jobs to backfill missing data for existing innovations.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import openai
from loguru import logger

from config.settings import settings
from services.serper_service import SerperService
from etl.intelligence.perplexity_african_ai import PerplexityAfricanAIModule


class BackfillPriority(Enum):
    """Priority levels for backfill operations"""
    CRITICAL = "critical"  # Missing funding, basic company info
    HIGH = "high"  # Missing contact info, key team members
    MEDIUM = "medium"  # Missing social media, detailed metrics
    LOW = "low"  # Missing nice-to-have information


class BackfillStatus(Enum):
    """Status of backfill operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class MissingField:
    """Represents a missing field that needs backfilling"""
    field_name: str
    field_type: str  # 'funding', 'contact', 'team', 'metrics', 'urls'
    priority: BackfillPriority
    search_strategy: str  # 'perplexity', 'serper', 'combined'
    estimated_cost: float  # API cost estimate
    

@dataclass
class BackfillJob:
    """Represents a backfill job for an innovation"""
    job_id: str
    innovation_id: str
    innovation_title: str
    innovation_description: str
    missing_fields: List[MissingField]
    status: BackfillStatus
    priority: BackfillPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    results: Dict[str, Any] = None
    error_message: Optional[str] = None


@dataclass
class BackfillResult:
    """Result of a backfill operation"""
    innovation_id: str
    field_name: str
    old_value: Any
    new_value: Any
    confidence_score: float
    data_source: str  # 'perplexity', 'serper', 'openai_parsed'
    validation_status: str  # 'validated', 'needs_review', 'low_confidence'
    cost: float


class AIBackfillService:
    """AI-powered service for backfilling missing innovation properties"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.perplexity_key = settings.PERPLEXITY_API_KEY
        self.serper_key = settings.SERPER_API_KEY
        
        # Cost tracking
        self.daily_cost_limit = 50.0  # $50 per day
        self.current_daily_cost = 0.0
        self.last_cost_reset = datetime.now().date()
        
        # Job queue
        self.job_queue: List[BackfillJob] = []
        
    async def analyze_missing_fields(self, innovation: Dict[str, Any]) -> List[MissingField]:
        """Analyze an innovation record to identify missing fields"""
        
        missing_fields = []
        
        # Critical missing fields
        if not innovation.get('fundings') or len(innovation.get('fundings', [])) == 0:
            missing_fields.append(MissingField(
                field_name='funding_amount',
                field_type='funding',
                priority=BackfillPriority.CRITICAL,
                search_strategy='perplexity',
                estimated_cost=0.10
            ))
        
        if not innovation.get('website_url'):
            missing_fields.append(MissingField(
                field_name='website_url',
                field_type='urls',
                priority=BackfillPriority.CRITICAL,
                search_strategy='serper',
                estimated_cost=0.05
            ))
        
        # High priority missing fields
        if not innovation.get('organizations') or len(innovation.get('organizations', [])) == 0:
            missing_fields.append(MissingField(
                field_name='founding_organization',
                field_type='contact',
                priority=BackfillPriority.HIGH,
                search_strategy='combined',
                estimated_cost=0.15
            ))
        
        if not innovation.get('individuals') or len(innovation.get('individuals', [])) == 0:
            missing_fields.append(MissingField(
                field_name='key_team_members',
                field_type='team',
                priority=BackfillPriority.HIGH,
                search_strategy='perplexity',
                estimated_cost=0.08
            ))
        
        # Medium priority missing fields
        if not innovation.get('github_url'):
            missing_fields.append(MissingField(
                field_name='github_url',
                field_type='urls',
                priority=BackfillPriority.MEDIUM,
                search_strategy='serper',
                estimated_cost=0.03
            ))
        
        if not innovation.get('impact_metrics') or not innovation.get('impact_metrics', {}).get('users_reached'):
            missing_fields.append(MissingField(
                field_name='user_metrics',
                field_type='metrics',
                priority=BackfillPriority.MEDIUM,
                search_strategy='perplexity',
                estimated_cost=0.07
            ))
        
        # Low priority missing fields
        if not innovation.get('demo_url'):
            missing_fields.append(MissingField(
                field_name='demo_url',
                field_type='urls',
                priority=BackfillPriority.LOW,
                search_strategy='serper',
                estimated_cost=0.02
            ))
        
        logger.info(f"Found {len(missing_fields)} missing fields for innovation {innovation.get('id')}")
        return missing_fields
    
    async def create_backfill_job(self, innovation: Dict[str, Any]) -> BackfillJob:
        """Create a backfill job for an innovation"""
        
        missing_fields = await self.analyze_missing_fields(innovation)
        
        if not missing_fields:
            logger.info(f"No missing fields found for innovation {innovation.get('id')}")
            return None
        
        # Determine overall priority
        priorities = [field.priority for field in missing_fields]
        overall_priority = min(priorities)  # Highest priority (CRITICAL = lowest enum value)
        
        job = BackfillJob(
            job_id=f"backfill_{innovation.get('id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            innovation_id=innovation.get('id'),
            innovation_title=innovation.get('title', ''),
            innovation_description=innovation.get('description', ''),
            missing_fields=missing_fields,
            status=BackfillStatus.PENDING,
            priority=overall_priority,
            created_at=datetime.now(),
            results={}
        )
        
        self.job_queue.append(job)
        logger.info(f"Created backfill job {job.job_id} with {len(missing_fields)} tasks")
        return job
    
    async def process_backfill_job(self, job: BackfillJob) -> BackfillJob:
        """Process a single backfill job using the double-hit approach"""
        
        logger.info(f"Starting backfill job {job.job_id}")
        job.status = BackfillStatus.IN_PROGRESS
        job.started_at = datetime.now()
        
        try:
            # Reset daily cost if needed
            self._check_daily_cost_reset()
            
            # Check daily cost limit
            estimated_total_cost = sum(field.estimated_cost for field in job.missing_fields)
            if self.current_daily_cost + estimated_total_cost > self.daily_cost_limit:
                logger.warning(f"Daily cost limit would be exceeded. Skipping job {job.job_id}")
                job.status = BackfillStatus.SKIPPED
                job.error_message = "Daily cost limit would be exceeded"
                return job
            
            # Process each missing field
            job.results = {}
            total_cost = 0.0
            
            for field in job.missing_fields:
                try:
                    logger.info(f"Processing field {field.field_name} using {field.search_strategy}")
                    
                    if field.search_strategy == 'perplexity':
                        result = await self._backfill_with_perplexity(job, field)
                    elif field.search_strategy == 'serper':
                        result = await self._backfill_with_serper(job, field)
                    elif field.search_strategy == 'combined':
                        result = await self._backfill_with_combined_approach(job, field)
                    else:
                        logger.warning(f"Unknown search strategy: {field.search_strategy}")
                        continue
                    
                    if result:
                        job.results[field.field_name] = result
                        total_cost += result.cost
                        logger.info(f"Successfully backfilled {field.field_name} with confidence {result.confidence_score:.2f}")
                    
                    # Rate limiting between field processing
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing field {field.field_name}: {e}")
                    job.results[field.field_name] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            
            job.total_cost = total_cost
            self.current_daily_cost += total_cost
            job.status = BackfillStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(f"Completed backfill job {job.job_id} with cost ${total_cost:.3f}")
            
        except Exception as e:
            logger.error(f"Error processing backfill job {job.job_id}: {e}")
            job.status = BackfillStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
        
        return job
    
    async def _backfill_with_perplexity(self, job: BackfillJob, field: MissingField) -> Optional[BackfillResult]:
        """First hit: Use Perplexity to gather comprehensive data"""
        
        # Craft targeted prompt based on field type
        prompt = self._create_perplexity_prompt(job, field)
        
        try:
            async with PerplexityAfricanAIModule(self.perplexity_key) as perplexity:
                # Call Perplexity API
                response = await perplexity._call_perplexity_api(prompt)
                raw_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                if not raw_content:
                    return None
                
                # Second hit: Use OpenAI to parse and structure the response
                structured_data = await self._parse_with_openai(raw_content, field)
                
                if structured_data:
                    return BackfillResult(
                        innovation_id=job.innovation_id,
                        field_name=field.field_name,
                        old_value=None,
                        new_value=structured_data.get('value'),
                        confidence_score=structured_data.get('confidence', 0.5),
                        data_source='perplexity_openai',
                        validation_status=self._determine_validation_status(structured_data.get('confidence', 0.5)),
                        cost=field.estimated_cost
                    )
        
        except Exception as e:
            logger.error(f"Error in Perplexity backfill for {field.field_name}: {e}")
            return None
    
    async def _backfill_with_serper(self, job: BackfillJob, field: MissingField) -> Optional[BackfillResult]:
        """Use Serper.dev for targeted search of specific missing values"""
        
        # Create targeted search query
        search_query = self._create_serper_query(job, field)
        
        try:
            async with SerperService() as serper:
                # Perform targeted search
                search_results = await serper.search_web(search_query, num_results=10)
                
                if not search_results.results:
                    return None
                
                # Extract value from search results using pattern matching
                extracted_value = await self._extract_value_from_search_results(
                    search_results.results, field
                )
                
                if extracted_value:
                    return BackfillResult(
                        innovation_id=job.innovation_id,
                        field_name=field.field_name,
                        old_value=None,
                        new_value=extracted_value.get('value'),
                        confidence_score=extracted_value.get('confidence', 0.6),
                        data_source='serper',
                        validation_status=self._determine_validation_status(extracted_value.get('confidence', 0.6)),
                        cost=field.estimated_cost
                    )
        
        except Exception as e:
            logger.error(f"Error in Serper backfill for {field.field_name}: {e}")
            return None
    
    async def _backfill_with_combined_approach(self, job: BackfillJob, field: MissingField) -> Optional[BackfillResult]:
        """Use both Perplexity and Serper for comprehensive backfilling"""
        
        # Try Perplexity first
        perplexity_result = await self._backfill_with_perplexity(job, field)
        
        # Try Serper as well
        serper_result = await self._backfill_with_serper(job, field)
        
        # Combine and validate results
        if perplexity_result and serper_result:
            # Both sources agree or complement each other
            combined_confidence = (perplexity_result.confidence_score + serper_result.confidence_score) / 2
            
            return BackfillResult(
                innovation_id=job.innovation_id,
                field_name=field.field_name,
                old_value=None,
                new_value={
                    'perplexity_data': perplexity_result.new_value,
                    'serper_data': serper_result.new_value,
                    'combined_confidence': combined_confidence
                },
                confidence_score=combined_confidence,
                data_source='combined',
                validation_status=self._determine_validation_status(combined_confidence),
                cost=field.estimated_cost
            )
        
        # Return the better result if only one succeeded
        if perplexity_result and perplexity_result.confidence_score >= 0.6:
            return perplexity_result
        elif serper_result and serper_result.confidence_score >= 0.6:
            return serper_result
        
        return None
    
    def _create_perplexity_prompt(self, job: BackfillJob, field: MissingField) -> str:
        """Create targeted Perplexity prompt based on field type"""
        
        base_context = f"""
        Please share data publicly available on the AI innovation "{job.innovation_title}".
        
        Innovation Description: {job.innovation_description}
        
        I specifically need information about: {field.field_name}
        """
        
        if field.field_type == 'funding':
            return base_context + """
            
            Please focus on:
            - Funding amounts raised (with currency)
            - Investment rounds (seed, Series A, B, etc.)
            - Investor names and organizations
            - Funding dates and announcements
            - Valuation information if available
            
            Provide specific, verifiable details with sources when possible.
            """
        
        elif field.field_type == 'contact':
            return base_context + """
            
            Please focus on:
            - Company/organization name and official details
            - Founding team and key personnel
            - Official contact information
            - Company registration details
            - Location and headquarters information
            
            Provide verified, publicly available information only.
            """
        
        elif field.field_type == 'team':
            return base_context + """
            
            Please focus on:
            - Founders and co-founders
            - Key team members and their roles
            - Leadership team information
            - Technical team leads
            - Advisory board members
            
            Include names, titles, and background information when available.
            """
        
        elif field.field_type == 'urls':
            return base_context + """
            
            Please focus on finding:
            - Official website URL
            - GitHub repository links
            - Demo or product URLs
            - Social media profiles
            - App store links
            
            Verify that URLs are current and accessible.
            """
        
        elif field.field_type == 'metrics':
            return base_context + """
            
            Please focus on:
            - User metrics (active users, downloads, etc.)
            - Revenue information if publicly disclosed
            - Growth metrics and milestones
            - Market traction indicators
            - Impact metrics and social outcomes
            
            Provide quantifiable data with sources when possible.
            """
        
        return base_context + f"\nPlease provide detailed, factual information about {field.field_name}."
    
    def _create_serper_query(self, job: BackfillJob, field: MissingField) -> str:
        """Create targeted Serper search query"""
        
        innovation_name = job.innovation_title
        
        if field.field_type == 'funding':
            return f'"{innovation_name}" AND (funding OR investment OR "raised" OR "million" OR "series")'
        
        elif field.field_type == 'urls':
            if field.field_name == 'website_url':
                return f'"{innovation_name}" AND (website OR "official site" OR domain)'
            elif field.field_name == 'github_url':
                return f'"{innovation_name}" AND (github OR repository OR "open source")'
            elif field.field_name == 'demo_url':
                return f'"{innovation_name}" AND (demo OR "try it" OR "live app")'
        
        elif field.field_type == 'contact':
            return f'"{innovation_name}" AND (company OR organization OR founded OR headquarters)'
        
        elif field.field_type == 'team':
            return f'"{innovation_name}" AND (founder OR "founded by" OR team OR CEO)'
        
        elif field.field_type == 'metrics':
            return f'"{innovation_name}" AND (users OR customers OR downloads OR revenue)'
        
        return f'"{innovation_name}" {field.field_name}'
    
    async def _parse_with_openai(self, raw_content: str, field: MissingField) -> Optional[Dict[str, Any]]:
        """Second hit: Use OpenAI to parse Perplexity output into structured JSON"""
        
        parsing_prompt = f"""
        Parse the following content and extract structured information for the field "{field.field_name}" of type "{field.field_type}".
        
        Content to parse:
        {raw_content}
        
        Please extract and structure the information into JSON format with the following structure:
        {{
            "value": "extracted value or structured data",
            "confidence": 0.0-1.0,
            "supporting_evidence": ["evidence1", "evidence2"],
            "source_reliability": "high|medium|low",
            "verification_notes": "any notes about verification"
        }}
        
        Focus on accuracy and provide confidence scores based on the quality of evidence found.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Extract structured information accurately and provide confidence scores."},
                    {"role": "user", "content": parsing_prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            if content:
                return json.loads(content)
        
        except Exception as e:
            logger.error(f"Error parsing with OpenAI: {e}")
            return None
    
    async def _extract_value_from_search_results(self, search_results: List, field: MissingField) -> Optional[Dict[str, Any]]:
        """Extract specific values from Serper search results using pattern matching"""
        
        combined_text = " ".join([f"{result.title} {result.snippet}" for result in search_results[:5]])
        
        if field.field_type == 'funding':
            return self._extract_funding_patterns(combined_text)
        elif field.field_type == 'urls':
            return self._extract_url_patterns(combined_text, field.field_name)
        elif field.field_type == 'contact':
            return self._extract_contact_patterns(combined_text)
        
        return None
    
    def _extract_funding_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract funding information using regex patterns"""
        
        funding_patterns = [
            r'raised\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'funding\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)',
            r'\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)\s+in\s+funding',
            r'series\s+[A-Z]\s+of\s+\$?(\d+(?:\.\d+)?)\s*(million|billion|M|B)'
        ]
        
        for pattern in funding_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to USD
                if unit in ['billion', 'b']:
                    amount *= 1000000000
                elif unit in ['million', 'm']:
                    amount *= 1000000
                
                return {
                    'value': {
                        'amount': amount,
                        'currency': 'USD',
                        'raw_text': match.group()
                    },
                    'confidence': 0.8
                }
        
        return None
    
    def _extract_url_patterns(self, text: str, field_name: str) -> Optional[Dict[str, Any]]:
        """Extract URL patterns from text"""
        
        if field_name == 'website_url':
            # Look for website URLs
            url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            matches = re.findall(url_pattern, text)
            
            if matches:
                # Return the most likely website (shortest domain name)
                best_match = min(matches, key=len)
                return {
                    'value': f"https://{best_match}",
                    'confidence': 0.7
                }
        
        elif field_name == 'github_url':
            # Look for GitHub URLs
            github_pattern = r'github\.com/([a-zA-Z0-9.-]+/[a-zA-Z0-9.-]+)'
            match = re.search(github_pattern, text)
            
            if match:
                return {
                    'value': f"https://github.com/{match.group(1)}",
                    'confidence': 0.9
                }
        
        return None
    
    def _extract_contact_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract contact/organization patterns"""
        
        # Look for company name patterns
        company_patterns = [
            r'company\s+([A-Z][a-zA-Z\s]+)',
            r'startup\s+([A-Z][a-zA-Z\s]+)',
            r'founded\s+([A-Z][a-zA-Z\s]+)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'value': match.group(1).strip(),
                    'confidence': 0.6
                }
        
        return None
    
    def _determine_validation_status(self, confidence_score: float) -> str:
        """Determine validation status based on confidence score"""
        
        if confidence_score >= 0.8:
            return 'validated'
        elif confidence_score >= 0.6:
            return 'needs_review'
        else:
            return 'low_confidence'
    
    def _check_daily_cost_reset(self):
        """Reset daily cost tracking if it's a new day"""
        
        today = datetime.now().date()
        if today > self.last_cost_reset:
            self.current_daily_cost = 0.0
            self.last_cost_reset = today
            logger.info(f"Reset daily cost tracking for {today}")
    
    async def run_scheduled_backfill(self, max_jobs: int = 10) -> List[BackfillJob]:
        """Run scheduled backfill jobs"""
        
        logger.info(f"Starting scheduled backfill run (max {max_jobs} jobs)")
        
        # Sort jobs by priority
        self.job_queue.sort(key=lambda job: (job.priority.value, job.created_at))
        
        # Process jobs
        completed_jobs = []
        jobs_to_process = self.job_queue[:max_jobs]
        
        for job in jobs_to_process:
            if job.status == BackfillStatus.PENDING:
                try:
                    completed_job = await self.process_backfill_job(job)
                    completed_jobs.append(completed_job)
                    
                    # Remove from queue if completed or failed
                    if completed_job.status in [BackfillStatus.COMPLETED, BackfillStatus.FAILED, BackfillStatus.SKIPPED]:
                        self.job_queue.remove(job)
                
                except Exception as e:
                    logger.error(f"Error processing job {job.job_id}: {e}")
                    job.status = BackfillStatus.FAILED
                    job.error_message = str(e)
        
        logger.info(f"Completed {len(completed_jobs)} backfill jobs")
        return completed_jobs
    
    def get_backfill_stats(self) -> Dict[str, Any]:
        """Get backfill service statistics"""
        
        total_jobs = len(self.job_queue)
        pending_jobs = len([job for job in self.job_queue if job.status == BackfillStatus.PENDING])
        completed_jobs = len([job for job in self.job_queue if job.status == BackfillStatus.COMPLETED])
        
        return {
            'total_jobs': total_jobs,
            'pending_jobs': pending_jobs,
            'completed_jobs': completed_jobs,
            'current_daily_cost': self.current_daily_cost,
            'daily_cost_limit': self.daily_cost_limit,
            'cost_utilization': (self.current_daily_cost / self.daily_cost_limit) * 100,
            'last_cost_reset': self.last_cost_reset.isoformat()
        }


# Global service instance
ai_backfill_service = AIBackfillService()


# Convenience functions for use in ETL pipeline
async def create_backfill_jobs_for_innovations(innovations: List[Dict[str, Any]]) -> List[BackfillJob]:
    """Create backfill jobs for a list of innovations"""
    
    jobs = []
    for innovation in innovations:
        job = await ai_backfill_service.create_backfill_job(innovation)
        if job:
            jobs.append(job)
    
    return jobs


async def run_backfill_batch(max_jobs: int = 10) -> List[BackfillJob]:
    """Run a batch of backfill jobs"""
    
    return await ai_backfill_service.run_scheduled_backfill(max_jobs)


if __name__ == "__main__":
    # Test the backfill service
    async def test_backfill():
        print("🤖 Testing AI Backfill Service")
        
        # Mock innovation with missing fields
        test_innovation = {
            'id': 'test-123',
            'title': 'Flutterwave',
            'description': 'African fintech company providing payment infrastructure',
            'innovation_type': 'FinTech',
            'fundings': [],  # Missing funding info
            'website_url': None,  # Missing website
            'organizations': [],  # Missing organization info
        }
        
        # Create backfill job
        job = await ai_backfill_service.create_backfill_job(test_innovation)
        
        if job:
            print(f"Created job: {job.job_id}")
            print(f"Missing fields: {len(job.missing_fields)}")
            
            # Process the job (this would use real APIs in production)
            # processed_job = await ai_backfill_service.process_backfill_job(job)
            print(f"Job priority: {job.priority.value}")
        
        # Show stats
        stats = ai_backfill_service.get_backfill_stats()
        print(f"Service stats: {stats}")
    
    asyncio.run(test_backfill())