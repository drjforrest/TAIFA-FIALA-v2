            
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
    
    def _create_extraction_prompt(self, schema: Dict[str, Any], content_type: ContentType) -> str:
        """Create detailed extraction prompt for LLM"""
        
        base_prompt = f"""
        Extract structured information from this {content_type.value} webpage focusing on African AI innovation.
        
        Be extremely thorough and extract ALL available information. Pay special attention to:
        - African individuals, organizations, and locations
        - Technical details about AI/ML technologies
        - Funding information and business metrics
        - Contact details and social media links
        - Performance metrics and impact data
        
        Return the information in the following JSON structure:
        """
        
        # Convert schema to structured prompt
        schema_prompt = json.dumps(schema, indent=2)
        
        prompt = f"""{base_prompt}
        
        {schema_prompt}
        
        IMPORTANT EXTRACTION GUIDELINES:
        1. Extract exact values - don't paraphrase or summarize
        2. Include all URLs, email addresses, and contact information found
        3. Look for African countries, cities, universities, and organizations
        4. Extract specific numbers for metrics, funding, team size, etc.
        5. Include social media handles and professional profiles
        6. Capture technical specifications and requirements
        7. Note any partnerships, collaborations, or recognition mentioned
        8. If information is not available, leave the field empty or null
        
        Focus on completeness and accuracy. This data will be used for academic research on African AI innovation.
        """
        
        return prompt
    
    async def _process_extraction_result(self, 
                                       result: Any, 
                                       content_type: ContentType, 
                                       url: str) -> InnovationExtractionResult:
        """Process Crawl4AI result into structured InnovationExtractionResult"""
        
        extraction_result = InnovationExtractionResult(
            url=url,
            content_type=content_type,
            extraction_timestamp=datetime.now(),
            success=True
        )
        
        # Extract data from LLM result if available
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
        
        # Extract African locations
        african_locations = re.findall(self.validation_patterns['african_location'], content, re.IGNORECASE)
        if african_locations:
            extracted['african_locations'] = list(set(african_locations))
        
        return extracted
    
    def _merge_pattern_data(self, result: InnovationExtractionResult, pattern_data: Dict[str, Any]) -> InnovationExtractionResult:
        """Merge pattern-extracted data into result"""
        
        # Merge contact information
        if not result.contact_information:
            result.contact_information = {}
        
        if 'emails' in pattern_data:
            result.contact_information['email'] = pattern_data['emails'][0] if pattern_data['emails'] else None
        
        # Merge funding information
        if 'funding_amounts' in pattern_data and not result.funding_amounts:
            result.funding_amounts = pattern_data['funding_amounts']
        
        # Merge location information
        if 'african_locations' in pattern_data and not result.location:
            result.location = pattern_data['african_locations'][0] if pattern_data['african_locations'] else None
        
        return result
    
    async def _follow_related_links(self, 
                                  result: Any, 
                                  content_type: ContentType, 
                                  max_depth: int) -> Dict[str, Any]:
        """Follow related links for additional context"""
        
        if max_depth <= 0:
            return {}
        
        additional_data = {}
        return additional_data  # Simplified for now
    
    def _merge_extraction_data(self, 
                             primary: InnovationExtractionResult, 
                             additional: Dict[str, Any]) -> InnovationExtractionResult:
        """Merge additional extraction data into primary result"""
        return primary  # Simplified for now
    
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
        
        return flags
    
    def to_json(self, result: InnovationExtractionResult) -> str:
        """Convert extraction result to JSON"""
        return json.dumps(asdict(result), default=str, indent=2)


# Example usage and testing
async def main():
    """Example usage of Enhanced Crawl4AI Integration"""
    
    # Initialize with OpenAI API key for LLM extraction
    openai_api_key = "your_openai_api_key_here"
    
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
                
            except Exception as e:
                logger.error(f"Extraction failed for {url}: {e}")
        
        logger.info("\nCrawl4AI integration testing completed!")


if __name__ == "__main__":
    asyncio.run(main())
oughs
        if intelligence_type == IntelligenceType.RESEARCH_BREAKTHROUGH:
            return PriorityLevel.HIGH
        
        # Medium priority for innovation discoveries with high confidence
        if innovation.get('confidence', 0) > 0.8:
            return PriorityLevel.MEDIUM
        
        # Default to low priority
        return PriorityLevel.LOW
    
    async def _create_validation_target(self, flag: Dict[str, Any]) -> Optional[CollectionTarget]:
        """Create collection target from validation flag"""
        
        # Extract URL from validation flag if available
        source_finding = flag.get('source_finding', {})
        
        if 'company_name' in source_finding:
            company_name = source_finding['company_name']
            url = await self._discover_innovation_url(company_name)
            
            if url:
                return CollectionTarget(
                    id=f"validation_{company_name}_{datetime.now().timestamp()}",
                    url=url,
                    content_type=self._determine_content_type(url),
                    priority=PriorityLevel.URGENT,  # Validation targets are urgent
                    source_collector=CollectorType.INTELLIGENCE_SYNTHESIS,
                    metadata={
                        'validation_flag': flag,
                        'requires_verification': True
                    },
                    discovered_at=datetime.now()
                )
        
        return None
    
    async def _run_collector_mission(self, collector_type: CollectorType) -> List[CollectionTarget]:
        """Execute specific collector mission"""
        
        logger.info(f"Running {collector_type.value} mission")
        
        mission_config = self.collector_missions[collector_type]
        targets = []
        
        if collector_type == CollectorType.ACADEMIC_DISCOVERY:
            targets = await self._run_academic_discovery_mission(mission_config)
        elif collector_type == CollectorType.INNOVATION_DISCOVERY:
            targets = await self._run_innovation_discovery_mission(mission_config)
        elif collector_type == CollectorType.NEWS_MONITORING:
            targets = await self._run_news_monitoring_mission(mission_config)
        elif collector_type == CollectorType.COMMUNITY_SIGNALS:
            targets = await self._run_community_signals_mission(mission_config)
        
        logger.info(f"{collector_type.value} mission discovered {len(targets)} targets")
        return targets
    
    async def _run_academic_discovery_mission(self, mission_config: Dict[str, Any]) -> List[CollectionTarget]:
        """Run academic discovery mission to find research papers and profiles"""
        
        targets = []
        
        # Search for recent African AI research papers
        academic_queries = [
            "African artificial intelligence research 2025",
            "machine learning Nigeria Kenya South Africa authors",
            "AI development sub-saharan africa universities",
            "deep learning african languages processing"
        ]
        
        for query in academic_queries:
            try:
                # Use Perplexity to find recent academic work
                response = await self.intelligence_module._query_perplexity(
                    f"Recent academic papers: {query} with author affiliations and paper URLs"
                )
                
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Extract paper URLs and author profiles
                paper_targets = self._extract_academic_targets_from_content(content)
                targets.extend(paper_targets)
                
                await asyncio.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Academic discovery query failed: {query}. Error: {e}")
                continue
        
        return targets[:20]  # Limit to top 20 academic targets per cycle
    
    def _extract_academic_targets_from_content(self, content: str) -> List[CollectionTarget]:
        """Extract academic targets from search content"""
        
        targets = []
        
        # Extract arXiv URLs
        import re
        arxiv_pattern = r'https?://arxiv\.org/abs/\d+\.\d+'
        arxiv_urls = re.findall(arxiv_pattern, content)
        
        for url in arxiv_urls:
            target = CollectionTarget(
                id=f"arxiv_{url.split('/')[-1]}_{datetime.now().timestamp()}",
                url=url,
                content_type=ContentType.RESEARCH_PAPER,
                priority=PriorityLevel.MEDIUM,
                source_collector=CollectorType.ACADEMIC_DISCOVERY,
                metadata={'source': 'arxiv', 'discovery_method': 'perplexity_search'},
                discovered_at=datetime.now()
            )
            targets.append(target)
        
        # Extract Google Scholar profiles
        scholar_pattern = r'https?://scholar\.google\.com/citations\?user=[\w-]+'
        scholar_urls = re.findall(scholar_pattern, content)
        
        for url in scholar_urls:
            target = CollectionTarget(
                id=f"scholar_{url.split('=')[-1]}_{datetime.now().timestamp()}",
                url=url,
                content_type=ContentType.ACADEMIC_PROFILE,
                priority=PriorityLevel.LOW,
                source_collector=CollectorType.ACADEMIC_DISCOVERY,
                metadata={'source': 'google_scholar', 'discovery_method': 'perplexity_search'},
                discovered_at=datetime.now()
            )
            targets.append(target)
        
        return targets
    
    async def _run_innovation_discovery_mission(self, mission_config: Dict[str, Any]) -> List[CollectionTarget]:
        """Run innovation discovery mission to find AI projects and startups"""
        
        targets = []
        
        # GitHub discovery
        github_queries = [
            "African AI projects GitHub machine learning",
            "artificial intelligence startups South Africa Nigeria GitHub",
            "deep learning projects African developers",
            "computer vision Africa GitHub repositories"
        ]
        
        for query in github_queries:
            try:
                response = await self.intelligence_module._query_perplexity(
                    f"Active GitHub repositories: {query} with repository URLs and contributor details"
                )
                
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Extract GitHub repository URLs
                github_targets = self._extract_github_targets_from_content(content)
                targets.extend(github_targets)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"GitHub discovery query failed: {query}. Error: {e}")
                continue
        
        # Startup ecosystem discovery
        startup_queries = [
            "AI startups funding rounds Africa 2025",
            "machine learning companies Nigeria Kenya startup",
            "artificial intelligence platform launches Africa"
        ]
        
        for query in startup_queries:
            try:
                response = await self.intelligence_module._query_perplexity(
                    f"Recent startup activity: {query} with company websites and founder details"
                )
                
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Extract startup URLs
                startup_targets = self._extract_startup_targets_from_content(content)
                targets.extend(startup_targets)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"Startup discovery query failed: {query}. Error: {e}")
                continue
        
        return targets[:30]  # Limit to top 30 innovation targets per cycle
    
    def _extract_github_targets_from_content(self, content: str) -> List[CollectionTarget]:
        """Extract GitHub repository targets from search content"""
        
        targets = []
        
        import re
        github_pattern = r'https?://github\.com/[\w\-\.]+/[\w\-\.]+'
        github_urls = re.findall(github_pattern, content)
        
        for url in github_urls:
            # Extract repo info from URL
            repo_parts = url.split('/')
            if len(repo_parts) >= 5:
                owner = repo_parts[-2]
                repo_name = repo_parts[-1]
                
                target = CollectionTarget(
                    id=f"github_{owner}_{repo_name}_{datetime.now().timestamp()}",
                    url=url,
                    content_type=ContentType.GITHUB_REPOSITORY,
                    priority=PriorityLevel.MEDIUM,
                    source_collector=CollectorType.INNOVATION_DISCOVERY,
                    metadata={
                        'source': 'github',
                        'owner': owner,
                        'repo_name': repo_name,
                        'discovery_method': 'perplexity_search'
                    },
                    discovered_at=datetime.now()
                )
                targets.append(target)
        
        return targets
    
    def _extract_startup_targets_from_content(self, content: str) -> List[CollectionTarget]:
        """Extract startup targets from search content"""
        
        targets = []
        
        # Extract general URLs that might be startup websites
        import re
        url_pattern = r'https?://(?:www\.)?[\w\-\.]+\.(?:com|ai|co|io|net|org|co\.za|ng|ke|gh)'
        urls = re.findall(url_pattern, content)
        
        # Filter for likely startup websites (exclude common platforms)
        excluded_domains = ['github.com', 'linkedin.com', 'twitter.com', 'facebook.com', 'crunchbase.com']
        
        for url in urls:
            if not any(domain in url for domain in excluded_domains):
                # Create target for potential startup website
                domain = url.split('//')[-1].split('/')[0]
                
                target = CollectionTarget(
                    id=f"startup_{domain}_{datetime.now().timestamp()}",
                    url=url,
                    content_type=ContentType.STARTUP_PROFILE,
                    priority=PriorityLevel.MEDIUM,
                    source_collector=CollectorType.INNOVATION_DISCOVERY,
                    metadata={
                        'source': 'startup_ecosystem',
                        'domain': domain,
                        'discovery_method': 'perplexity_search'
                    },
                    discovered_at=datetime.now()
                )
                targets.append(target)
        
        return targets[:10]  # Limit startup targets
    
    async def _run_news_monitoring_mission(self, mission_config: Dict[str, Any]) -> List[CollectionTarget]:
        """Run news monitoring mission for recent developments"""
        
        targets = []
        
        news_queries = [
            "African AI startup news funding announcements today",
            "artificial intelligence Nigeria Kenya latest developments",
            "machine learning company launches Africa this week"
        ]
        
        for query in news_queries:
            try:
                response = await self.intelligence_module._query_perplexity(
                    f"Latest news articles: {query} with article URLs and company mentions"
                )
                
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Extract news article URLs
                news_targets = self._extract_news_targets_from_content(content)
                targets.extend(news_targets)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"News monitoring query failed: {query}. Error: {e}")
                continue
        
        return targets[:15]  # Limit news targets
    
    def _extract_news_targets_from_content(self, content: str) -> List[CollectionTarget]:
        """Extract news article targets from search content"""
        
        targets = []
        
        # Extract URLs from known African tech news sites
        import re
        
        news_domains = [
            'techpoint.africa',
            'techcabal.com',
            'disrupt-africa.com',
            'ventureburn.com',
            'techmoran.com'
        ]
        
        for domain in news_domains:
            domain_pattern = rf'https?://{re.escape(domain)}/[\w\-/]+'
            domain_urls = re.findall(domain_pattern, content)
            
            for url in domain_urls:
                target = CollectionTarget(
                    id=f"news_{domain}_{datetime.now().timestamp()}",
                    url=url,
                    content_type=ContentType.NEWS_ARTICLE,
                    priority=PriorityLevel.HIGH,  # News is time-sensitive
                    source_collector=CollectorType.NEWS_MONITORING,
                    metadata={
                        'source': 'news_monitoring',
                        'news_domain': domain,
                        'discovery_method': 'perplexity_search'
                    },
                    discovered_at=datetime.now()
                )
                targets.append(target)
        
        return targets
    
    async def _run_community_signals_mission(self, mission_config: Dict[str, Any]) -> List[CollectionTarget]:
        """Run community signals mission to identify talent and engagement"""
        
        targets = []
        
        # This would integrate with APIs like Kaggle, Zindi, etc.
        # For now, use Perplexity to find community activity
        
        community_queries = [
            "Kaggle competition winners Africa artificial intelligence",
            "Zindi data science challenge African participants",
            "Deep Learning Indaba speakers researchers Africa",
            "AI Saturday chapters Africa community leaders"
        ]
        
        for query in community_queries:
            try:
                response = await self.intelligence_module._query_perplexity(
                    f"Community activity: {query} with participant profiles and achievement details"
                )
                
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Extract community member profiles
                community_targets = self._extract_community_targets_from_content(content)
                targets.extend(community_targets)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"Community signals query failed: {query}. Error: {e}")
                continue
        
        return targets[:10]  # Limit community targets
    
    def _extract_community_targets_from_content(self, content: str) -> List[CollectionTarget]:
        """Extract community member targets from search content"""
        
        targets = []
        
        # Extract LinkedIn profiles of community members
        import re
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+'
        linkedin_urls = re.findall(linkedin_pattern, content)
        
        for url in linkedin_urls:
            profile_id = url.split('/')[-1]
            
            target = CollectionTarget(
                id=f"community_{profile_id}_{datetime.now().timestamp()}",
                url=url,
                content_type=ContentType.ACADEMIC_PROFILE,
                priority=PriorityLevel.LOW,
                source_collector=CollectorType.COMMUNITY_SIGNALS,
                metadata={
                    'source': 'community_signals',
                    'profile_type': 'linkedin',
                    'discovery_method': 'perplexity_search'
                },
                discovered_at=datetime.now()
            )
            targets.append(target)
        
        return targets
    
    def _prioritize_targets(self, targets: List[CollectionTarget]) -> List[CollectionTarget]:
        """Prioritize targets for processing based on priority level and other factors"""
        
        # Sort by priority level first, then by discovery time
        priority_order = {
            PriorityLevel.URGENT: 0,
            PriorityLevel.HIGH: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
            PriorityLevel.BATCH: 4
        }
        
        sorted_targets = sorted(
            targets,
            key=lambda t: (priority_order[t.priority], t.discovered_at)
        )
        
        # Limit to maximum targets per cycle
        max_targets = self.collection_config["processing_limits"]["max_targets_per_cycle"]
        return sorted_targets[:max_targets]
    
    async def _process_extraction_queue(self, 
                                      targets: List[CollectionTarget],
                                      max_concurrent: int = 5) -> List[InnovationExtractionResult]:
        """Process extraction queue with concurrency control"""
        
        logger.info(f"Processing {len(targets)} targets with max concurrency {max_concurrent}")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        extraction_tasks = []
        
        for target in targets:
            task = self._extract_target_with_semaphore(target, semaphore)
            extraction_tasks.append(task)
        
        # Process all extraction tasks
        extraction_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful extractions
        successful_extractions = []
        for result in extraction_results:
            if isinstance(result, InnovationExtractionResult):
                successful_extractions.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Extraction failed with exception: {result}")
        
        logger.info(f"Completed {len(successful_extractions)} successful extractions")
        return successful_extractions
    
    async def _extract_target_with_semaphore(self, 
                                           target: CollectionTarget, 
                                           semaphore: asyncio.Semaphore) -> InnovationExtractionResult:
        """Extract single target with semaphore control"""
        
        async with semaphore:
            try:
                logger.info(f"Extracting target: {target.url}")
                
                result = await self.extraction_orchestrator.extract_innovation_data(
                    url=target.url,
                    content_type=target.content_type,
                    follow_links=True,
                    max_depth=1
                )
                
                # Update target with extraction result
                target.extraction_result = result
                target.processed_at = datetime.now()
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to extract {target.url}: {e}")
                
                # Return failed extraction result
                return InnovationExtractionResult(
                    url=target.url,
                    content_type=target.content_type,
                    extraction_timestamp=datetime.now(),
                    success=False,
                    validation_flags=[f"Extraction failed: {str(e)}"]
                )
    
    async def _validate_and_store_innovations(self, 
                                            extraction_results: List[InnovationExtractionResult]) -> List[Dict[str, Any]]:
        """Validate extractions and prepare for database storage"""
        
        validated_innovations = []
        
        for result in extraction_results:
            if not result.success:
                continue
            
            # Apply quality thresholds
            min_completeness = self.collection_config["quality_thresholds"]["min_completeness_score"]
            min_confidence = self.collection_config["quality_thresholds"]["min_confidence_score"]
            max_flags = self.collection_config["quality_thresholds"]["max_validation_flags"]
            
            if (result.data_completeness_score >= min_completeness and 
                result.confidence_score >= min_confidence and
                len(result.validation_flags or []) <= max_flags):
                
                # Prepare for database insertion
                innovation_record = self._prepare_database_record(result)
                validated_innovations.append(innovation_record)
                
                logger.info(f"Validated innovation: {result.title}")
            else:
                logger.warning(f"Innovation failed quality thresholds: {result.url}")
        
        logger.info(f"Validated {len(validated_innovations)} innovations for database storage")
        return validated_innovations
    
    def _prepare_database_record(self, result: InnovationExtractionResult) -> Dict[str, Any]:
        """Prepare extraction result for database insertion"""
        
        return {
            'title': result.title,
            'description': result.description,
            'innovation_type': result.innovation_type,
            'problem_solved': result.problem_solved,
            'technical_approach': result.technical_approach,
            'development_stage': result.development_stage,
            'technical_stack': result.technical_stack,
            'location': result.location,
            'organization_affiliation': result.organization_affiliation,
            'contact_information': result.contact_information,
            'funding_sources': result.funding_sources,
            'funding_amounts': result.funding_amounts,
            'source_url': result.url,
            'extraction_metadata': {
                'completeness_score': result.data_completeness_score,
                'confidence_score': result.confidence_score,
                'extraction_timestamp': result.extraction_timestamp,
                'validation_flags': result.validation_flags
            }
        }
    
    def _generate_cycle_recommendations(self, 
                                      extraction_results: List[InnovationExtractionResult],
                                      cycle_result: CollectionCycleResult) -> List[str]:
        """Generate recommendations for next collection cycle"""
        
        recommendations = []
        
        # Analyze success rates
        success_rate = len([r for r in extraction_results if r.success]) / len(extraction_results) if extraction_results else 0
        
        if success_rate < 0.7:
            recommendations.append("Improve URL discovery and validation before extraction")
        
        # Analyze completeness scores
        completeness_scores = [r.data_completeness_score for r in extraction_results if r.success]
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        
        if avg_completeness < 0.5:
            recommendations.append("Enhance extraction schemas and LLM prompts for better data capture")
        
        # Analyze geographic distribution
        african_locations = [r.location for r in extraction_results if r.location and any(
            country in r.location for country in self.collection_config["geographic_focus"]["primary_countries"]
        )]
        
        if len(african_locations) < cycle_result.innovations_extracted * 0.8:
            recommendations.append("Improve African relevance filtering in target discovery")
        
        # Analyze content type performance
        content_type_performance = {}
        for result in extraction_results:
            if result.success:
                content_type_performance[result.content_type] = content_type_performance.get(result.content_type, 0) + 1
        
        best_performing_type = max(content_type_performance, key=content_type_performance.get) if content_type_performance else None
        if best_performing_type:
            recommendations.append(f"Increase focus on {best_performing_type.value} targets in next cycle")
        
        return recommendations
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about collection performance"""
        
        if not self.collection_history:
            return {"message": "No collection cycles completed yet"}
        
        latest_cycle = self.collection_history[-1]
        
        return {
            "latest_cycle": latest_cycle.cycle_id,
            "total_cycles": len(self.collection_history),
            "last_cycle_performance": {
                "targets_discovered": latest_cycle.targets_discovered,
                "targets_processed": latest_cycle.targets_processed,
                "innovations_extracted": latest_cycle.innovations_extracted,
                "success_rate": latest_cycle.innovations_extracted / latest_cycle.targets_processed if latest_cycle.targets_processed > 0 else 0
            },
            "active_targets": len(self.active_targets),
            "recommendations": latest_cycle.next_cycle_recommendations
        }


# Example usage
async def main():
    """Example usage of Data Collection Orchestrator"""
    
    # Initialize with API keys
    perplexity_key = "your_perplexity_api_key"
    openai_key = "your_openai_api_key"
    
    async with DataCollectionOrchestrator(perplexity_key, openai_key) as orchestrator:
        
        # Run a complete collection cycle
        result = await orchestrator.run_collection_cycle(
            collector_types=[
                CollectorType.INTELLIGENCE_SYNTHESIS,
                CollectorType.INNOVATION_DISCOVERY
            ]
        )
        
        logger.info(f"Collection cycle completed: {result.cycle_id}")
        logger.info(f"Discovered: {result.targets_discovered} targets")
        logger.info(f"Processed: {result.targets_processed} targets")
        logger.info(f"Extracted: {result.innovations_extracted} innovations")
        
        # Get collection statistics
        stats = orchestrator.get_collection_stats()
        logger.info(f"Collection stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
.innovations_mentioned:
                if 'company_name' in innovation:
                    target = await self._create_target_from_innovation(innovation)
                    if target:
                        targets.append(target)
        
        logger.info(f"Intelligence synthesis discovered {len(targets)} targets")
        return targets
    
    async def _create_target_from_innovation(self, innovation: Dict[str, Any]) -> Optional[CollectionTarget]:
        """Create collection target from intelligence mention"""
        
        company_name = innovation.get('company_name', '')
        if not company_name:
            return None
        
        # Simple URL discovery strategy
        url = await self._discover_innovation_url(company_name)
        if not url:
            return None
        
        content_type = self._determine_content_type(url)
        priority = PriorityLevel.MEDIUM
        
        return CollectionTarget(
            id=f"intel_{company_name}_{datetime.now().timestamp()}",
            url=url,
            content_type=content_type,
            priority=priority,
            source_collector=CollectorType.INTELLIGENCE_SYNTHESIS,
            metadata={
                'company_name': company_name,
                'original_mention': innovation
            },
            discovered_at=datetime.now()
        )
    
    async def _discover_innovation_url(self, company_name: str) -> Optional[str]:
        """Discover URL for innovation using search"""
        
        try:
            # Use Perplexity to find official website
            search_query = f"{company_name} official website African AI startup"
            response = await self.intelligence_module._query_perplexity(search_query)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract URLs from response
            import re
            urls = re.findall(r'https?://[^\s]+', content)
            
            # Return first valid URL (simplified)
            for url in urls:
                if not any(excluded in url for excluded in ['google.com', 'facebook.com', 'twitter.com']):
                    return url.rstrip('.,)')  # Clean up punctuation
            
        except Exception as e:
            logger.warning(f"Could not search for {company_name} website: {e}")
        
        return None
    
    def _determine_content_type(self, url: str) -> ContentType:
        """Determine content type based on URL"""
        
        for pattern, content_type in self.content_type_mapping.items():
            if pattern in url:
                return content_type
        
        return ContentType.INNOVATION_PROFILE
    
    def _prioritize_targets(self, targets: List[CollectionTarget]) -> List[CollectionTarget]:
        """Prioritize targets for processing"""
        
        priority_order = {
            PriorityLevel.URGENT: 0,
            PriorityLevel.HIGH: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
            PriorityLevel.BATCH: 4
        }
        
        return sorted(targets, key=lambda t: priority_order[t.priority])
    
    async def _process_extraction_queue(self, targets: List[CollectionTarget]) -> List[InnovationExtractionResult]:
        """Process extraction queue with concurrency control"""
        
        logger.info(f"Processing {len(targets)} targets")
        
        extraction_results = []
        
        for target in targets:
            try:
                logger.info(f"Extracting: {target.url}")
                
                result = await self.extraction_orchestrator.extract_innovation_data(
                    url=target.url,
                    content_type=target.content_type,
                    follow_links=False,  # Simplified for demo
                    max_depth=1
                )
                
                target.extraction_result = result
                target.processed_at = datetime.now()
                extraction_results.append(result)
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to extract {target.url}: {e}")
                
                # Create failed result
                failed_result = InnovationExtractionResult(
                    url=target.url,
                    content_type=target.content_type,
                    extraction_timestamp=datetime.now(),
                    success=False,
                    validation_flags=[f"Extraction failed: {str(e)}"]
                )
                extraction_results.append(failed_result)
        
        return extraction_results
    
    async def _validate_innovations(self, results: List[InnovationExtractionResult]) -> List[Dict[str, Any]]:
        """Validate extraction results"""
        
        validated = []
        
        for result in results:
            if (result.success and 
                result.data_completeness_score >= 0.3 and 
                result.confidence_score >= 0.5):
                
                innovation_record = {
                    'title': result.title,
                    'description': result.description,
                    'innovation_type': result.innovation_type,
                    'location': result.location,
                    'source_url': result.url,
                    'completeness_score': result.data_completeness_score,
                    'confidence_score': result.confidence_score,
                    'extracted_at': result.extraction_timestamp
                }
                
                validated.append(innovation_record)
                logger.info(f"Validated innovation: {result.title}")
        
        logger.info(f"Validated {len(validated)} innovations")
        return validated
    
    def _generate_recommendations(self, results: List[InnovationExtractionResult]) -> List[str]:
        """Generate recommendations for next cycle"""
        
        recommendations = []
        
        success_rate = len([r for r in results if r.success]) / len(results) if results else 0
        
        if success_rate < 0.7:
            recommendations.append("Improve URL discovery and validation")
        
        avg_completeness = sum(r.data_completeness_score for r in results if r.success) / len([r for r in results if r.success]) if any(r.success for r in results) else 0
        
        if avg_completeness < 0.5:
            recommendations.append("Enhance extraction schemas for better data capture")
        
        return recommendations
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        
        if not self.collection_history:
            return {"message": "No collection cycles completed yet"}
        
        latest = self.collection_history[-1]
        
        return {
            "latest_cycle_id": latest.cycle_id,
            "total_cycles": len(self.collection_history),
            "last_performance": {
                "targets_discovered": latest.targets_discovered,
                "targets_processed": latest.targets_processed,
                "innovations_extracted": latest.innovations_extracted,
                "success_rate": latest.innovations_extracted / latest.targets_processed if latest.targets_processed > 0 else 0
            },
            "active_targets": len(self.active_targets),
            "recommendations": latest.recommendations
        }


# Example usage
async def main():
    """Example usage of Data Collection Orchestrator"""
    
    # Replace with actual API keys
    perplexity_key = "your_perplexity_api_key"
    openai_key = "your_openai_api_key"
    
    async with DataCollectionOrchestrator(perplexity_key, openai_key) as orchestrator:
        
        # Run collection cycle
        result = await orchestrator.run_collection_cycle()
        
        logger.info(f"Cycle completed: {result.cycle_id}")
        logger.info(f"Discovered: {result.targets_discovered}")
        logger.info(f"Processed: {result.targets_processed}")
        logger.info(f"Extracted: {result.innovations_extracted}")
        
        # Get stats
        stats = orchestrator.get_stats()
        logger.info(f"Stats: {json.dumps(stats, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())
