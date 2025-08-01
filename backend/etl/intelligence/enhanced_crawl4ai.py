"""
TAIFA-FIALA Enhanced Crawl4AI Integration
========================================

Intelligent web scraping orchestrator for African AI innovation discovery.
Uses Crawl4AI with LLM-powered extraction for comprehensive data collection.
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    STARTUP_PROFILE = "startup_profile"
    GITHUB_REPOSITORY = "github_repository"
    RESEARCH_PAPER = "research_paper"
    NEWS_ARTICLE = "news_article"
    FUNDING_ANNOUNCEMENT = "funding_announcement"
    ACADEMIC_PROFILE = "academic_profile"
    COMPANY_WEBSITE = "company_website"
    POLICY_DOCUMENT = "policy_document"


@dataclass
class InnovationExtractionResult:
    """Comprehensive extraction result for African AI innovations"""

    # Basic metadata
    url: str
    content_type: ContentType
    extraction_timestamp: datetime
    success: bool = False

    # Core innovation information
    title: Optional[str] = None
    description: Optional[str] = None
    innovation_type: Optional[str] = None
    problem_solved: Optional[str] = None

    # Technical details
    technical_approach: Optional[str] = None
    development_stage: Optional[str] = None
    technical_stack: Optional[List[str]] = None
    computational_requirements: Optional[Dict[str, Any]] = None
    datasets_used: Optional[List[str]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

    # Team and organization
    creators: Optional[List[Dict[str, str]]] = None
    organization_affiliation: Optional[str] = None
    location: Optional[str] = None
    contact_information: Optional[Dict[str, Any]] = None

    # Impact and adoption
    use_cases: Optional[List[str]] = None
    user_adoption_metrics: Optional[Dict[str, Any]] = None
    social_impact: Optional[str] = None

    # Recognition and validation
    recognition: Optional[List[str]] = None
    media_coverage: Optional[List[str]] = None
    research_citations: Optional[List[str]] = None

    # Business and funding
    funding_sources: Optional[List[Dict[str, Any]]] = None
    funding_amounts: Optional[List[str]] = None
    business_model: Optional[str] = None
    revenue_model: Optional[str] = None

    # Metadata and quality scores
    data_completeness_score: float = 0.0
    confidence_score: float = 0.0
    validation_flags: Optional[List[str]] = None
    source_links: Optional[List[str]] = None
    structured_data: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Convert to JSON string"""
        data = asdict(self)
        data['extraction_timestamp'] = self.extraction_timestamp.isoformat()
        data['content_type'] = self.content_type.value
        return json.dumps(data, indent=2, default=str)

    def save_extraction(self, filepath: str):
        """Save to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())


class IntelligentCrawl4AIOrchestrator:
    """Advanced web crawler with AI-powered extraction for African AI innovations"""

    def __init__(self, llm_api_key: Optional[str] = None):
        self.llm_api_key = llm_api_key
        self.crawler: Optional[AsyncWebCrawler] = None

        # Validation patterns for African AI content
        self.validation_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'funding_amount': r'\$\d+(?:\.\d+)?\s*(?:million|billion|M|B)',
            'github_repo': r'github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',
            'linkedin_profile': r'linkedin\.com/in/[A-Za-z0-9_.-]+',
            'african_location': r'\b(?:Nigeria|Kenya|South Africa|Ghana|Egypt|Morocco|Rwanda|Uganda|Tanzania|Senegal|Ivory Coast|Algeria|Tunisia|Zimbabwe|Botswana|Namibia|Zambia|Malawi|Mozambique|Madagascar|Mauritius|Ethiopia|Sudan|Chad|Niger|Mali|Burkina Faso|Guinea|Sierra Leone|Liberia|Togo|Benin|Cameroon|Central African Republic|Democratic Republic of Congo|Republic of Congo|Gabon|Equatorial Guinea|São Tomé and Príncipe|Cape Verde|Gambia|Guinea-Bissau|Comoros|Seychelles|Djibouti|Eritrea|Somalia|Angola|Lesotho|Eswatini|Burundi|South Sudan|Lagos|Nairobi|Cape Town|Cairo|Casablanca|Kigali|Kampala|Accra|Dakar|Abidjan|Tunis|Algiers|Addis Ababa|Johannesburg|Durban|Pretoria|Alexandria|Giza|Rabat|Marrakech|Fez|Dar es Salaam|Mombasa|Kisumu|Ibadan|Kano|Port Harcourt|Abuja|Kumasi|Tamale|Lusaka|Harare|Bulawayo|Windhoek|Gaborone|Maputo|Antananarivo|Port Louis)\b',
        }

    async def __aenter__(self):
        self.crawler = AsyncWebCrawler(verbose=True)
        await self.crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)

    async def extract_innovation_data(self,
                                    url: str,
                                    content_type: ContentType,
                                    follow_links: bool = False,
                                    max_depth: int = 1) -> InnovationExtractionResult:
        """Extract comprehensive innovation data from a URL"""

        try:
            logger.info(f"Starting extraction for {url} ({content_type.value})")

            # Create extraction result container
            extraction_result = InnovationExtractionResult(
                url=url,
                content_type=content_type,
                extraction_timestamp=datetime.now()
            )

            # Create content-specific extraction schema
            schema = self._create_extraction_schema(content_type)

            # Create LLM extraction strategy if API key is available
            extraction_strategy = None
            if self.llm_api_key:
                schema_prompt = self._create_extraction_prompt(schema, content_type)
                extraction_strategy = LLMExtractionStrategy(
                    provider="openai",
                    api_token=self.llm_api_key,
                    instruction=schema_prompt
                )

            # Perform the crawl with extraction
            result = await self.crawler.arun(
                url=url,
                extraction_strategy=extraction_strategy,
                bypass_cache=True,
                include_links_summary=follow_links,
                magic=True,  # Enable enhanced content extraction
                exclude_external_images=True,
                exclude_social_media_links=True
            )

            # Process extraction results
            extracted_data = await self._process_extraction_result(result, content_type, url)

            # Follow important links for additional context
            if follow_links and max_depth > 0:
                additional_data = await self._follow_related_links(result, content_type, max_depth - 1)
                extracted_data = self._merge_extraction_data(extracted_data, additional_data)

            # Validate and score the extraction
            extracted_data.data_completeness_score = self._calculate_completeness_score(extracted_data)
            extracted_data.confidence_score = self._calculate_confidence_score(extracted_data, result)
            extracted_data.validation_flags = self._generate_validation_flags(extracted_data)

            logger.info(f"Extraction completed for {url}. Completeness: {extracted_data.data_completeness_score:.2f}")

            return extracted_data

        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            return InnovationExtractionResult(
                url=url,
                content_type=content_type,
                extraction_timestamp=datetime.now(),
                success=False,
                validation_flags=[f"Extraction failed: {str(e)}"]
            )

    def _create_extraction_schema(self, content_type: ContentType) -> Dict[str, Any]:
        """Create content-specific extraction schema"""

        base_schema = {
            "innovation_basic_info": {
                "title": "string",
                "description": "string",
                "innovation_type": "string"
            },
            "problem_and_solution": {
                "problem_solved": "string",
                "target_users": "array",
                "value_proposition": "string"
            },
            "team_and_organization": {
                "founders": "array",
                "organization_name": "string",
                "location": "string",
                "team_size": "number"
            },
            "contact_and_social": {
                "email_contacts": "array",
                "linkedin_profiles": "array",
                "twitter_handles": "array",
                "github_repositories": "array",
                "contact_form_url": "string"
            }
        }

        if content_type == ContentType.STARTUP_PROFILE:
            base_schema.update({
                "funding_and_business": {
                    "funding_sources": "array",
                    "funding_amounts": "array",
                    "business_model": "string",
                    "revenue_model": "string"
                },
                "impact_and_adoption": {
                    "use_cases": "array",
                    "user_statistics": "object",
                    "social_impact": "string"
                }
            })

        elif content_type == ContentType.GITHUB_REPOSITORY:
            base_schema.update({
                "technical_details": {
                    "technical_approach": "string",
                    "technical_stack": "array",
                    "development_stage": "string",
                    "computational_requirements": "object",
                    "datasets_used": "array",
                    "performance_metrics": "object"
                },
                "open_source_metrics": {
                    "stars": "number",
                    "forks": "number",
                    "contributors": "number",
                    "license": "string"
                }
            })

        elif content_type == ContentType.RESEARCH_PAPER:
            base_schema.update({
                "research_details": {
                    "research_institution": "string",
                    "publication_venue": "string",
                    "publication_date": "string",
                    "doi": "string",
                    "arxiv_id": "string"
                },
                "technical_details": {
                    "technical_approach": "string",
                    "datasets_used": "array",
                    "performance_metrics": "object",
                    "computational_requirements": "object"
                }
            })

        elif content_type == ContentType.NEWS_ARTICLE:
            base_schema.update({
                "news_details": {
                    "publication_date": "string",
                    "author": "string",
                    "publication_name": "string"
                },
                "key_information": {
                    "funding_updates": "array",
                    "key_quotes": "array",
                    "mentioned_companies": "array"
                }
            })

        return base_schema

    def _create_extraction_prompt(self, schema: Dict[str, Any], content_type: ContentType) -> str:
        """Create extraction prompt for LLM"""

        base_prompt = f"""
        You are an expert at extracting structured information about African AI innovations.

        Extract information from this {content_type.value} and return it as JSON following this schema:
        {json.dumps(schema, indent=2)}

        IMPORTANT INSTRUCTIONS:
        1. Focus specifically on African AI innovations, companies, researchers, and developments
        2. Extract exact quotes, names, amounts, and technical details when available
        3. If information is not available, use null for that field
        4. For arrays, include all relevant items found
        5. Be precise with funding amounts, technical specifications, and contact information
        6. Identify specific African countries, cities, and regions mentioned
        7. Extract GitHub repositories, LinkedIn profiles, and other social links
        8. Include performance metrics, user statistics, and impact measurements when available

        Return only valid JSON matching the schema. Do not include explanations or comments.
        """

        if content_type == ContentType.STARTUP_PROFILE:
            base_prompt += """

            STARTUP-SPECIFIC FOCUS:
            - Extract funding rounds, investors, and valuation details
            - Identify business model and revenue streams
            - Capture user adoption metrics and growth statistics
            - Find customer testimonials and use case examples
            - Look for partnership announcements and market traction
            """

        elif content_type == ContentType.GITHUB_REPOSITORY:
            base_prompt += """

            GITHUB-SPECIFIC FOCUS:
            - Extract technical stack, programming languages, and frameworks
            - Identify computational requirements and system architecture
            - Capture performance benchmarks and evaluation metrics
            - Find dataset information and training procedures
            - Look for installation instructions and usage examples
            """

        elif content_type == ContentType.RESEARCH_PAPER:
            base_prompt += """

            RESEARCH-SPECIFIC FOCUS:
            - Extract research methodology and technical approaches
            - Identify datasets, experiments, and evaluation procedures
            - Capture performance results and comparison metrics
            - Find author affiliations and institutional connections
            - Look for reproducibility information and code availability
            """

        return base_prompt

    async def _process_extraction_result(self, result: Any, content_type: ContentType, url: str) -> InnovationExtractionResult:
        """Process crawl result and extract structured information"""

        extraction_result = InnovationExtractionResult(
            url=url,
            content_type=content_type,
            extraction_timestamp=datetime.now(),
            success=True
        )

        # Process LLM extraction if available
        if hasattr(result, 'extracted_content') and result.extracted_content:
            try:
                extracted_json = json.loads(result.extracted_content)
                extraction_result = self._map_json_to_result(extracted_json, extraction_result)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse extracted JSON for {url}")

        # Fallback to pattern-based extraction from raw content
        if hasattr(result, 'markdown_content') and result.markdown_content:
            pattern_extracted = self._pattern_based_extraction(result.markdown_content, content_type)
            extraction_result = self._merge_pattern_data(extraction_result, pattern_extracted)

        # Extract links and metadata
        if hasattr(result, 'links'):
            extraction_result.source_links = [link.get('href') for link in result.links if link.get('href')]

        return extraction_result

    def _map_json_to_result(self, extracted_json: Dict[str, Any], result: InnovationExtractionResult) -> InnovationExtractionResult:
        """Map extracted JSON data to InnovationExtractionResult fields"""

        # Map basic innovation info
        if 'innovation_basic_info' in extracted_json:
            basic_info = extracted_json['innovation_basic_info']
            result.title = basic_info.get('title')
            result.description = basic_info.get('description')
            result.innovation_type = basic_info.get('innovation_type')

        # Map problem and solution
        if 'problem_and_solution' in extracted_json:
            problem_solution = extracted_json['problem_and_solution']
            result.problem_solved = problem_solution.get('problem_solved')

        # Map technical details
        if 'technical_details' in extracted_json:
            tech_details = extracted_json['technical_details']
            result.technical_approach = tech_details.get('technical_approach')
            result.development_stage = tech_details.get('development_stage')

            # Handle arrays and objects
            if tech_details.get('technical_stack'):
                if isinstance(tech_details['technical_stack'], str):
                    result.technical_stack = [tech_details['technical_stack']]
                else:
                    result.technical_stack = tech_details['technical_stack']

            if tech_details.get('computational_requirements'):
                result.computational_requirements = tech_details['computational_requirements']

            if tech_details.get('datasets_used'):
                if isinstance(tech_details['datasets_used'], str):
                    result.datasets_used = [tech_details['datasets_used']]
                else:
                    result.datasets_used = tech_details['datasets_used']

            if tech_details.get('performance_metrics'):
                result.performance_metrics = tech_details['performance_metrics']

        # Map team and organization
        if 'team_and_organization' in extracted_json:
            team_org = extracted_json['team_and_organization']
            result.organization_affiliation = team_org.get('organization_name')
            result.location = team_org.get('location')

            # Handle creators/founders
            if team_org.get('founders'):
                founders_data = team_org['founders']
                if isinstance(founders_data, str):
                    result.creators = [{'name': founders_data, 'role': 'founder'}]
                elif isinstance(founders_data, list):
                    result.creators = [{'name': founder, 'role': 'founder'} for founder in founders_data]

        # Map contact information
        if 'contact_and_social' in extracted_json:
            contact_info = extracted_json['contact_and_social']
            result.contact_information = {
                'email': contact_info.get('email_contacts'),
                'linkedin': contact_info.get('linkedin_profiles'),
                'twitter': contact_info.get('twitter_handles'),
                'github': contact_info.get('github_repositories'),
                'contact_form': contact_info.get('contact_form_url')
            }

        # Map impact and adoption
        if 'impact_and_adoption' in extracted_json:
            impact = extracted_json['impact_and_adoption']
            if impact.get('use_cases'):
                if isinstance(impact['use_cases'], str):
                    result.use_cases = [impact['use_cases']]
                else:
                    result.use_cases = impact['use_cases']

            if impact.get('user_statistics'):
                result.user_adoption_metrics = impact['user_statistics']

        # Map recognition
        if 'recognition_and_validation' in extracted_json:
            recognition = extracted_json['recognition_and_validation']
            result.recognition = []

            if recognition.get('awards'):
                result.recognition.extend(recognition['awards'] if isinstance(recognition['awards'], list) else [recognition['awards']])
            if recognition.get('media_coverage'):
                result.media_coverage = recognition['media_coverage'] if isinstance(recognition['media_coverage'], list) else [recognition['media_coverage']]

        # Map funding information
        if 'funding_and_business' in extracted_json:
            funding = extracted_json['funding_and_business']

            if funding.get('funding_sources'):
                sources = funding['funding_sources']
                if isinstance(sources, str):
                    result.funding_sources = [{'name': sources}]
                elif isinstance(sources, list):
                    result.funding_sources = [{'name': source} if isinstance(source, str) else source for source in sources]

            if funding.get('funding_amounts'):
                amounts = funding['funding_amounts']
                result.funding_amounts = amounts if isinstance(amounts, list) else [amounts]

        return result

    def _pattern_based_extraction(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Fallback pattern-based extraction when LLM extraction fails"""

        extracted = {}

        # Extract emails
        emails = re.findall(self.validation_patterns['email'], content)
        if emails:
            extracted['emails'] = list(set(emails))

        # Extract URLs
        urls = re.findall(self.validation_patterns['url'], content)
        if urls:
            extracted['urls'] = list(set(urls))

        # Extract funding amounts
        funding_amounts = re.findall(self.validation_patterns['funding_amount'], content)
        if funding_amounts:
            extracted['funding_amounts'] = funding_amounts

        # Extract GitHub repositories
        github_repos = re.findall(self.validation_patterns['github_repo'], content)
        if github_repos:
            extracted['github_repos'] = list(set(github_repos))

        # Extract LinkedIn profiles
        linkedin_profiles = re.findall(self.validation_patterns['linkedin_profile'], content)
        if linkedin_profiles:
            extracted['linkedin_profiles'] = list(set(linkedin_profiles))

        # Extract African locations
        african_locations = re.findall(self.validation_patterns['african_location'], content, re.IGNORECASE)
        if african_locations:
            extracted['african_locations'] = list(set(african_locations))

        # Content type specific patterns
        if content_type == ContentType.GITHUB_REPOSITORY:
            extracted.update(self._extract_github_patterns(content))
        elif content_type == ContentType.RESEARCH_PAPER:
            extracted.update(self._extract_research_patterns(content))
        elif content_type == ContentType.STARTUP_PROFILE:
            extracted.update(self._extract_startup_patterns(content))

        return extracted

    def _extract_github_patterns(self, content: str) -> Dict[str, Any]:
        """Extract GitHub-specific patterns"""
        github_data = {}

        # Extract star count
        star_pattern = r'(\d+(?:,\d{3})*)\s*stars?'
        star_match = re.search(star_pattern, content, re.IGNORECASE)
        if star_match:
            github_data['stars'] = star_match.group(1)

        # Extract programming language
        language_pattern = r'(?:written in|primary language|mainly)\s+(\w+)'
        language_match = re.search(language_pattern, content, re.IGNORECASE)
        if language_match:
            github_data['primary_language'] = language_match.group(1)

        # Extract license
        license_pattern = r'license[:\s]+([A-Z]+(?:\s+[A-Z]+)*)'
        license_match = re.search(license_pattern, content, re.IGNORECASE)
        if license_match:
            github_data['license'] = license_match.group(1)

        return github_data

    def _extract_research_patterns(self, content: str) -> Dict[str, Any]:
        """Extract research paper-specific patterns"""
        research_data = {}

        # Extract DOI
        doi_pattern = r'doi[:\s]*(10\.\d+/[^\s]+)'
        doi_match = re.search(doi_pattern, content, re.IGNORECASE)
        if doi_match:
            research_data['doi'] = doi_match.group(1)

        # Extract arXiv ID
        arxiv_pattern = r'arxiv[:\s]*(\d+\.\d+)'
        arxiv_match = re.search(arxiv_pattern, content, re.IGNORECASE)
        if arxiv_match:
            research_data['arxiv_id'] = arxiv_match.group(1)

        # Extract publication year
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, content)
        if years:
            research_data['publication_years'] = list(set(years))

        return research_data

    def _extract_startup_patterns(self, content: str) -> Dict[str, Any]:
        """Extract startup-specific patterns"""
        startup_data = {}

        # Extract team size
        team_pattern = r'(?:team of|employs?|staff of)\s+(\d+)\s+(?:people|employees|members)'
        team_match = re.search(team_pattern, content, re.IGNORECASE)
        if team_match:
            startup_data['team_size'] = team_match.group(1)

        # Extract founding year
        founded_pattern = r'(?:founded|established|started)\s+in\s+(20\d{2})'
        founded_match = re.search(founded_pattern, content, re.IGNORECASE)
        if founded_match:
            startup_data['founded_year'] = founded_match.group(1)

        # Extract valuation
        valuation_pattern = r'valued\s+at\s+\$?(\d+(?:\.\d+)?)\s*(?:million|billion|M|B)'
        valuation_match = re.search(valuation_pattern, content, re.IGNORECASE)
        if valuation_match:
            startup_data['valuation'] = valuation_match.group(0)

        return startup_data

    def _merge_pattern_data(self, result: InnovationExtractionResult, pattern_data: Dict[str, Any]) -> InnovationExtractionResult:
        """Merge pattern-extracted data into result"""

        # Merge contact information
        if not result.contact_information:
            result.contact_information = {}

        if 'emails' in pattern_data:
            result.contact_information['email'] = pattern_data['emails'][0] if pattern_data['emails'] else None

        if 'github_repos' in pattern_data:
            result.contact_information['github'] = pattern_data['github_repos']

        if 'linkedin_profiles' in pattern_data:
            result.contact_information['linkedin'] = pattern_data['linkedin_profiles']

        # Merge funding information
        if 'funding_amounts' in pattern_data and not result.funding_amounts:
            result.funding_amounts = pattern_data['funding_amounts']

        # Merge location information
        if 'african_locations' in pattern_data and not result.location:
            result.location = pattern_data['african_locations'][0] if pattern_data['african_locations'] else None

        # Merge additional URLs
        if 'urls' in pattern_data:
            if not result.source_links:
                result.source_links = []
            result.source_links.extend(pattern_data['urls'])

        return result

    async def _follow_related_links(self,
                                  result: Any,
                                  content_type: ContentType,
                                  max_depth: int) -> Dict[str, Any]:
        """Follow related links for additional context"""

        if max_depth <= 0:
            return {}

        additional_data = {}

        # Identify high-value links to follow
        priority_links = []

        if hasattr(result, 'links'):
            for link in result.links[:5]:  # Limit to top 5 links
                href = link.get('href', '')
                text = link.get('text', '').lower()

                # Prioritize certain types of links
                if any(keyword in text for keyword in ['about', 'team', 'product', 'demo', 'github', 'paper']):
                    priority_links.append(href)

                # For GitHub repos, follow documentation links
                if content_type == ContentType.GITHUB_REPOSITORY and any(keyword in text for keyword in ['docs', 'wiki', 'readme']):
                    priority_links.append(href)

        # Extract data from priority links
        for link_url in priority_links[:3]:  # Maximum 3 additional links
            try:
                link_result = await self.crawler.arun(
                    url=link_url,
                    bypass_cache=True,
                    magic=True
                )

                if hasattr(link_result, 'markdown_content'):
                    link_patterns = self._pattern_based_extraction(link_result.markdown_content, content_type)
                    additional_data[link_url] = link_patterns

                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                logger.warning(f"Failed to extract from link {link_url}: {e}")
                continue

        return additional_data

    def _merge_extraction_data(self,
                             primary: InnovationExtractionResult,
                             additional: Dict[str, Any]) -> InnovationExtractionResult:
        """Merge additional extraction data into primary result"""

        for url, data in additional.items():
            # Add to source links
            if not primary.source_links:
                primary.source_links = []
            if url not in primary.source_links:
                primary.source_links.append(url)

            # Enhance contact information
            if 'emails' in data and primary.contact_information:
                if not primary.contact_information.get('email'):
                    primary.contact_information['email'] = data['emails'][0]

            # Enhance technical stack
            if 'primary_language' in data and not primary.technical_stack:
                primary.technical_stack = [data['primary_language']]

        return primary

    def _calculate_completeness_score(self, result: InnovationExtractionResult) -> float:
        """Calculate data completeness score based on filled fields"""

        total_fields = 0
        filled_fields = 0

        # Core fields (weighted more heavily)
        core_fields = ['title', 'description', 'innovation_type', 'problem_solved']
        for field in core_fields:
            total_fields += 2  # Weight core fields double
            if getattr(result, field):
                filled_fields += 2

        # Standard fields
        standard_fields = [
            'technical_approach', 'development_stage', 'technical_stack',
            'creators', 'organization_affiliation', 'location', 'contact_information',
            'use_cases', 'funding_sources'
        ]

        for field in standard_fields:
            total_fields += 1
            field_value = getattr(result, field)
            if field_value:
                # Check if it's a meaningful value (not empty list/dict)
                if isinstance(field_value, (list, dict)):
                    if field_value:
                        filled_fields += 1
                else:
                    filled_fields += 1

        return filled_fields / total_fields if total_fields > 0 else 0.0

    def _calculate_confidence_score(self, result: InnovationExtractionResult, crawl_result: Any) -> float:
        """Calculate confidence score based on extraction quality indicators"""

        confidence = 0.5  # Base confidence

        # Boost confidence for successful LLM extraction
        if hasattr(crawl_result, 'extracted_content') and crawl_result.extracted_content:
            confidence += 0.2

        # Boost confidence for pattern matches
        if result.contact_information and any(result.contact_information.values()):
            confidence += 0.1

        # Boost confidence for African relevance
        if result.location and any(country in result.location for country in ['South Africa', 'Nigeria', 'Kenya', 'Ghana']):
            confidence += 0.15

        # Boost confidence for technical depth
        if result.technical_stack and len(result.technical_stack) > 1:
            confidence += 0.1

        # Boost confidence for funding information
        if result.funding_sources or result.funding_amounts:
            confidence += 0.1

        return min(1.0, confidence)  # Cap at 1.0

    def _generate_validation_flags(self, result: InnovationExtractionResult) -> List[str]:
        """Generate validation flags for manual review"""

        flags = []

        # Flag missing core information
        if not result.title:
            flags.append("Missing title - manual verification needed")

        if not result.description:
            flags.append("Missing description - may need additional sources")

        if not result.location:
            flags.append("No African location identified - verify geographic relevance")

        # Flag incomplete contact information
        if not result.contact_information or not any(result.contact_information.values()):
            flags.append("No contact information found - outreach may be difficult")

        # Flag unverified funding claims
        if result.funding_amounts but not result.funding_sources:
            flags.append("Funding amounts mentioned without sources - verify claims")

        # Flag technical depth concerns
        if not result.technical_approach and not result.technical_stack:
            flags.append("Limited technical details - may need deeper investigation")

        return flags

    def to_json(self, result: InnovationExtractionResult) -> str:
        """Convert extraction result to JSON"""
        return result.to_json()

    def save_extraction(self, result: InnovationExtractionResult, filepath: str) -> None:
        """Save extraction result to file"""
        result.save_extraction(filepath)
        logger.info(f"Extraction result saved to {filepath}")


# Example usage and testing
async def main():
    """Example usage of Enhanced Crawl4AI Integration"""

    import os

    # Initialize with OpenAI API key for LLM extraction
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if not openai_api_key:
        print("Please set OPENAI_API_KEY environment variable")
        print("Testing pattern-based extraction only...")

        # Test pattern extraction without LLM
        test_content = """
        Flutterwave is a Nigerian fintech startup that raised $250 million in Series C funding.
        The company was founded by Olugbenga Agboola and is based in Lagos, Nigeria.
        Contact: hello@flutterwave.com
        GitHub: https://github.com/flutterwave/flutterwave
        LinkedIn: https://linkedin.com/company/flutterwave
        """

        orchestrator = IntelligentCrawl4AIOrchestrator()
        pattern_data = orchestrator._pattern_based_extraction(test_content, ContentType.STARTUP_PROFILE)
        print(f"Pattern extraction test: {pattern_data}")
        return

    async with IntelligentCrawl4AIOrchestrator(llm_api_key=openai_api_key) as orchestrator:

        # Test URLs for different content types
        test_urls = [
            ("https://github.com/instadeepai", ContentType.GITHUB_REPOSITORY),
            ("https://zindi.africa", ContentType.STARTUP_PROFILE)
        ]

        for url, content_type in test_urls:
            logger.info(f"\n--- Testing {content_type.value} extraction ---")

            try:
                result = await orchestrator.extract_innovation_data(
                    url=url,
                    content_type=content_type,
                    follow_links=True,
                    max_depth=1
                )

                logger.info(f"Extraction successful: {result.success}")
                logger.info(f"Completeness score: {result.data_completeness_score:.2f}")
                logger.info(f"Confidence score: {result.confidence_score:.2f}")
                logger.info(f"Title: {result.title}")
                logger.info(f"Location: {result.location}")
                logger.info(f"Validation flags: {len(result.validation_flags) if result.validation_flags else 0}")

                # Save result
                filename = f"extraction_{content_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                orchestrator.save_extraction(result, filename)

            except Exception as e:
                logger.error(f"Extraction failed for {url}: {e}")

        logger.info("\nCrawl4AI integration testing completed!")


if __name__ == "__main__":
    asyncio.run(main())
