value} synthesis",
            summary=summary,
            key_findings=key_findings,
            innovations_mentioned=innovations,
            funding_updates=funding_updates,
            policy_developments=policy_developments,
            validation_flags=self._generate_validation_flags(findings),
            confidence_score=confidence_score,
            sources=list(set(sources)),  # Deduplicate sources
            geographic_focus=geographic_focus,
            follow_up_actions=follow_up_actions
        )
    
    def _generate_follow_up_actions(self, intel_type: IntelligenceType, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable follow-up items based on findings"""
        
        actions = []
        
        if intel_type == IntelligenceType.INNOVATION_DISCOVERY:
            for innovation in [f for f in findings if f.get('type') == 'innovation_discovery']:
                if 'company_name' in innovation:
                    actions.append(f"Deep crawl {innovation['company_name']} for technical details and team information")
                    actions.append(f"Cross-reference {innovation['company_name']} against GitHub and LinkedIn for validation")
        
        elif intel_type == IntelligenceType.FUNDING_LANDSCAPE:
            actions.append("Verify funding amounts through multiple sources")
            actions.append("Contact startups directly for validation of funding claims")
            actions.append("Track funding impact on innovation development milestones")
        
        elif intel_type == IntelligenceType.RESEARCH_BREAKTHROUGH:
            actions.append("Extract full paper details for academic validation")
            actions.append("Map research collaboration networks")
            actions.append("Identify commercialization potential of research findings")
        
        return actions[:5]  # Limit to top 5 actions
    
    def _generate_validation_flags(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate validation flags for claims requiring verification"""
        
        flags = []
        
        for finding in findings:
            # Flag funding claims for verification
            if 'funding_mention' in finding:
                flags.append({
                    'type': 'funding_verification_needed',
                    'claim': finding['funding_mention'],
                    'source_finding': finding,
                    'priority': 'high'
                })
            
            # Flag new company mentions for validation
            if finding.get('type') == 'innovation_discovery' and 'company_name' in finding:
                flags.append({
                    'type': 'company_validation_needed',
                    'claim': f"New innovation by {finding['company_name']}",
                    'source_finding': finding,
                    'priority': 'medium'
                })
        
        return flags
    
    async def cross_validate_with_sources(self, innovation_claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-validate innovation claims against multiple sources
        """
        validation_result = {
            'claim': innovation_claim,
            'validation_status': 'pending',
            'confidence_score': 0.0,
            'supporting_sources': [],
            'conflicting_information': [],
            'verification_timestamp': datetime.now()
        }
        
        if 'company_name' in innovation_claim:
            company_name = innovation_claim['company_name']
            
            # Query multiple sources for validation
            validation_queries = [
                f"{company_name} African AI startup company details",
                f"{company_name} artificial intelligence platform technology",
                f"{company_name} founders team location Africa"
            ]
            
            supporting_evidence = 0
            total_checks = len(validation_queries)
            
            for query in validation_queries:
                try:
                    response = await self._query_perplexity(query)
                    content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    if company_name.lower() in content.lower():
                        supporting_evidence += 1
                        validation_result['supporting_sources'].append({
                            'query': query,
                            'evidence': content[:200],
                            'sources': response.get('sources', [])
                        })
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Validation query failed: {e}")
                    continue
            
            # Calculate validation confidence
            validation_result['confidence_score'] = supporting_evidence / total_checks
            
            if validation_result['confidence_score'] >= 0.6:
                validation_result['validation_status'] = 'validated'
            elif validation_result['confidence_score'] >= 0.3:
                validation_result['validation_status'] = 'partially_validated'
            else:
                validation_result['validation_status'] = 'unvalidated'
        
        return validation_result
    
    async def generate_trend_analysis(self, reports: List[IntelligenceReport]) -> Dict[str, Any]:
        """
        Analyze trends across multiple intelligence reports
        """
        trend_analysis = {
            'analysis_timestamp': datetime.now(),
            'reports_analyzed': len(reports),
            'time_span': self._calculate_time_span(reports),
            'emerging_patterns': [],
            'funding_trends': {},
            'geographic_trends': {},
            'technology_trends': {},
            'collaboration_patterns': [],
            'recommendations': []
        }
        
        # Analyze funding trends
        all_funding_updates = []
        for report in reports:
            all_funding_updates.extend(report.funding_updates)
        
        if all_funding_updates:
            trend_analysis['funding_trends'] = self._analyze_funding_trends(all_funding_updates)
        
        # Analyze geographic distribution
        all_geographic_mentions = []
        for report in reports:
            all_geographic_mentions.extend(report.geographic_focus)
        
        trend_analysis['geographic_trends'] = self._analyze_geographic_trends(all_geographic_mentions)
        
        # Generate recommendations
        trend_analysis['recommendations'] = self._generate_trend_recommendations(reports)
        
        return trend_analysis
    
    def _calculate_time_span(self, reports: List[IntelligenceReport]) -> str:
        """Calculate time span covered by reports"""
        if not reports:
            return "No reports"
        
        timestamps = [report.timestamp for report in reports]
        earliest = min(timestamps)
        latest = max(timestamps)
        
        span = latest - earliest
        return f"{span.days} days"
    
    def _analyze_funding_trends(self, funding_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze funding trends from collected updates"""
        return {
            'total_updates': len(funding_updates),
            'trend_direction': 'increasing',  # Placeholder - implement actual analysis
            'average_funding_size': 'TBD',
            'most_active_sectors': ['fintech', 'healthtech', 'agritech']
        }
    
    def _analyze_geographic_trends(self, geographic_mentions: List[str]) -> Dict[str, Any]:
        """Analyze geographic distribution trends"""
        from collections import Counter
        
        location_counts = Counter(geographic_mentions)
        
        return {
            'most_mentioned_locations': dict(location_counts.most_common(5)),
            'geographic_diversity_score': len(set(geographic_mentions)),
            'emerging_hubs': list(location_counts.keys())[:3]
        }
    
    def _generate_trend_recommendations(self, reports: List[IntelligenceReport]) -> List[str]:
        """Generate actionable recommendations based on trend analysis"""
        
        recommendations = [
            "Increase monitoring frequency for emerging innovation hubs",
            "Deep dive into cross-border collaboration patterns",
            "Validate high-impact innovation claims with direct outreach",
            "Expand data collection to underrepresented geographic regions",
            "Implement automated tracking for identified high-potential innovations"
        ]
        
        return recommendations
    
    def to_json(self, report: IntelligenceReport) -> str:
        """Convert intelligence report to JSON format"""
        return json.dumps(asdict(report), default=str, indent=2)
    
    def save_report(self, report: IntelligenceReport, filepath: str) -> None:
        """Save intelligence report to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json(report))
        
        logger.info(f"Intelligence report saved to {filepath}")


# Usage example and testing
async def main():
    """Example usage of Perplexity African AI Intelligence Module"""
    
    # Initialize with API key (replace with actual key)
    api_key = "your_perplexity_api_key_here"
    
    async with PerplexityAfricanAIModule(api_key) as intelligence_module:
        
        # Generate comprehensive intelligence reports
        logger.info("Starting African AI intelligence synthesis...")
        
        reports = await intelligence_module.synthesize_intelligence(
            intelligence_types=[
                IntelligenceType.INNOVATION_DISCOVERY,
                IntelligenceType.FUNDING_LANDSCAPE
            ],
            time_period='last_30_days'
        )
        
        # Process and display results
        for report in reports:
            logger.info(f"\n--- {report.report_type.value.upper()} REPORT ---")
            logger.info(f"Summary: {report.summary}")
            logger.info(f"Key Findings: {len(report.key_findings)} items")
            logger.info(f"Confidence Score: {report.confidence_score:.2f}")
            logger.info(f"Follow-up Actions: {len(report.follow_up_actions)} items")
            
            # Save report
            filename = f"intelligence_report_{report.report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            intelligence_module.save_report(report, filename)
        
        # Generate trend analysis
        if len(reports) > 1:
            logger.info("\nGenerating trend analysis...")
            trend_analysis = await intelligence_module.generate_trend_analysis(reports)
            logger.info(f"Trend Analysis: {json.dumps(trend_analysis, default=str, indent=2)}")
        
        logger.info("African AI intelligence synthesis completed!")


if __name__ == "__main__":
    asyncio.run(main())
_to_result(extracted_json, extraction_result)
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
        return json.dumps(asdict(result), default=str, indent=2)
    
    def save_extraction(self, result: InnovationExtractionResult, filepath: str) -> None:
        """Save extraction result to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json(result))
        
        logger.info(f"Extraction result saved to {filepath}")


# Example usage and testing
async def main():
    """Example usage of Enhanced Crawl4AI Integration"""
    
    # Initialize with OpenAI API key for LLM extraction
    openai_api_key = "your_openai_api_key_here"
    
    async with IntelligentCrawl4AIOrchestrator(llm_api_key=openai_api_key) as orchestrator:
        
        # Test URLs for different content types
        test_urls = [
            ("https://github.com/instadeepai", ContentType.GITHUB_REPOSITORY),
            ("https://zindi.africa", ContentType.STARTUP_PROFILE),
            ("https://arxiv.org/abs/2301.00001", ContentType.RESEARCH_PAPER)  # Example arXiv URL
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
