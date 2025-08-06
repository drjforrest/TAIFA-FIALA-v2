#!/usr/bin/env python3
"""
Extract Organizations from Existing Data
This script extracts organization information from publications and innovations
and populates the organizations table to fix the dashboard count.
"""

import asyncio
import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Set
from uuid import uuid4
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from loguru import logger
from config.database import get_supabase


# Load environment variables
load_dotenv()

class OrganizationExtractor:
    def __init__(self):
        self.supabase = get_supabase()
        self.extracted_orgs = set()
        
    async def extract_organizations_from_publications(self):
        """Extract organizations from publications data"""
        try:
            # Get all publications with available data
            response = self.supabase.table('publications').select(
                'id, title, authors, abstract'
            ).execute()
            
            if not response.data:
                logger.info("No publications found")
                return []
            
            publications = response.data
            logger.info(f"Processing {len(publications)} publications for organization extraction")
            
            organizations = []
            
            for pub in publications:
                pub_orgs = self._extract_orgs_from_publication(pub)
                organizations.extend(pub_orgs)
            
            logger.info(f"Extracted {len(organizations)} organization references from publications")
            return organizations
            
        except Exception as e:
            logger.error(f"Error extracting organizations from publications: {e}")
            return []
    
    def _extract_orgs_from_publication(self, publication: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract organizations from a single publication"""
        organizations = []
        
        try:
            # Combine text sources (only available columns)
            authors = publication.get('authors', []) or []
            authors_text = ' '.join([str(author) for author in authors if author is not None])
            
            text_sources = [
                publication.get('title', '') or '',
                publication.get('abstract', '') or '',
                authors_text
            ]
            
            full_text = ' '.join(text_sources)
            
            if not full_text.strip():
                return organizations
            
            # Extract organizations using patterns
            org_names = self._extract_organization_names(full_text)
            
            for org_name in org_names:
                if org_name not in self.extracted_orgs:
                    self.extracted_orgs.add(org_name)
                    
                    # Determine organization type and country
                    org_type = self._classify_organization_type(org_name, full_text)
                    country = self._extract_country_for_org(org_name, full_text)
                    
                    organizations.append({
                        'id': str(uuid4()),
                        'name': org_name,
                        'organization_type': org_type,
                        'country': country,
                        'description': f"Extracted from publication: {publication.get('title', '')[:100]}...",
                        'verification_status': 'community'
                    })
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error extracting organizations from publication {publication.get('id')}: {e}")
            return []
    
    def _extract_organization_names(self, text: str) -> Set[str]:
        """Extract organization names using regex patterns"""
        org_names = set()
        
        # University patterns
        university_patterns = [
            r'University of ([A-Za-z\s]+)',
            r'([A-Za-z\s]+) University',
            r'([A-Za-z\s]+) Institute of Technology',
            r'([A-Za-z\s]+) Institute',
            r'([A-Za-z\s]+) College',
            r'([A-Za-z\s]+) School of ([A-Za-z\s]+)',
        ]
        
        for pattern in university_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    org_name = match.group(0).strip()
                    if len(org_name) > 5 and len(org_name) < 80:  # Filter reasonable lengths
                        org_names.add(org_name)
        
        # Research institution patterns
        research_patterns = [
            r'([A-Za-z\s]+) Research (?:Institute|Center|Centre)',
            r'(?:National|International) ([A-Za-z\s]+) (?:Institute|Center|Centre)',
            r'Council for Scientific and Industrial Research',
            r'CSIR',
            r'([A-Za-z\s]+) Laboratory',
            r'([A-Za-z\s]+) Foundation',
        ]
        
        for pattern in research_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                org_name = match.group(0).strip()
                if len(org_name) > 5 and len(org_name) < 80:
                    org_names.add(org_name)
        
        # Company patterns (be more selective)
        company_patterns = [
            r'([A-Za-z\s]+) (?:Ltd|Limited|Inc|Corporation|Corp|Company)',
            r'([A-Za-z\s]+) Technologies?',
            r'([A-Za-z\s]+) Systems?',
            r'([A-Za-z\s]+) Solutions?',
        ]
        
        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                org_name = match.group(0).strip()
                if len(org_name) > 8 and len(org_name) < 60:  # More selective for companies
                    org_names.add(org_name)
        
        return org_names
    
    def _classify_organization_type(self, org_name: str, context: str) -> str:
        """Classify organization type based on name and context"""
        org_lower = org_name.lower()
        context_lower = context.lower()
        
        # University/Academic
        if any(word in org_lower for word in ['university', 'college', 'institute of technology', 'school of']):
            return 'university'
        
        # Research Institution
        if any(word in org_lower for word in ['research', 'laboratory', 'institute', 'center', 'centre', 'csir']):
            return 'research_institute'
        
        # Company/Private
        if any(word in org_lower for word in ['ltd', 'limited', 'inc', 'corporation', 'corp', 'company', 'technologies', 'systems', 'solutions']):
            return 'company'
        
        # Foundation/NGO
        if any(word in org_lower for word in ['foundation', 'trust', 'society', 'association']):
            return 'foundation'
        
        # Government
        if any(word in org_lower for word in ['national', 'ministry', 'department', 'council', 'government']):
            return 'government'
        
        # Default
        return 'other'
    
    def _extract_country_for_org(self, org_name: str, context: str) -> str:
        """Extract country for organization based on context"""
        # African countries mapping
        african_countries = [
            'Nigeria', 'Kenya', 'South Africa', 'Ghana', 'Egypt', 'Morocco', 'Tunisia',
            'Uganda', 'Tanzania', 'Ethiopia', 'Rwanda', 'Senegal', 'Ivory Coast',
            'Botswana', 'Zambia', 'Zimbabwe', 'Cameroon', 'Algeria', 'Libya',
            'Sudan', 'Mali', 'Burkina Faso', 'Niger', 'Chad', 'Madagascar'
        ]
        
        context_lower = (org_name + ' ' + context).lower()
        
        # Look for country mentions near the organization
        for country in african_countries:
            if country.lower() in context_lower:
                return country
        
        # Default based on common patterns
        if 'cape town' in context_lower or 'johannesburg' in context_lower or 'pretoria' in context_lower:
            return 'South Africa'
        elif 'lagos' in context_lower or 'abuja' in context_lower or 'ibadan' in context_lower:
            return 'Nigeria'
        elif 'nairobi' in context_lower or 'mombasa' in context_lower:
            return 'Kenya'
        elif 'accra' in context_lower or 'kumasi' in context_lower:
            return 'Ghana'
        elif 'cairo' in context_lower or 'alexandria' in context_lower:
            return 'Egypt'
        
        return 'Unknown'
    
    def _extract_website_for_org(self, org_name: str, source_url: str) -> str:
        """Extract or infer website for organization"""
        if source_url and 'http' in source_url:
            # Extract domain from source URL as potential org website
            import urllib.parse
            try:
                parsed = urllib.parse.urlparse(source_url)
                return f"{parsed.scheme}://{parsed.netloc}"
            except:
                pass
        
        return None
    
    async def store_organizations(self, organizations: List[Dict[str, Any]]):
        """Store extracted organizations in the database"""
        try:
            if not organizations:
                logger.info("No organizations to store")
                return
            
            # Remove duplicates by name
            unique_orgs = {}
            for org in organizations:
                name = org['name']
                if name not in unique_orgs:
                    unique_orgs[name] = org
                else:
                    # Merge information if duplicate
                    existing = unique_orgs[name]
                    if org['country'] != 'Unknown' and existing['country'] == 'Unknown':
                        existing['country'] = org['country']
            
            final_orgs = list(unique_orgs.values())
            logger.info(f"Storing {len(final_orgs)} unique organizations")
            
            # Insert in batches
            batch_size = 50
            for i in range(0, len(final_orgs), batch_size):
                batch = final_orgs[i:i + batch_size]
                
                response = self.supabase.table('organizations').insert(batch).execute()
                
                if response.data:
                    logger.info(f"Successfully inserted batch of {len(batch)} organizations")
                else:
                    logger.error(f"Failed to insert batch: {response}")
            
            logger.info(f"✅ Successfully stored {len(final_orgs)} organizations")
            
        except Exception as e:
            logger.error(f"Error storing organizations: {e}")
    
    async def run_extraction(self):
        """Run the full organization extraction process"""
        try:
            logger.info("🏢 Starting organization extraction from existing data...")
            
            # Extract from publications
            pub_organizations = await self.extract_organizations_from_publications()
            
            all_organizations = pub_organizations
            logger.info(f"Total organizations extracted: {len(all_organizations)}")
            
            if all_organizations:
                await self.store_organizations(all_organizations)
                
                # Verify count
                count_response = self.supabase.table('organizations').select('id', count='exact').execute()
                final_count = count_response.count or 0
                
                logger.info(f"🎉 Organization extraction completed! Final count: {final_count}")
                return final_count
            else:
                logger.info("No organizations were extracted")
                return 0
                
        except Exception as e:
            logger.error(f"Error in organization extraction: {e}")
            return 0


async def main():
    """Main execution function"""
    extractor = OrganizationExtractor()
    count = await extractor.run_extraction()
    
    if count > 0:
        print(f"\n✅ SUCCESS: Extracted and stored {count} organizations!")
        print("The dashboard should now show the correct organization count.")
    else:
        print("\n❌ No organizations were extracted. Check the logs for details.")


if __name__ == "__main__":
    asyncio.run(main())