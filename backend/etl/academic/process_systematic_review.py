#!/usr/bin/env python3
"""
Systematic Review Data Processor for TAIFA-FIALA
Process existing systematic review of AI R&D in Africa from CSV data
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger
from services.database_service import DatabaseService
from services.deduplication_service import DeduplicationService

from services.etl_deduplication import check_and_handle_publication_duplicates


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
                'venue': venue if venue != 'nan' else '',
                'citation_count': citation_count,
                'publication_date': pub_date,
                'year': year,
                'project_domain': project_domain if project_domain != 'nan' else '',
                'funding_source': funding_source if funding_source != 'nan' else '',
                'ai_techniques': ai_techniques if ai_techniques != 'nan' else '',
                'geographic_scope': geographic_scope if geographic_scope != 'nan' else '',
                'project_duration': project_duration if project_duration != 'nan' else '',
                'key_outcomes': key_outcomes if key_outcomes != 'nan' else '',
                'keywords': keywords,
                'african_entities': african_entities,
                'african_relevance_score': african_score,
                'ai_relevance_score': ai_score,
                'source': 'Systematic Review',
                'data_type': 'African AI R&D Study'
            }
            
        except Exception as e:
            logger.error(f"Error processing study row: {e}")
            return None
    
    def parse_authors(self, authors_str: str) -> List[str]:
        """Parse authors string into list"""
        if not authors_str or authors_str == 'nan':
            return []
        
        # Split by common delimiters
        authors = re.split(r'[,;&]', authors_str)
        
        # Clean up author names
        cleaned_authors = []
        for author in authors:
            author = author.strip()
            if author and len(author) > 1:
                cleaned_authors.append(author)
        
        return cleaned_authors[:10]  # Limit to first 10 authors
    
    def parse_number(self, value) -> int:
        """Parse numeric value safely"""
        try:
            if pd.isna(value):
                return 0
            return int(float(value))
        except:
            return 0
    
    def parse_year(self, value) -> Optional[int]:
        """Parse year value safely"""
        try:
            if pd.isna(value):
                return None
            
            # Extract year from string if needed
            year_str = str(value).strip()
            year_match = re.search(r'\b(20\d{2})\b', year_str)
            
            if year_match:
                return int(year_match.group(1))
            
            # Try direct conversion
            year = int(float(value))
            if 2000 <= year <= 2030:
                return year
            
            return None
        except:
            return None
    
    def extract_keywords(self, project_domain: str, ai_techniques: str) -> List[str]:
        """Extract keywords from project domain and AI techniques"""
        keywords = []
        
        # Domain keywords
        if project_domain and project_domain != 'nan':
            domain_terms = [
                'healthcare', 'agriculture', 'finance', 'education', 'transportation',
                'energy', 'environment', 'security', 'governance', 'development',
                'covid', 'malaria', 'tuberculosis', 'hiv', 'drug discovery',
                'climate', 'sustainable', 'mobile', 'social', 'economic'
            ]
            
            text_lower = project_domain.lower()
            for term in domain_terms:
                if term in text_lower:
                    keywords.append(term.title())
        
        # AI technique keywords
        if ai_techniques and ai_techniques != 'nan':
            ai_terms = [
                'machine learning', 'deep learning', 'neural network', 'computer vision',
                'natural language processing', 'reinforcement learning', 'classification',
                'regression', 'clustering', 'recommendation', 'automation', 'robotics',
                'prediction', 'optimization', 'detection', 'nlp'
            ]
            
            text_lower = ai_techniques.lower()
            for term in ai_terms:
                if term in text_lower:
                    keywords.append(term.title())
        
        return list(set(keywords))
    
    def extract_african_entities(self, geographic_scope: str, venue: str, authors: List[str]) -> List[str]:
        """Extract African entities from various fields"""
        entities = []
        
        african_countries = [
            "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", 
            "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros", 
            "Congo", "Democratic Republic of Congo", "Djibouti", "Egypt", 
            "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", 
            "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", 
            "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", 
            "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", 
            "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", 
            "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", 
            "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
        ]
        
        # Check geographic scope
        if geographic_scope and geographic_scope != 'nan':
            text = geographic_scope.lower()
            for country in african_countries:
                if country.lower() in text:
                    entities.append(country)
            
            # Check for regional terms
            african_terms = ['africa', 'african', 'sub-saharan', 'sahel', 'maghreb']
            for term in african_terms:
                if term in text:
                    entities.append(term.title())
        
        # Check venue for African affiliations
        if venue and venue != 'nan':
            text = venue.lower()
            for country in african_countries:
                if country.lower() in text:
                    entities.append(country)
        
        return list(set(entities))
    
    def calculate_african_relevance(self, title: str, geographic_scope: str, venue: str, authors: List[str]) -> float:
        """Calculate African relevance score"""
        score = 0.0
        text = f"{title} {geographic_scope} {venue} {' '.join(authors)}".lower()
        
        african_countries = [
            "south africa", "nigeria", "kenya", "egypt", "ghana", "ethiopia",
            "morocco", "algeria", "tunisia", "uganda", "tanzania", "zimbabwe"
        ]
        
        # Check for African countries
        for country in african_countries:
            if country in text:
                score += 0.3
        
        # Check for African terms
        african_terms = ['africa', 'african', 'sub-saharan']
        for term in african_terms:
            if term in text:
                score += 0.4
        
        return min(score, 1.0)
    
    def calculate_ai_relevance(self, title: str, project_domain: str, ai_techniques: str) -> float:
        """Calculate AI relevance score"""
        score = 0.0
        text = f"{title} {project_domain} {ai_techniques}".lower()
        
        ai_terms = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'computer vision', 'natural language processing'
        ]
        
        for term in ai_terms:
            if term in text:
                score += 0.3
        
        return min(score, 1.0)
    
    def get_summary_statistics(self, studies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics of processed studies"""
        if not studies:
            return {}
        
        total_studies = len(studies)
        
        # Year distribution
        years = {}
        for study in studies:
            if study['year']:
                years[study['year']] = years.get(study['year'], 0) + 1
        
        # Domain distribution
        domains = {}
        for study in studies:
            domain = study['project_domain']
            if domain:
                # Split multi-line domains
                domain_parts = domain.split('\n')
                for part in domain_parts:
                    part = part.strip('- ').strip()
                    if part and len(part) > 2:
                        domains[part] = domains.get(part, 0) + 1
        
        # African entities
        all_entities = []
        for study in studies:
            all_entities.extend(study['african_entities'])
        
        entity_count = {}
        for entity in all_entities:
            entity_count[entity] = entity_count.get(entity, 0) + 1
        
        # Keywords
        all_keywords = []
        for study in studies:
            all_keywords.extend(study['keywords'])
        
        keyword_count = {}
        for keyword in all_keywords:
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        # Average scores
        avg_african_score = sum(s['african_relevance_score'] for s in studies) / total_studies
        avg_ai_score = sum(s['ai_relevance_score'] for s in studies) / total_studies
        avg_citations = sum(s['citation_count'] for s in studies) / total_studies
        
        return {
            'total_studies': total_studies,
            'year_distribution': dict(sorted(years.items(), reverse=True)),
            'top_domains': dict(list(sorted(domains.items(), key=lambda x: x[1], reverse=True))[:10]),
            'top_african_entities': dict(list(sorted(entity_count.items(), key=lambda x: x[1], reverse=True))[:10]),
            'top_keywords': dict(list(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))[:10]),
            'avg_african_relevance': avg_african_score,
            'avg_ai_relevance': avg_ai_score,
            'avg_citations': avg_citations
        }


async def main():
    """Main function to process systematic review data"""
    logger.info("🔬 Starting Systematic Review Data Processing...")
    
    csv_path = "/Users/drjforrest/dev/devprojects/TAIFA-FIALA/data/Elicit - extract-results-review-b8c80b4e-9037-459f-9afb-d4c8b22f8553.csv"
    
    processor = SystematicReviewProcessor(csv_path)
    
    # Load data
    data = processor.load_data()
    if data is None:
        logger.error("Failed to load data")
        return
    
    # Process studies
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
        logger.info("📝 Next steps:")
        logger.info("   1. Integrate with ArXiv + PubMed + Scholar data")
        logger.info("   2. Store all studies in database")
        logger.info("   3. Build unified search and discovery system")
        logger.info("   4. Launch public portal with real data")
        
        return studies
        
    else:
        logger.warning("⚠️  No studies were processed successfully")
        return []


if __name__ == "__main__":
    studies = asyncio.run(main())