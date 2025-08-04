#!/usr/bin/env python3
"""
Systematic Review Data Processor for TAIFA-FIALA
Process existing systematic review of AI R&D in Africa from CSV data
"""

import pandas as pd
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

from services.database_service import DatabaseService
from services.deduplication_service import DeduplicationService
from utils.etl_deduplication import check_and_handle_publication_duplicates


class SystematicReviewProcessor:
    """Process systematic review data from CSV export"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = None
        
        # Initialize database and deduplication services
        self.db_service = DatabaseService()
        self.dedup_service = DeduplicationService()
        
    def load_data(self) -> pd.DataFrame:
        """Load systematic review data from CSV"""
        try:
            logger.info(f"Loading systematic review data from {self.csv_path}")
            
            # Read CSV with proper encoding
            self.data = pd.read_csv(self.csv_path, encoding='utf-8-sig')
            
            logger.info(f"Loaded {len(self.data)} studies from systematic review")
            logger.info(f"Columns: {list(self.data.columns)}")
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading systematic review data: {e}")
            return None
    
    def clean_and_process_data(self) -> List[Dict[str, Any]]:
        """Clean and process the systematic review data"""
        if self.data is None:
            logger.error("No data loaded. Call load_data() first.")
            return []
        
        processed_studies = []
        
        for idx, row in self.data.iterrows():
            try:
                study_data = self.process_study_row(row)
                if study_data:
                    processed_studies.append(study_data)
            except Exception as e:
                logger.error(f"Error processing row {idx}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_studies)} studies")
        return processed_studies
    
    def process_study_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Process a single study row"""
        try:
            # Basic information
            title = str(row.get('Title', '')).strip()
            if not title or title == 'nan':
                return None
            
            authors = self.parse_authors(str(row.get('Authors', '')))
            doi = str(row.get('DOI', '')).strip()
            doi_link = str(row.get('DOI link', '')).strip()
            venue = str(row.get('Venue', '')).strip()
            
            # Citation and year
            citation_count = self.parse_number(row.get('Citation count', 0))
            year = self.parse_year(row.get('Year', ''))
            
            # Research characteristics
            project_domain = str(row.get('Project Domain/Focus', '')).strip()
            funding_source = str(row.get('Funding Source/Collaboration', '')).strip()
            ai_techniques = str(row.get('AI/Machine Learning Techniques Used', '')).strip()
            geographic_scope = str(row.get('Geographic Scope', '')).strip()
            project_duration = str(row.get('Project Duration/Timeline', '')).strip()
            key_outcomes = str(row.get('Key Project Outcomes', '')).strip()
            
            # Extract keywords and entities
            keywords = self.extract_keywords(project_domain, ai_techniques)
            african_entities = self.extract_african_entities(geographic_scope, venue, authors)
            
            # Calculate relevance scores
            african_score = self.calculate_african_relevance(title, geographic_scope, venue, authors)
            ai_score = self.calculate_ai_relevance(title, project_domain, ai_techniques)
            
            # Create publication date
            pub_date = None
            if year:
                try:
                    pub_date = datetime(year, 1, 1)
                except:
                    pass
            
            return {
                'title': title,
                'authors': authors,
                'doi': doi if doi != 'nan' else '',
                'url': doi_link if doi_link != 'nan' else '',
                'venue': venue,
                'citation_count': citation_count,
                'year': year,
                'project_domain': project_domain,
                'funding_source': funding_source,
                'ai_techniques': ai_techniques,
                'geographic_scope': geographic_scope,
                'project_duration': project_duration,
                'key_outcomes': key_outcomes,
                'keywords': keywords,
                'african_entities': african_entities,
                'african_relevance_score': african_score,
                'ai_relevance_score': ai_score,
                'publication_date': pub_date
            }
            
        except Exception as e:
            logger.error(f"Error processing study row: {e}")
            return None
    
    def parse_authors(self, authors_str: str) -> List[str]:
        """Parse authors string into list"""
        if not authors_str or authors_str == 'nan':
            return []
        
        # Split by common delimiters
        authors = re.split(r'[,;]|and\s+', authors_str)
        
        # Clean up each author name
        cleaned_authors = []
        for author in authors:
            author = author.strip()
            if author and author != 'nan':
                cleaned_authors.append(author)
        
        return cleaned_authors
    
    def parse_number(self, value) -> int:
        """Parse numeric value safely"""
        try:
            return int(float(str(value)))
        except:
            return 0
    
    def parse_year(self, value) -> Optional[int]:
        """Parse year value safely"""
        try:
            year_str = str(value).strip()
            if year_str == 'nan' or not year_str:
                return None
            
            # Extract 4-digit year
            year_match = re.search(r'\b(19|20)\d{2}\b', year_str)
            if year_match:
                year = int(year_match.group())
                if 1990 <= year <= 2030:  # Reasonable range
                    return year
            
            # Try direct conversion
            year = int(float(year_str))
            if 1990 <= year <= 2030:
                return year
                
        except:
            pass
        
        return None
    
    def extract_keywords(self, project_domain: str, ai_techniques: str) -> List[str]:
        """Extract keywords from project domain and AI techniques"""
        keywords = set()
        
        # Common AI/ML keywords
        ai_keywords = [
            'machine learning', 'deep learning', 'neural network', 'artificial intelligence',
            'computer vision', 'natural language processing', 'nlp', 'reinforcement learning',
            'supervised learning', 'unsupervised learning', 'classification', 'regression',
            'clustering', 'recommendation system', 'predictive modeling', 'data mining',
            'big data', 'analytics', 'algorithm', 'model', 'training', 'prediction'
        ]
        
        # Extract from project domain
        if project_domain and project_domain != 'nan':
            domain_lower = project_domain.lower()
            for keyword in ai_keywords:
                if keyword in domain_lower:
                    keywords.add(keyword)
        
        # Extract from AI techniques
        if ai_techniques and ai_techniques != 'nan':
            techniques_lower = ai_techniques.lower()
            for keyword in ai_keywords:
                if keyword in techniques_lower:
                    keywords.add(keyword)
        
        # Add domain-specific keywords
        domain_keywords = ['healthcare', 'agriculture', 'education', 'finance', 'transportation']
        combined_text = f"{project_domain} {ai_techniques}".lower()
        
        for keyword in domain_keywords:
            if keyword in combined_text:
                keywords.add(keyword)
        
        return list(keywords)
    
    def extract_african_entities(self, geographic_scope: str, venue: str, authors: List[str]) -> List[str]:
        """Extract African entities from various fields"""
        entities = set()
        
        # African countries and regions
        african_entities = [
            'africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana', 'ethiopia',
            'tanzania', 'uganda', 'rwanda', 'botswana', 'zambia', 'zimbabwe', 'morocco',
            'egypt', 'tunisia', 'senegal', 'mali', 'burkina faso', 'ivory coast', 'cameroon',
            'madagascar', 'mozambique', 'angola', 'sudan', 'algeria', 'libya', 'chad',
            'niger', 'somalia', 'malawi', 'benin', 'togo', 'sierra leone', 'liberia',
            'guinea', 'gambia', 'mauritania', 'namibia', 'lesotho', 'swaziland', 'djibouti',
            'eritrea', 'comoros', 'seychelles', 'mauritius', 'cape verde'
        ]
        
        # Check geographic scope
        if geographic_scope and geographic_scope != 'nan':
            scope_lower = geographic_scope.lower()
            for entity in african_entities:
                if entity in scope_lower:
                    entities.add(entity.title())
        
        # Check venue
        if venue and venue != 'nan':
            venue_lower = venue.lower()
            for entity in african_entities:
                if entity in venue_lower:
                    entities.add(entity.title())
        
        # Check authors (simplified - look for African-sounding names or affiliations)
        for author in authors:
            author_lower = author.lower()
            for entity in african_entities:
                if entity in author_lower:
                    entities.add(entity.title())
        
        return list(entities)
    
    def calculate_african_relevance(self, title: str, geographic_scope: str, venue: str, authors: List[str]) -> float:
        """Calculate African relevance score"""
        score = 0.0
        
        # Check title
        if title:
            title_lower = title.lower()
            if any(term in title_lower for term in ['africa', 'african']):
                score += 0.4
        
        # Check geographic scope
        if geographic_scope and geographic_scope != 'nan':
            scope_lower = geographic_scope.lower()
            if any(term in scope_lower for term in ['africa', 'african']):
                score += 0.3
        
        # Check venue
        if venue and venue != 'nan':
            venue_lower = venue.lower()
            if any(term in venue_lower for term in ['africa', 'african']):
                score += 0.2
        
        # Check authors (simplified)
        author_text = ' '.join(authors).lower()
        if any(term in author_text for term in ['africa', 'african']):
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_ai_relevance(self, title: str, project_domain: str, ai_techniques: str) -> float:
        """Calculate AI relevance score"""
        score = 0.0
        
        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning', 'neural network',
            'computer vision', 'natural language processing', 'nlp', 'ai', 'ml', 'algorithm'
        ]
        
        # Check title
        if title:
            title_lower = title.lower()
            for term in ai_terms:
                if term in title_lower:
                    score += 0.3
                    break
        
        # Check project domain
        if project_domain and project_domain != 'nan':
            domain_lower = project_domain.lower()
            for term in ai_terms:
                if term in domain_lower:
                    score += 0.4
                    break
        
        # Check AI techniques
        if ai_techniques and ai_techniques != 'nan':
            techniques_lower = ai_techniques.lower()
            for term in ai_terms:
                if term in techniques_lower:
                    score += 0.3
                    break
        
        return min(score, 1.0)
    
    def get_summary_statistics(self, studies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics of processed studies"""
        if not studies:
            return {}
        
        # Basic counts
        total_studies = len(studies)
        
        # Relevance scores
        african_scores = [s.get('african_relevance_score', 0) for s in studies]
        ai_scores = [s.get('ai_relevance_score', 0) for s in studies]
        citations = [s.get('citation_count', 0) for s in studies]
        
        avg_african_relevance = sum(african_scores) / len(african_scores) if african_scores else 0
        avg_ai_relevance = sum(ai_scores) / len(ai_scores) if ai_scores else 0
        avg_citations = sum(citations) / len(citations) if citations else 0
        
        # Year distribution
        years = [s.get('year') for s in studies if s.get('year')]
        year_distribution = {}
        for year in years:
            year_distribution[year] = year_distribution.get(year, 0) + 1
        
        # Top domains
        domains = [s.get('project_domain', '') for s in studies if s.get('project_domain')]
        domain_counts = {}
        for domain in domains:
            if domain and domain != 'nan':
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top African entities
        all_entities = []
        for study in studies:
            all_entities.extend(study.get('african_entities', []))
        
        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        top_african_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top keywords
        all_keywords = []
        for study in studies:
            all_keywords.extend(study.get('keywords', []))
        
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return {
            'total_studies': total_studies,
            'avg_african_relevance': avg_african_relevance,
            'avg_ai_relevance': avg_ai_relevance,
            'avg_citations': avg_citations,
            'year_distribution': dict(sorted(year_distribution.items())),
            'top_domains': top_domains,
            'top_african_entities': top_african_entities,
            'top_keywords': top_keywords
        }


async def process_systematic_review_data(csv_path: str = None) -> List[Dict[str, Any]]:
    """Main function to process systematic review data with deduplication"""
    
    if not csv_path:
        csv_path = "/Users/drjforrest/dev/devprojects/TAIFA-FIALA/data/Elicit - extract-results-review-b8c80b4e-9037-459f-9afb-d4c8b22f8553.csv"
    
    logger.info("🔬 Starting Systematic Review Data Processing...")
    
    # Initialize processor
    processor = SystematicReviewProcessor(csv_path)
    
    # Load and process data
    if not processor.load_data():
        logger.error("Failed to load systematic review data")
        return []
    
    studies = processor.clean_and_process_data()
    
    if studies:
        logger.info(f"✅ Successfully processed {len(studies)} studies")
        
        # Store studies in database with deduplication
        try:
            logger.info("💾 Storing studies in Supabase database with deduplication...")
            logger.info(f"📊 About to store {len(studies)} studies")
            
            stored_publications = []
            for study in studies:
                try:
                    # Convert study to publication format
                    publication_data = {
                        'title': study.get('title', ''),
                        'publication_type': 'journal_paper',
                        'publication_date': study.get('publication_date'),
                        'year': study.get('year'),
                        'doi': study.get('doi', ''),
                        'url': study.get('url', ''),
                        'venue': study.get('venue', ''),
                        'abstract': study.get('abstract', ''),
                        'keywords': study.get('keywords', []),
                        'source': 'systematic_review',
                        'source_id': f"sr_{hash(study.get('title', ''))}_{study.get('year', 'unknown')}",
                        'project_domain': study.get('project_domain', ''),
                        'ai_techniques': study.get('ai_techniques', ''),
                        'geographic_scope': study.get('geographic_scope', ''),
                        'funding_source': study.get('funding_source', ''),
                        'key_outcomes': study.get('key_outcomes', ''),
                        'african_relevance_score': study.get('african_relevance_score', 0.0),
                        'ai_relevance_score': study.get('ai_relevance_score', 0.0),
                        'african_entities': study.get('african_entities', []),
                        'data_type': 'Academic Paper'
                    }
                    
                    # Store with deduplication
                    success, stored_record, action = await check_and_handle_publication_duplicates(
                        publication_data,
                        processor.db_service,
                        processor.dedup_service,
                        action='reject'  # Can be configured: reject, merge, update, link
                    )
                    
                    if success and stored_record:
                        stored_publications.append(stored_record)
                        logger.info(f"✅ Stored systematic review study ({action}): {study.get('title', 'Unknown')[:50]}...")
                    elif not success:
                        logger.info(f"ℹ️ Systematic review study handling ({action}): {study.get('title', 'Unknown')[:50]}...")
                        
                except Exception as study_error:
                    logger.error(f"❌ Error storing individual study: {study_error}")
                    continue
            
            logger.info(f"✅ Stored {len(stored_publications)}/{len(studies)} studies in database")
            
        except Exception as e:
            logger.error(f"❌ Failed to store studies in database: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            stored_publications = []
        
        # Show sample studies
        logger.info("\n📚 Sample African AI R&D Studies:")
        for i, study in enumerate(studies[:5], 1):
            logger.info(f"\n{i}. {study['title']}")
            logger.info(f"   Authors: {', '.join(study['authors'][:3])}{'...' if len(study['authors']) > 3 else ''}")
            logger.info(f"   Venue: {study['venue']}")
            if study['year']:
                logger.info(f"   Year: {study['year']}")
            logger.info(f"   Citations: {study['citation_count']}")
            logger.info(f"   Domain: {study['project_domain'][:100]}...")
            logger.info(f"   Geographic Scope: {study['geographic_scope']}")
            logger.info(f"   AI Techniques: {study['ai_techniques'][:100]}...")
            logger.info(f"   African Score: {study['african_relevance_score']:.2f}")
            logger.info(f"   AI Score: {study['ai_relevance_score']:.2f}")
            logger.info(f"   Keywords: {study['keywords']}")
            logger.info(f"   African Entities: {study['african_entities']}")
            if study['url']:
                logger.info(f"   URL: {study['url']}")
            logger.info("-" * 100)
        
        # Show statistics
        stats = processor.get_summary_statistics(studies)
        
        logger.info(f"\n📊 Systematic Review Statistics:")
        logger.info(f"   Total Studies: {stats['total_studies']}")
        logger.info(f"   Average African Relevance: {stats['avg_african_relevance']:.3f}")
        logger.info(f"   Average AI Relevance: {stats['avg_ai_relevance']:.3f}")
        logger.info(f"   Average Citations: {stats['avg_citations']:.1f}")
        
        if stats['year_distribution']:
            logger.info(f"   Year Distribution: {dict(list(stats['year_distribution'].items())[:10])}")
        
        if stats['top_domains']:
            logger.info(f"   Top Domains: {stats['top_domains']}")
        
        if stats['top_african_entities']:
            logger.info(f"   Top African Entities: {stats['top_african_entities']}")
        
        if stats['top_keywords']:
            logger.info(f"   Top Keywords: {stats['top_keywords']}")
        
        logger.info("🎉 Systematic review data processing completed!")
        
        return studies
        
    else:
        logger.warning("⚠️  No studies were processed successfully")
        return []


if __name__ == "__main__":
    studies = asyncio.run(process_systematic_review_data())
