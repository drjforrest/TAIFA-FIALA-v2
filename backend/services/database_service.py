"""
Supabase Database Service for TAIFA-FIALA
Provides reusable database operations using Supabase client for Row Level Security
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from uuid import uuid4
from loguru import logger

from config.database import supabase
from models.schemas import (
    InnovationCreate, OrganizationCreate, IndividualCreate, 
    PublicationCreate, FundingCreate
)


class DatabaseService:
    """Centralized database service using Supabase client for RLS compliance"""
    
    def __init__(self):
        self.client = supabase
    
    def serialize_date(self, date_obj):
        """Helper function to serialize dates for JSON compatibility"""
        if date_obj is None:
            return None
        elif isinstance(date_obj, datetime):
            return date_obj.isoformat()
        elif isinstance(date_obj, date):
            return date_obj.isoformat()
        elif isinstance(date_obj, str):
            return date_obj
        else:
            return str(date_obj)
        
    # PUBLICATIONS
    async def create_publication(self, publication_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new publication record"""
        try:
            # Prepare publication data according to current schema
            publication_date = publication_data.get('publication_date')
            pub_record = {
                'id': str(uuid4()),
                'title': publication_data.get('title', ''),
                'abstract': publication_data.get('abstract'),
                'publication_type': publication_data.get('publication_type', 'journal_paper'),
                'publication_date': self.serialize_date(publication_date),
                'year': publication_data.get('year') or (publication_date.year if hasattr(publication_date, 'year') else None),
                'doi': publication_data.get('doi'),
                'url': publication_data.get('url'),
                'pdf_url': publication_data.get('pdf_url'),
                'journal': publication_data.get('journal') or publication_data.get('venue'),
                'venue': publication_data.get('venue'),
                'citation_count': publication_data.get('citation_count', 0),
                'project_domain': publication_data.get('project_domain'),
                'ai_techniques': publication_data.get('ai_techniques'),
                'geographic_scope': publication_data.get('geographic_scope'),
                'funding_source': publication_data.get('funding_source'),
                'key_outcomes': publication_data.get('key_outcomes'),
                'african_relevance_score': publication_data.get('african_relevance_score', 0.0),
                'ai_relevance_score': publication_data.get('ai_relevance_score', 0.0),
                'african_entities': publication_data.get('african_entities', []),
                'keywords': publication_data.get('keywords', []),
                'source': publication_data.get('source', 'systematic_review'),
                'source_id': publication_data.get('source_id') or publication_data.get('arxiv_id') or publication_data.get('pubmed_id'),
                'data_type': publication_data.get('data_type', 'Academic Paper'),
                'processed_at': datetime.utcnow().isoformat(),
                'verification_status': publication_data.get('verification_status', 'pending'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            pub_record = {k: v for k, v in pub_record.items() if v is not None}
            
            result = self.client.table('publications').insert(pub_record).execute()
            
            if result.data:
                logger.info(f"✅ Created publication: {publication_data.get('title', 'Unknown')[:50]}...")
                return result.data[0]
            else:
                logger.error(f"❌ Failed to create publication: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating publication: {e}")
            return None
    
    async def bulk_create_publications(self, publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bulk create multiple publications"""
        created_publications = []
        
        for pub_data in publications:
            result = await self.create_publication(pub_data)
            if result:
                created_publications.append(result)
        
        logger.info(f"✅ Bulk created {len(created_publications)}/{len(publications)} publications")
        return created_publications
    
    # INNOVATIONS
    async def create_innovation(self, innovation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new innovation record"""
        try:
            innovation_record = {
                'id': str(uuid4()),
                'title': innovation_data.get('title', ''),
                'description': innovation_data.get('description', ''),
                'innovation_type': innovation_data.get('innovation_type', 'software'),
                'domain': innovation_data.get('domain', 'other'),
                'ai_techniques_used': innovation_data.get('ai_techniques_used', []),
                'target_beneficiaries': innovation_data.get('target_beneficiaries'),
                'problem_addressed': innovation_data.get('problem_addressed') or innovation_data.get('problem_solved'),
                'solution_approach': innovation_data.get('solution_approach'),
                'development_stage': innovation_data.get('development_stage', 'concept'),
                'technology_stack': innovation_data.get('technology_stack', []) or innovation_data.get('tech_stack', []),
                'programming_languages': innovation_data.get('programming_languages', []),
                'datasets_used': innovation_data.get('datasets_used', []),
                'countries_deployed': innovation_data.get('countries_deployed', []),
                'target_countries': innovation_data.get('target_countries', []),
                'users_reached': innovation_data.get('users_reached', 0),
                'impact_metrics': innovation_data.get('impact_metrics', {}),
                'verification_status': innovation_data.get('verification_status', 'pending'),
                'visibility': innovation_data.get('visibility', 'public'),
                'demo_url': innovation_data.get('demo_url'),
                'github_url': innovation_data.get('github_url'),
                'documentation_url': innovation_data.get('documentation_url') or innovation_data.get('website_url'),
                'video_url': innovation_data.get('video_url'),
                'image_urls': innovation_data.get('image_urls', []),
                'creation_date': self.serialize_date(innovation_data.get('creation_date')),
                'last_updated_date': self.serialize_date(innovation_data.get('last_updated_date')),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            innovation_record = {k: v for k, v in innovation_record.items() if v is not None}
            
            result = self.client.table('innovations').insert(innovation_record).execute()
            
            if result.data:
                logger.info(f"✅ Created innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                return result.data[0]
            else:
                logger.error(f"❌ Failed to create innovation: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating innovation: {e}")
            return None
    
    # ORGANIZATIONS
    async def create_organization(self, org_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new organization record"""
        try:
            org_record = {
                'id': str(uuid4()),
                'name': org_data.get('name', ''),
                'organization_type': org_data.get('organization_type', 'unknown'),
                'country': org_data.get('country', ''),
                'website': org_data.get('website'),
                'description': org_data.get('description'),
                'founded_date': self.serialize_date(org_data.get('founded_date')),
                'contact_email': org_data.get('contact_email'),
                'logo_url': org_data.get('logo_url'),
                'verification_status': org_data.get('verification_status', 'pending'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            org_record = {k: v for k, v in org_record.items() if v is not None}
            
            result = self.client.table('organizations').insert(org_record).execute()
            
            if result.data:
                logger.info(f"✅ Created organization: {org_data.get('name', 'Unknown')}")
                return result.data[0]
            else:
                logger.error(f"❌ Failed to create organization: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating organization: {e}")
            return None
    
    # INDIVIDUALS
    async def create_individual(self, individual_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new individual record"""
        try:
            individual_record = {
                'id': str(uuid4()),
                'name': individual_data.get('name', ''),
                'email': individual_data.get('email'),
                'role': individual_data.get('role'),
                'bio': individual_data.get('bio'),
                'country': individual_data.get('country'),
                'organization_id': individual_data.get('organization_id'),
                'linkedin_url': individual_data.get('linkedin_url'),
                'twitter_url': individual_data.get('twitter_url') or individual_data.get('twitter_handle'),
                'website_url': individual_data.get('website_url') or individual_data.get('website'),
                'orcid_id': individual_data.get('orcid_id'),
                'profile_image_url': individual_data.get('profile_image_url'),
                'expertise_areas': individual_data.get('expertise_areas', []),
                'verification_status': individual_data.get('verification_status', 'pending'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            individual_record = {k: v for k, v in individual_record.items() if v is not None}
            
            result = self.client.table('individuals').insert(individual_record).execute()
            
            if result.data:
                logger.info(f"✅ Created individual: {individual_data.get('name', 'Unknown')}")
                return result.data[0]
            else:
                logger.error(f"❌ Failed to create individual: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating individual: {e}")
            return None
    
    # FUNDING
    async def create_funding(self, funding_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new funding record"""
        try:
            funding_record = {
                'id': str(uuid4()),
                'innovation_id': funding_data.get('innovation_id'),
                'funder_org_id': funding_data.get('funder_org_id'),
                'funding_type': funding_data.get('funding_type', 'grant'),
                'amount': funding_data.get('amount'),
                'currency': funding_data.get('currency', 'USD'),
                'funding_date': funding_data.get('funding_date'),
                'duration_months': funding_data.get('duration_months'),
                'description': funding_data.get('description') or funding_data.get('notes'),
                'funding_program': funding_data.get('funding_program') or funding_data.get('funding_round'),
                'verification_status': funding_data.get('verification_status', 'pending'),
                'verified': funding_data.get('verified', False),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            funding_record = {k: v for k, v in funding_record.items() if v is not None}
            
            result = self.client.table('fundings').insert(funding_record).execute()
            
            if result.data:
                logger.info(f"✅ Created funding record")
                return result.data[0]
            else:
                logger.error(f"❌ Failed to create funding: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating funding: {e}")
            return None
    
    # QUERY METHODS
    async def get_publications(self, limit: int = 100, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get publications with optional filters"""
        try:
            query = self.client.table('publications').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error fetching publications: {e}")
            return []
    
    async def get_innovations(self, limit: int = 100, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get innovations with optional filters"""
        try:
            query = self.client.table('innovations').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error fetching innovations: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}
            
            # Count publications
            pub_result = self.client.table('publications').select('id', count='exact').execute()
            stats['total_publications'] = pub_result.count if pub_result.count else 0
            
            # Count innovations
            innov_result = self.client.table('innovations').select('id', count='exact').execute()
            stats['total_innovations'] = innov_result.count if innov_result.count else 0
            
            # Count organizations
            org_result = self.client.table('organizations').select('id', count='exact').execute()
            stats['total_organizations'] = org_result.count if org_result.count else 0
            
            # Count individuals
            ind_result = self.client.table('individuals').select('id', count='exact').execute()
            stats['total_individuals'] = ind_result.count if ind_result.count else 0
            
            # Count fundings
            fund_result = self.client.table('fundings').select('id', count='exact').execute()
            stats['total_fundings'] = fund_result.count if fund_result.count else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error fetching statistics: {e}")
            return {}
    
    # SEARCH METHODS
    async def search_publications(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search publications by title, abstract, or keywords"""
        try:
            result = self.client.table('publications').select('*').or_(
                f'title.ilike.%{query}%,abstract.ilike.%{query}%'
            ).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error searching publications: {e}")
            return []
    
    async def search_innovations(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search innovations by title or description"""
        try:
            result = self.client.table('innovations').select('*').or_(
                f'title.ilike.%{query}%,description.ilike.%{query}%'
            ).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error searching innovations: {e}")
            return []
    
    # RELATIONSHIP METHODS
    async def link_publication_to_innovation(self, publication_id: str, innovation_id: str, relationship_type: str = "related") -> bool:
        """Link a publication to an innovation"""
        try:
            link_record = {
                'publication_id': publication_id,
                'innovation_id': innovation_id,
                'relationship_type': relationship_type
            }
            
            result = self.client.table('innovation_publications').insert(link_record).execute()
            
            if result.data:
                logger.info(f"✅ Linked publication {publication_id} to innovation {innovation_id}")
                return True
            else:
                logger.error(f"❌ Failed to link publication to innovation: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error linking publication to innovation: {e}")
            return False


# Global database service instance
db_service = DatabaseService()
