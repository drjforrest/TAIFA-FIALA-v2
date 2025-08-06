"""
Enhanced Publication Analysis Service for TAIFA-FIALA
Implements Phase 1 of the Citations Expansion Strategy:
- Enhanced metadata extraction
- Author affiliation tracking
- Institutional connection mapping
- Business model and development stage detection

Focus on extracting maximum intelligence from existing publication data.
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import json

from loguru import logger
from config.database import get_supabase


@dataclass
class AuthorAffiliation:
    """Author affiliation information"""
    author_name: str
    institution: str
    country: str
    department: Optional[str]
    confidence: float


@dataclass
class InstitutionalConnection:
    """Connection between institutions"""
    institution_1: str
    institution_2: str
    connection_type: str  # "collaboration", "author_movement", "citation"
    strength: float
    evidence: List[str]


@dataclass
class DevelopmentStageIndicators:
    """Indicators of innovation development stage"""
    stage: str  # "research", "prototype", "pilot", "scaling", "commercial"
    confidence: float
    indicators: List[str]


@dataclass
class BusinessModelInfo:
    """Business model information extracted from text"""
    model_type: str  # "B2B", "B2C", "B2G", "NGO", "research"
    target_market: List[str]
    revenue_model: Optional[str]
    confidence: float


class EnhancedPublicationService:
    """Advanced publication analysis for competitive intelligence"""
    
    def __init__(self):
        self.supabase = get_supabase()
        
        # Institution patterns for African institutions
        self.african_institutions = {
            'South Africa': [
                'University of Cape Town', 'University of the Witwatersrand', 'Stellenbosch University',
                'University of KwaZulu-Natal', 'University of Pretoria', 'Rhodes University',
                'Council for Scientific and Industrial Research', 'CSIR'
            ],
            'Nigeria': [
                'University of Lagos', 'University of Ibadan', 'Obafemi Awolowo University',
                'University of Nigeria', 'Lagos Business School', 'Covenant University'
            ],
            'Kenya': [
                'University of Nairobi', 'Kenyatta University', 'Jomo Kenyatta University',
                'Strathmore University', 'Technical University of Kenya'
            ],
            'Ghana': [
                'University of Ghana', 'Kwame Nkrumah University of Science and Technology',
                'University of Cape Coast', 'Ashesi University'
            ],
            'Egypt': [
                'Cairo University', 'American University in Cairo', 'Alexandria University',
                'Ain Shams University', 'Helwan University'
            ],
            'Morocco': [
                'Mohammed V University', 'Hassan II University', 'Al Akhawayn University'
            ],
            'Tunisia': [
                'University of Tunis', 'University of Sfax', 'University of Carthage'
            ]
        }
        
        # Development stage indicators
        self.stage_indicators = {
            'research': [
                'theoretical', 'simulation', 'analysis', 'survey', 'literature review',
                'framework', 'model', 'algorithm', 'method', 'approach'
            ],
            'prototype': [
                'prototype', 'proof of concept', 'poc', 'demo', 'implementation',
                'system design', 'architecture', 'development', 'build'
            ],
            'pilot': [
                'pilot study', 'field test', 'trial', 'validation', 'evaluation',
                'testing', 'experiment', 'case study', 'real-world'
            ],
            'scaling': [
                'deployment', 'scaling', 'production', 'rollout', 'expansion',
                'commercialization', 'market', 'adoption', 'scale-up'
            ],
            'commercial': [
                'product', 'service', 'business', 'startup', 'company',
                'revenue', 'customers', 'market launch', 'commercial'
            ]
        }
        
        # Business model indicators
        self.business_model_indicators = {
            'B2B': [
                'enterprise', 'business-to-business', 'b2b', 'corporate',
                'companies', 'organizations', 'institutional'
            ],
            'B2C': [
                'consumer', 'business-to-consumer', 'b2c', 'individual',
                'personal', 'retail', 'end-user', 'customer'
            ],
            'B2G': [
                'government', 'public sector', 'municipal', 'policy',
                'regulation', 'administration', 'civic', 'public service'
            ],
            'NGO': [
                'non-profit', 'ngo', 'humanitarian', 'development',
                'social impact', 'community', 'charitable', 'foundation'
            ]
        }
    
    # ENHANCED METADATA EXTRACTION
    async def enhance_publication_metadata(self, batch_size: int = 100) -> Dict[str, Any]:
        """Extract enhanced metadata from all publications"""
        try:
            # Get publications in batches
            offset = 0
            total_processed = 0
            enhancement_results = {
                'author_affiliations': [],
                'institutional_connections': [],
                'development_stages': [],
                'business_models': [],
                'technology_extractions': []
            }
            
            while True:
                response = self.supabase.table('publications').select(
                    'id, title, abstract, content, authors, publication_date'
                ).range(offset, offset + batch_size - 1).execute()
                
                if not response.data:
                    break
                
                batch_results = await self._process_publication_batch(response.data)
                
                # Merge results
                for key in enhancement_results:
                    enhancement_results[key].extend(batch_results.get(key, []))
                
                total_processed += len(response.data)
                offset += batch_size
                
                logger.info(f"Processed {total_processed} publications for enhancement")
                
                if len(response.data) < batch_size:
                    break
            
            # Store enhanced metadata
            await self._store_enhanced_metadata(enhancement_results)
            
            return {
                'total_processed': total_processed,
                'enhancements': enhancement_results,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error enhancing publication metadata: {e}")
            return {}
    
    async def _process_publication_batch(self, publications: List[Dict]) -> Dict[str, List]:
        """Process a batch of publications for metadata enhancement"""
        results = {
            'author_affiliations': [],
            'institutional_connections': [],
            'development_stages': [],
            'business_models': [],
            'technology_extractions': []
        }
        
        for pub in publications:
            try:
                # Extract author affiliations
                affiliations = self._extract_author_affiliations(pub)
                results['author_affiliations'].extend(affiliations)
                
                # Detect development stage
                stage = self._detect_development_stage(pub)
                if stage:
                    results['development_stages'].append({
                        'publication_id': pub['id'],
                        'stage_info': stage
                    })
                
                # Extract business model info
                business_model = self._extract_business_model(pub)
                if business_model:
                    results['business_models'].append({
                        'publication_id': pub['id'],
                        'business_model': business_model
                    })
                
                # Extract technologies and methods
                technologies = self._extract_technologies(pub)
                if technologies:
                    results['technology_extractions'].append({
                        'publication_id': pub['id'],
                        'technologies': technologies
                    })
                
            except Exception as e:
                logger.error(f"Error processing publication {pub.get('id')}: {e}")
                continue
        
        # Extract institutional connections from affiliations
        results['institutional_connections'] = self._identify_institutional_connections(
            results['author_affiliations']
        )
        
        return results
    
    def _extract_author_affiliations(self, publication: Dict) -> List[AuthorAffiliation]:
        """Extract author affiliation information"""
        affiliations = []
        
        try:
            authors = publication.get('authors', [])
            abstract = publication.get('abstract', '')
            content = publication.get('content', '')
            
            # Look for affiliation patterns in abstract and content
            text = abstract + ' ' + content
            
            # Pattern for author affiliations: "Author Name1, Institution1, Country1"
            affiliation_patterns = [
                r'([A-Z][a-z]+ [A-Z][a-z]+)[\s,]*([A-Z][^,]+)[\s,]*([A-Z][a-z]+)',
                r'(\w+\s+\w+).*?University of (\w+)',
                r'(\w+\s+\w+).*?(University|Institute|College) of ([^,\n]+)'
            ]
            
            for author in authors:
                if isinstance(author, str):
                    # Try to find institution for this author
                    institution, country = self._match_author_to_institution(author, text)
                    
                    if institution:
                        affiliations.append(AuthorAffiliation(
                            author_name=author,
                            institution=institution,
                            country=country or 'Unknown',
                            department=None,
                            confidence=0.8
                        ))
            
            return affiliations
            
        except Exception as e:
            logger.error(f"Error extracting author affiliations: {e}")
            return []
    
    def _match_author_to_institution(self, author: str, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Match author to institution using patterns"""
        try:
            author_lower = author.lower()
            text_lower = text.lower()
            
            # Check if author appears near institution names
            for country, institutions in self.african_institutions.items():
                for institution in institutions:
                    inst_lower = institution.lower()
                    
                    # Look for author name within 100 characters of institution
                    inst_pos = text_lower.find(inst_lower)
                    if inst_pos != -1:
                        author_pos = text_lower.find(author_lower)
                        
                        if author_pos != -1 and abs(inst_pos - author_pos) < 100:
                            return institution, country
            
            # Generic university pattern matching
            university_pattern = r'university of (\w+)'
            matches = re.finditer(university_pattern, text_lower)
            
            for match in matches:
                university = match.group(0).title()
                location = match.group(1).title()
                
                # Check if author appears near this university
                match_pos = match.start()
                author_pos = text_lower.find(author_lower)
                
                if author_pos != -1 and abs(match_pos - author_pos) < 150:
                    # Try to determine country
                    country = self._guess_country_from_location(location)
                    return university, country
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error matching author to institution: {e}")
            return None, None
    
    def _guess_country_from_location(self, location: str) -> str:
        """Guess country from location string"""
        location_lower = location.lower()
        
        # Simple mapping of common locations to countries
        location_map = {
            'cape town': 'South Africa', 'johannesburg': 'South Africa', 'durban': 'South Africa',
            'lagos': 'Nigeria', 'abuja': 'Nigeria', 'ibadan': 'Nigeria',
            'nairobi': 'Kenya', 'mombasa': 'Kenya',
            'accra': 'Ghana', 'kumasi': 'Ghana',
            'cairo': 'Egypt', 'alexandria': 'Egypt',
            'casablanca': 'Morocco', 'rabat': 'Morocco',
            'tunis': 'Tunisia'
        }
        
        return location_map.get(location_lower, 'Unknown')
    
    def _identify_institutional_connections(self, affiliations: List[AuthorAffiliation]) -> List[InstitutionalConnection]:
        """Identify connections between institutions"""
        connections = []
        
        try:
            # Group affiliations by publication
            pub_affiliations = defaultdict(list)
            for affiliation in affiliations:
                # We need publication_id - this would need to be added to the affiliation data structure
                pass  # TODO: Implement when affiliation structure includes publication_id
            
            # For now, identify connections based on co-authorship
            institutions = defaultdict(set)
            for affiliation in affiliations:
                institutions[affiliation.institution].add(affiliation.author_name)
            
            # Find institutions that share authors
            inst_list = list(institutions.keys())
            for i, inst1 in enumerate(inst_list):
                for inst2 in inst_list[i+1:]:
                    shared_authors = institutions[inst1].intersection(institutions[inst2])
                    
                    if shared_authors:
                        connection = InstitutionalConnection(
                            institution_1=inst1,
                            institution_2=inst2,
                            connection_type="author_movement",
                            strength=len(shared_authors),
                            evidence=list(shared_authors)
                        )
                        connections.append(connection)
            
            return connections
            
        except Exception as e:
            logger.error(f"Error identifying institutional connections: {e}")
            return []
    
    def _detect_development_stage(self, publication: Dict) -> Optional[DevelopmentStageIndicators]:
        """Detect development stage from publication content"""
        try:
            title = publication.get('title', '').lower()
            abstract = publication.get('abstract', '').lower()
            content = publication.get('content', '').lower()
            
            text = title + ' ' + abstract + ' ' + content
            
            stage_scores = {}
            stage_evidence = defaultdict(list)
            
            # Score each stage based on indicator presence
            for stage, indicators in self.stage_indicators.items():
                score = 0
                for indicator in indicators:
                    count = text.count(indicator.lower())
                    if count > 0:
                        score += count
                        stage_evidence[stage].append(f"{indicator} ({count}x)")
                
                stage_scores[stage] = score
            
            # Determine most likely stage
            if not stage_scores or max(stage_scores.values()) == 0:
                return None
            
            best_stage = max(stage_scores, key=stage_scores.get)
            confidence = stage_scores[best_stage] / sum(stage_scores.values())
            
            return DevelopmentStageIndicators(
                stage=best_stage,
                confidence=confidence,
                indicators=stage_evidence[best_stage]
            )
            
        except Exception as e:
            logger.error(f"Error detecting development stage: {e}")
            return None
    
    def _extract_business_model(self, publication: Dict) -> Optional[BusinessModelInfo]:
        """Extract business model information"""
        try:
            title = publication.get('title', '').lower()
            abstract = publication.get('abstract', '').lower()
            content = publication.get('content', '').lower()
            
            text = title + ' ' + abstract + ' ' + content
            
            model_scores = {}
            
            # Score each business model type
            for model_type, indicators in self.business_model_indicators.items():
                score = 0
                for indicator in indicators:
                    score += text.count(indicator.lower())
                model_scores[model_type] = score
            
            if not model_scores or max(model_scores.values()) == 0:
                return None
            
            best_model = max(model_scores, key=model_scores.get)
            confidence = model_scores[best_model] / sum(model_scores.values())
            
            # Extract target market information
            target_markets = self._extract_target_markets(text)
            
            return BusinessModelInfo(
                model_type=best_model,
                target_market=target_markets,
                revenue_model=None,  # Could be enhanced
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error extracting business model: {e}")
            return None
    
    def _extract_target_markets(self, text: str) -> List[str]:
        """Extract target market information from text"""
        markets = []
        
        market_indicators = {
            'healthcare': ['health', 'medical', 'hospital', 'clinic', 'patient'],
            'agriculture': ['farm', 'crop', 'agriculture', 'food', 'harvest'],
            'education': ['education', 'school', 'student', 'learning', 'teaching'],
            'finance': ['financial', 'banking', 'payment', 'money', 'credit'],
            'energy': ['energy', 'power', 'electricity', 'renewable', 'solar'],
            'transportation': ['transport', 'vehicle', 'traffic', 'mobility', 'logistics']
        }
        
        for market, indicators in market_indicators.items():
            if any(indicator in text for indicator in indicators):
                markets.append(market)
        
        return markets
    
    def _extract_technologies(self, publication: Dict) -> List[Dict[str, Any]]:
        """Extract specific technologies and methods"""
        try:
            title = publication.get('title', '').lower()
            abstract = publication.get('abstract', '').lower()
            content = publication.get('content', '').lower()
            
            text = title + ' ' + abstract + ' ' + content
            
            # Technology categories and indicators
            tech_categories = {
                'machine_learning': [
                    'machine learning', 'deep learning', 'neural network', 'cnn', 'rnn',
                    'transformer', 'bert', 'gpt', 'random forest', 'svm', 'gradient boosting'
                ],
                'nlp': [
                    'natural language processing', 'nlp', 'text mining', 'sentiment analysis',
                    'named entity recognition', 'language model', 'text classification'
                ],
                'computer_vision': [
                    'computer vision', 'image processing', 'object detection', 'face recognition',
                    'image classification', 'opencv', 'yolo', 'resnet'
                ],
                'blockchain': [
                    'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'smart contract',
                    'decentralized', 'distributed ledger'
                ],
                'iot': [
                    'internet of things', 'iot', 'sensor', 'embedded system', 'wireless',
                    'mqtt', 'zigbee', 'lora'
                ],
                'data_science': [
                    'data science', 'big data', 'analytics', 'visualization', 'pandas',
                    'numpy', 'scikit-learn', 'tensorflow', 'pytorch'
                ]
            }
            
            detected_technologies = []
            
            for category, indicators in tech_categories.items():
                for indicator in indicators:
                    if indicator in text:
                        detected_technologies.append({
                            'technology': indicator,
                            'category': category,
                            'confidence': 0.9 if indicator in title or indicator in abstract else 0.7
                        })
            
            return detected_technologies
            
        except Exception as e:
            logger.error(f"Error extracting technologies: {e}")
            return []
    
    async def _store_enhanced_metadata(self, enhancement_results: Dict[str, List]):
        """Store enhanced metadata in database"""
        try:
            # Store author affiliations
            if enhancement_results['author_affiliations']:
                affiliation_data = []
                for affiliation in enhancement_results['author_affiliations']:
                    affiliation_data.append({
                        'author_name': affiliation.author_name,
                        'institution': affiliation.institution,
                        'country': affiliation.country,
                        'department': affiliation.department,
                        'confidence': affiliation.confidence,
                        'extracted_at': datetime.now().isoformat()
                    })
                
                if affiliation_data:
                    self.supabase.table('author_affiliations').insert(affiliation_data).execute()
                    logger.info(f"Stored {len(affiliation_data)} author affiliations")
            
            # Store institutional connections
            if enhancement_results['institutional_connections']:
                connection_data = []
                for connection in enhancement_results['institutional_connections']:
                    connection_data.append({
                        'institution_1': connection.institution_1,
                        'institution_2': connection.institution_2,
                        'connection_type': connection.connection_type,
                        'strength': connection.strength,
                        'evidence': connection.evidence,
                        'identified_at': datetime.now().isoformat()
                    })
                
                if connection_data:
                    self.supabase.table('institutional_connections').insert(connection_data).execute()
                    logger.info(f"Stored {len(connection_data)} institutional connections")
            
            # Update publications with enhanced metadata
            for stage_info in enhancement_results['development_stages']:
                pub_id = stage_info['publication_id']
                stage = stage_info['stage_info']
                
                self.supabase.table('publications').update({
                    'development_stage': stage.stage,
                    'stage_confidence': stage.confidence,
                    'stage_indicators': stage.indicators
                }).eq('id', pub_id).execute()
            
            for bm_info in enhancement_results['business_models']:
                pub_id = bm_info['publication_id']
                business_model = bm_info['business_model']
                
                self.supabase.table('publications').update({
                    'business_model': business_model.model_type,
                    'target_markets': business_model.target_market,
                    'business_model_confidence': business_model.confidence
                }).eq('id', pub_id).execute()
            
            for tech_info in enhancement_results['technology_extractions']:
                pub_id = tech_info['publication_id']
                technologies = tech_info['technologies']
                
                self.supabase.table('publications').update({
                    'extracted_technologies': technologies
                }).eq('id', pub_id).execute()
            
            logger.info("Enhanced metadata storage completed")
            
        except Exception as e:
            logger.error(f"Error storing enhanced metadata: {e}")
    
    # ANALYTICS AND REPORTING
    async def generate_publication_intelligence_report(self) -> Dict[str, Any]:
        """Generate comprehensive publication intelligence report"""
        try:
            # Get enhanced publication data
            pubs_response = self.supabase.table('publications').select(
                'id, title, development_stage, business_model, target_markets, extracted_technologies, publication_date'
            ).execute()
            
            publications = pubs_response.data if pubs_response.data else []
            
            # Get institutional data
            affiliations_response = self.supabase.table('author_affiliations').select('*').execute()
            affiliations = affiliations_response.data if affiliations_response.data else []
            
            connections_response = self.supabase.table('institutional_connections').select('*').execute()
            connections = connections_response.data if connections_response.data else []
            
            # Analyze patterns
            stage_distribution = Counter(pub.get('development_stage') for pub in publications if pub.get('development_stage'))
            model_distribution = Counter(pub.get('business_model') for pub in publications if pub.get('business_model'))
            
            # Technology trends
            all_technologies = []
            for pub in publications:
                technologies = pub.get('extracted_technologies', [])
                if isinstance(technologies, list):
                    all_technologies.extend([tech.get('technology') for tech in technologies if isinstance(tech, dict)])
            
            tech_trends = Counter(all_technologies).most_common(20)
            
            # Institutional analysis
            institution_countries = Counter(aff['country'] for aff in affiliations)
            top_institutions = Counter(aff['institution'] for aff in affiliations).most_common(15)
            
            # Collaboration analysis
            collaboration_strength = sum(conn['strength'] for conn in connections)
            avg_collaboration = collaboration_strength / max(len(connections), 1)
            
            return {
                'overview': {
                    'total_publications_analyzed': len(publications),
                    'publications_with_stage_info': len([p for p in publications if p.get('development_stage')]),
                    'publications_with_business_model': len([p for p in publications if p.get('business_model')]),
                    'total_author_affiliations': len(affiliations),
                    'institutional_connections': len(connections)
                },
                'development_stages': dict(stage_distribution),
                'business_models': dict(model_distribution),
                'technology_trends': [{'technology': tech, 'count': count} for tech, count in tech_trends],
                'institutional_landscape': {
                    'countries': dict(institution_countries),
                    'top_institutions': [{'institution': inst, 'publications': count} for inst, count in top_institutions],
                    'collaboration_metrics': {
                        'total_collaborations': len(connections),
                        'average_collaboration_strength': round(avg_collaboration, 2)
                    }
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating publication intelligence report: {e}")
            return {}


# Global service instance
enhanced_publication_service = EnhancedPublicationService()