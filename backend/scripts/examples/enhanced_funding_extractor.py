"""
Enhanced Funding Extractor
Extracts comprehensive funding information from text using advanced pattern recognition

This module provides enhanced extraction capabilities for the three main funding patterns:
1. Total Pool Pattern: "The fund announces $5M total funding for 10-15 projects"
2. Exact Amount Pattern: "Each project receives exactly $50,000"
3. Range Pattern: "Grants ranging from $25,000 to $100,000"

The extractor also identifies:
- Target audiences (startups, researchers, SMEs, individuals)
- AI subsectors (healthcare, fintech, education, etc.)
- Application deadlines and types
- Process information and requirements
- Special focus indicators (gender, youth, collaboration)
- Project details and development stages
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class EnhancedFundingExtractor:
    """
    Enhanced funding information extractor with pattern recognition
    Supports three main funding announcement patterns and comprehensive field extraction
    """
    
    def __init__(self):
        # Initialize pattern dictionaries
        self._initialize_patterns()
        
        # Currency symbol mapping
        self.currency_symbols = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            'USD': 'USD',
            'EUR': 'EUR',
            'GBP': 'GBP',
            'CAD': 'CAD',
            'AUD': 'AUD',
            'ZAR': 'ZAR',  # South African Rand
            'NGN': 'NGN',  # Nigerian Naira
            'KES': 'KES',  # Kenyan Shilling
            'GHS': 'GHS',  # Ghanaian Cedi
        }
    
    def _initialize_patterns(self):
        """Initialize all regex patterns for extraction"""
        
        # Pattern 1: Total Pool Patterns
        self.total_pool_patterns = [
            r'(?:announces?|launches?|provides?)\s+([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(million|billion|m|b|k|thousand)?\s+(?:total\s+)?(?:funding|fund|grant|prize)',
            r'([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(million|billion|m|b|k|thousand)?\s+(?:total\s+)?(?:funding|fund|initiative|program)',
            r'(?:total\s+of\s+|totaling\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(million|billion|m|b|k|thousand)?',
            r'([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(million|billion|m|b|k|thousand)?\s+(?:fund|initiative)\s+(?:to\s+support|for)',
            r'([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(m|million)\s+(?:initiative|funding|fund)',
        ]
        
        # Pattern 2: Exact Amount Patterns
        self.exact_amount_patterns = [
            r'(?:each|every)\s+(?:project|grant|award)\s+(?:receives?|gets?|will\s+receive)\s+(?:exactly\s+)?([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?',
            r'([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?\s+(?:each|per\s+project|per\s+grant)',
            r'(?:grants?\s+of\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?\s+(?:each|per)',
            r'(?:exactly\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?\s+(?:per\s+project|each)',
            r'(?:each\s+selected\s+project\s+will\s+receive\s+exactly\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?',
        ]
        
        # Pattern 3: Range Patterns
        self.range_amount_patterns = [
            r'(?:grants?\s+)?(?:ranging\s+from\s+|between\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(?:thousand|k|million|m)?\s+(?:to|and|\-)\s+([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?',
            r'([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(?:thousand|k|million|m)?\s*(?:\-|to)\s*([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?\s+(?:grants?|funding|awards?)',
            r'(?:from\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(?:thousand|k|million|m)?\s+(?:to|up\s+to)\s+([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?',
            r'(?:up\s+to\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?',  # "up to $X" pattern
            r'(?:receive\s+up\s+to\s+)([€$£¥]?)\s*(\d+(?:[.,]\d+)?)\s*(thousand|k|million|m)?',
        ]
        
        # Project count patterns
        self.project_count_patterns = [
            r'(?:support|fund|award)\s+(\d+)(?:\s*[-–—]\s*(\d+))?\s+(?:projects?|startups?|companies?|teams?)',
            r'(\d+)(?:\s*[-–—]\s*(\d+))?\s+(?:projects?|grants?|awards?)\s+(?:will\s+be|to\s+be)',
            r'(?:up\s+to\s+)(\d+)\s+(?:projects?|grants?|awards?)',
            r'(?:maximum\s+of\s+)(\d+)\s+(?:projects?|grants?|awards?)',
        ]
        
        # Target audience patterns
        self.target_audience_patterns = {
            'startups': [
                r'startups?', r'start-ups?', r'entrepreneurs?', r'ventures?', 
                r'early\s+stage\s+companies?', r'emerging\s+companies?'
            ],
            'researchers': [
                r'researchers?', r'research\s+teams?', r'academics?', r'scientists?',
                r'research\s+institutions?', r'universities?'
            ],
            'smes': [
                r'smes?', r'small\s+(?:and\s+)?medium\s+enterprises?', 
                r'small\s+businesses?', r'medium\s+businesses?'
            ],
            'individuals': [
                r'individuals?', r'persons?', r'applicants?', r'candidates?'
            ],
            'nonprofits': [
                r'non-?profits?', r'ngos?', r'charities?', r'foundations?',
                r'civil\s+society', r'community\s+organizations?'
            ],
            'students': [
                r'students?', r'graduates?', r'undergraduates?', r'postgraduates?',
                r'phd\s+candidates?', r'doctoral\s+students?'
            ]
        }
        
        # AI subsector patterns
        self.ai_subsector_patterns = {
            'healthcare': [
                r'healthcare?', r'health\s+tech', r'medical', r'biotech', r'pharma',
                r'digital\s+health', r'telemedicine', r'health\s+ai'
            ],
            'fintech': [
                r'fintech', r'financial\s+technology', r'banking', r'payments?',
                r'blockchain', r'cryptocurrency', r'digital\s+finance'
            ],
            'education': [
                r'education', r'edtech', r'educational\s+technology', r'learning',
                r'e-learning', r'digital\s+education', r'training'
            ],
            'agriculture': [
                r'agriculture', r'agtech', r'farming', r'agri-tech', r'food\s+tech',
                r'precision\s+agriculture', r'smart\s+farming'
            ],
            'climate': [
                r'climate', r'environmental?', r'green\s+tech', r'clean\s+tech',
                r'sustainability', r'renewable\s+energy', r'carbon'
            ],
            'mobility': [
                r'mobility', r'transportation', r'automotive', r'logistics',
                r'smart\s+cities', r'urban\s+tech'
            ],
            'general': [
                r'artificial\s+intelligence', r'machine\s+learning', r'deep\s+learning',
                r'computer\s+vision', r'natural\s+language', r'robotics'
            ]
        }
        
        # Deadline patterns
        self.deadline_patterns = [
            r'(?:deadline|due\s+date|applications?\s+due|submit\s+by)[:\s]+([^\.]+)',
            r'(?:applications?\s+must\s+be\s+submitted\s+by)[:\s]+([^\.]+)',
            r'(?:closing\s+date)[:\s]+([^\.]+)',
            r'(?:apply\s+by|submit\s+before)[:\s]+([^\.]+)',
        ]
        
        # Process information patterns
        self.process_patterns = {
            'application_process': [
                r'(?:application\s+process|how\s+to\s+apply)[:\s]+([^\.]+)',
                r'(?:to\s+apply)[:\s]+([^\.]+)',
            ],
            'selection_criteria': [
                r'(?:selection\s+criteria|evaluation\s+criteria)[:\s]+([^\.]+)',
                r'(?:we\s+are\s+looking\s+for|criteria\s+include)[:\s]+([^\.]+)',
            ],
            'reporting_requirements': [
                r'(?:reporting\s+requirements|progress\s+reports?)[:\s]+([^\.]+)',
                r'(?:recipients?\s+must|grantees?\s+must)[:\s]+([^\.]+)',
            ]
        }
        
        # Focus indicators
        self.focus_indicators = {
            'collaboration_required': [
                r'collaboration', r'partnership', r'consortium', r'joint\s+application',
                r'team\s+application', r'multi-institutional'
            ],
            'gender_focused': [
                r'women', r'female', r'gender', r'women-led', r'women\s+entrepreneurs?',
                r'female\s+founders?', r'girls?'
            ],
            'youth_focused': [
                r'youth', r'young\s+people', r'young\s+entrepreneurs?', r'students?',
                r'under\s+\d+', r'age\s+\d+', r'young\s+professionals?'
            ]
        }

    def extract_funding_info(self, text: str) -> Dict[str, Any]:
        """
        Extract comprehensive funding information from text
        Returns structured data matching the enhanced schema
        """
        text_lower = text.lower()
        
        # Determine funding type and extract amounts
        funding_info = self._extract_funding_amounts(text_lower)
        
        # Extract additional fields
        funding_info.update({
            'target_audience': self._extract_target_audience(text_lower),
            'ai_subsectors': self._extract_ai_subsectors(text_lower),
            'deadline_info': self._extract_deadline_info(text),
            'process_info': self._extract_process_info(text),
            'focus_indicators': self._extract_focus_indicators(text_lower),
            'project_details': self._extract_project_details(text_lower),
        })
        
        return funding_info

    def _extract_funding_amounts(self, text: str) -> Dict[str, Any]:
        """Extract funding amounts and determine funding type pattern"""
        
        # Try total pool patterns first
        for pattern in self.total_pool_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                currency_symbol = groups[0] if groups[0] else '$'
                amount_str = groups[1] if len(groups) > 1 else None
                multiplier = groups[2] if len(groups) > 2 and groups[2] else None
                
                if amount_str:
                    amount = self._parse_amount(amount_str, multiplier)
                    currency = self._parse_currency(currency_symbol)
                    
                    # Look for project count
                    project_count = self._extract_project_count(text)
                    
                    return {
                        'funding_type': 'total_pool',
                        'total_funding_pool': amount,
                        'currency': currency,
                        'estimated_project_count': project_count.get('estimated_count'),
                        'project_count_range': project_count.get('count_range'),
                    }
        
        # Try exact amount patterns
        for pattern in self.exact_amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                currency_symbol = groups[0] if groups[0] else '$'
                amount_str = groups[1] if len(groups) > 1 else None
                multiplier = groups[2] if len(groups) > 2 and groups[2] else None
                
                if amount_str:
                    amount = self._parse_amount(amount_str, multiplier)
                    currency = self._parse_currency(currency_symbol)
                    
                    return {
                        'funding_type': 'per_project_exact',
                        'exact_amount_per_project': amount,
                        'currency': currency,
                    }
        
        # Try range patterns
        for pattern in self.range_amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                # Handle "up to X" pattern (single amount)
                if len(groups) == 3 and groups[1] and not any(groups[3:] if len(groups) > 3 else []):
                    currency_symbol = groups[0] if groups[0] else '$'
                    max_amount_str = groups[1]
                    multiplier = groups[2] if groups[2] else None
                    
                    max_amount = self._parse_amount(max_amount_str, multiplier)
                    currency = self._parse_currency(currency_symbol)
                    
                    return {
                        'funding_type': 'per_project_range',
                        'min_amount_per_project': 0,
                        'max_amount_per_project': max_amount,
                        'currency': currency,
                    }
                
                # Handle range pattern (min to max)
                elif len(groups) >= 4:
                    currency1 = groups[0] if groups[0] else '$'
                    min_amount_str = groups[1] if groups[1] else None
                    currency2 = groups[2] if groups[2] else currency1
                    max_amount_str = groups[3] if groups[3] else None
                    multiplier = groups[4] if len(groups) >= 5 and groups[4] else None
                    
                    if min_amount_str and max_amount_str:
                        min_amount = self._parse_amount(min_amount_str, multiplier)
                        max_amount = self._parse_amount(max_amount_str, multiplier)
                        currency = self._parse_currency(currency1)
                        
                        return {
                            'funding_type': 'per_project_range',
                            'min_amount_per_project': min_amount,
                            'max_amount_per_project': max_amount,
                            'currency': currency,
                        }
        
        # Default fallback
        return {
            'funding_type': 'per_project_range',
            'currency': 'USD',
        }

    def _extract_project_count(self, text: str) -> Dict[str, Any]:
        """Extract expected number of projects to be funded"""
        for pattern in self.project_count_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:  # Range pattern
                    try:
                        return {
                            'count_range': {
                                'min': int(groups[0]),
                                'max': int(groups[1])
                            }
                        }
                    except (ValueError, TypeError):
                        continue
                elif groups[0]:  # Single number
                    try:
                        return {
                            'estimated_count': int(groups[0])
                        }
                    except (ValueError, TypeError):
                        continue
        return {}

    def _extract_target_audience(self, text: str) -> List[str]:
        """Extract target audience from text"""
        audiences = []
        for audience_type, patterns in self.target_audience_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    audiences.append(audience_type)
                    break
        return audiences

    def _extract_ai_subsectors(self, text: str) -> List[str]:
        """Extract AI subsectors and focus areas"""
        subsectors = []
        for subsector, patterns in self.ai_subsector_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    subsectors.append(subsector)
                    break
        return subsectors

    def _extract_deadline_info(self, text: str) -> Dict[str, Any]:
        """Extract deadline and deadline type information"""
        deadline_info = {}
        
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline_text = match.group(1).strip()
                
                # Determine deadline type
                if re.search(r'rolling|ongoing|continuous', deadline_text, re.IGNORECASE):
                    deadline_info['application_deadline_type'] = 'rolling'
                elif re.search(r'rounds?|phases?|cycles?', deadline_text, re.IGNORECASE):
                    deadline_info['application_deadline_type'] = 'multiple_rounds'
                else:
                    deadline_info['application_deadline_type'] = 'fixed'
                
                # Try to parse actual date
                parsed_date = self._parse_date(deadline_text)
                if parsed_date:
                    deadline_info['deadline'] = parsed_date
                
                break
        
        return deadline_info

    def _extract_process_info(self, text: str) -> Dict[str, Any]:
        """Extract application process and requirements"""
        process_info = {}
        
        for info_type, patterns in self.process_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    
                    if info_type == 'selection_criteria':
                        # Split criteria into list
                        criteria = [c.strip() for c in re.split(r'[;,\n]', content) if c.strip()]
                        process_info[info_type] = criteria
                    elif info_type == 'reporting_requirements':
                        # Split requirements into list
                        requirements = [r.strip() for r in re.split(r'[;,\n]', content) if r.strip()]
                        process_info[info_type] = requirements
                    else:
                        process_info[info_type] = content
                    break
        
        return process_info

    def _extract_focus_indicators(self, text: str) -> Dict[str, bool]:
        """Extract special focus indicators"""
        indicators = {}
        
        for focus_type, patterns in self.focus_indicators.items():
            indicators[focus_type] = any(
                re.search(pattern, text, re.IGNORECASE) for pattern in patterns
            )
        
        return indicators

    def _extract_project_details(self, text: str) -> Dict[str, Any]:
        """Extract project duration and other details"""
        details = {}
        
        # Project duration patterns
        duration_patterns = [
            r'(?:project\s+duration|duration)[:\s]+([^\.]+)',
            r'(?:projects?\s+will\s+run\s+for|funding\s+period)[:\s]+([^\.]+)',
            r'(\d+)(?:\s*[-–—]\s*(\d+))?\s*(?:months?|years?)\s+(?:project|funding|grant)',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['project_duration'] = match.group(1).strip()
                break
        
        # Development stage patterns
        stage_patterns = {
            'early_stage': [r'early\s+stage', r'prototype', r'proof\s+of\s+concept', r'mvp'],
            'growth_stage': [r'growth\s+stage', r'scaling', r'expansion', r'series\s+a'],
            'mature_stage': [r'mature', r'established', r'series\s+b', r'scale-?up'],
        }
        
        development_stages = []
        for stage, patterns in stage_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    development_stages.append(stage)
                    break
        
        if development_stages:
            details['development_stage'] = development_stages
        
        return details

    def _parse_amount(self, amount_str: str, multiplier: str = None) -> float:
        """Parse amount string to numeric value"""
        if not amount_str:
            return 0.0
            
        try:
            # Remove commas and convert to float
            amount = float(re.sub(r'[,\s]', '', str(amount_str)))
            
            # Apply multiplier
            if multiplier:
                multiplier = multiplier.lower()
                if multiplier in ['k', 'thousand']:
                    amount *= 1000
                elif multiplier in ['m', 'million']:
                    amount *= 1000000
                elif multiplier in ['b', 'billion']:
                    amount *= 1000000000
            
            return amount
        except (ValueError, TypeError):
            return 0.0

    def _parse_currency(self, currency_symbol: str) -> str:
        """Parse currency symbol to currency code"""
        if not currency_symbol:
            return 'USD'
        currency_symbol = str(currency_symbol).strip()
        return self.currency_symbols.get(currency_symbol, 'USD')

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        # This is a simplified parser - in production, use a library like dateutil
        date_patterns = [
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',          # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    # This is simplified - implement proper date parsing
                    return date_str.strip()
                except:
                    continue
        
        return None


# Enhanced ETL Pipeline Integration
class EnhancedETLPipeline:
    """
    Enhanced ETL pipeline that uses the new extraction patterns
    """
    
    def __init__(self):
        self.extractor = EnhancedFundingExtractor()
    
    def process_rss_item(self, rss_item: Dict[str, Any]) -> Dict[str, Any]:
        """Process RSS feed item with enhanced extraction"""
        
        # Combine title and description for analysis
        full_text = f"{rss_item.get('title', '')} {rss_item.get('description', '')}"
        
        # Extract funding information
        funding_info = self.extractor.extract_funding_info(full_text)
        
        # Build enhanced opportunity data
        opportunity_data = {
            # Core fields
            'title': rss_item.get('title', ''),
            'description': rss_item.get('description', ''),
            'source_url': rss_item.get('link', ''),
            'application_url': rss_item.get('link', ''),
            
            # Enhanced funding fields
            'funding_type': funding_info.get('funding_type', 'per_project_range'),
            'total_funding_pool': funding_info.get('total_funding_pool'),
            'min_amount_per_project': funding_info.get('min_amount_per_project'),
            'max_amount_per_project': funding_info.get('max_amount_per_project'),
            'exact_amount_per_project': funding_info.get('exact_amount_per_project'),
            'estimated_project_count': funding_info.get('estimated_project_count'),
            'project_count_range': funding_info.get('project_count_range'),
            'currency': funding_info.get('currency', 'USD'),
            
            # Enhanced process fields
            'deadline': funding_info.get('deadline_info', {}).get('deadline'),
            'application_deadline_type': funding_info.get('deadline_info', {}).get('application_deadline_type', 'fixed'),
            'application_process': funding_info.get('process_info', {}).get('application_process'),
            'selection_criteria': funding_info.get('process_info', {}).get('selection_criteria'),
            'reporting_requirements': funding_info.get('process_info', {}).get('reporting_requirements'),
            
            # Enhanced targeting fields
            'target_audience': funding_info.get('target_audience'),
            'ai_subsectors': funding_info.get('ai_subsectors'),
            'development_stage': funding_info.get('project_details', {}).get('development_stage'),
            'project_duration': funding_info.get('project_details', {}).get('project_duration'),
            
            # Focus indicators
            'collaboration_required': funding_info.get('focus_indicators', {}).get('collaboration_required'),
            'gender_focused': funding_info.get('focus_indicators', {}).get('gender_focused'),
            'youth_focused': funding_info.get('focus_indicators', {}).get('youth_focused'),
            
            # Standard metadata
            'status': 'active',
            'source_type': 'rss',
            'created_at': datetime.utcnow().isoformat(),
        }
        
        # Remove None values
        return {k: v for k, v in opportunity_data.items() if v is not None}
    
    def process_web_scraped_content(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process web scraped content with enhanced extraction"""
        
        # Combine all text content
        full_text = " ".join([
            scraped_data.get('title', ''),
            scraped_data.get('content', ''),
            scraped_data.get('meta_description', ''),
        ])
        
        # Extract funding information
        funding_info = self.extractor.extract_funding_info(full_text)
        
        # Build enhanced opportunity data similar to RSS processing
        opportunity_data = self.process_rss_item({
            'title': scraped_data.get('title'),
            'description': scraped_data.get('content'),
            'link': scraped_data.get('url'),
        })
        
        # Add web-specific metadata
        opportunity_data.update({
            'source_type': 'web_scraping',
            'meta_description': scraped_data.get('meta_description'),
            'scraped_at': datetime.utcnow().isoformat(),
        })
        
        return opportunity_data


# Example usage and testing
if __name__ == "__main__":
    extractor = EnhancedFundingExtractor()
    
    # Test cases for the three funding patterns
    test_cases = [
        # Total pool pattern
        "The African Innovation Fund announces $5 million total funding to support 10-15 AI startups across the continent.",
        
        # Exact amount pattern  
        "Each selected project will receive exactly $50,000 to develop AI solutions for healthcare challenges.",
        
        # Range pattern
        "Grants ranging from $25,000 to $100,000 are available for women-led AI ventures focusing on fintech and edtech.",
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"Text: {test_case}")
        result = extractor.extract_funding_info(test_case)
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
