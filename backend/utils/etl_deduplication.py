"""
ETL Deduplication Integration
Integrates the modern deduplication service with the ETL pipeline

This module provides wrapper functions that ETL modules can use to:
1. Check for duplicates before storing data
2. Handle duplicate actions (reject, merge, update, link)
3. Log deduplication results
4. Maintain data quality metrics
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from services.database_service import db_service
from services.deduplication_service import (
    DuplicateAction,
    DuplicateMatch,
    DuplicateType,
    dedup_service,
)


class ETLDeduplicationManager:
    """Manages deduplication for ETL processes"""
    
    def __init__(self):
        self.dedup_service = dedup_service
        self.db_service = db_service
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'duplicates_rejected': 0,
            'duplicates_merged': 0,
            'duplicates_updated': 0,
            'duplicates_linked': 0
        }
    
    async def process_publication_with_dedup(self, publication_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[List[DuplicateMatch]]]:
        """
        Process a publication with deduplication check
        
        Returns:
            (stored: bool, stored_record: Optional[Dict], duplicate_matches: Optional[List[DuplicateMatch]])
        """
        self.stats['total_checked'] += 1
        
        try:
            # Check for duplicates
            duplicate_matches = await self.dedup_service.check_publication_duplicates(publication_data)
            
            if not duplicate_matches:
                # No duplicates found, store the publication
                stored_record = await self.db_service.create_publication(publication_data)
                
                if stored_record:
                    logger.info(f"✅ Stored new publication: {publication_data.get('title', 'Unknown')[:50]}...")
                    return True, stored_record, None
                else:
                    logger.error(f"❌ Failed to store publication: {publication_data.get('title', 'Unknown')[:50]}...")
                    return False, None, None
                
            # Handle duplicates
            self.stats['duplicates_found'] += 1
            logger.info(f"📋 Duplicate publication detected: {', '.join([match.reason for match in duplicate_matches])}")
            
            # Use the highest confidence match
            best_match = max(duplicate_matches, key=lambda x: x.confidence)
            
            # Handle based on action
            if best_match.action == DuplicateAction.REJECT:
                self.stats['duplicates_rejected'] += 1
                logger.info(f"❌ Rejecting duplicate publication: {publication_data.get('title', 'Unknown')[:50]}...")
                return False, None, duplicate_matches
            
            elif best_match.action == DuplicateAction.UPDATE:
                self.stats['duplicates_updated'] += 1
                logger.info(f"🔄 Updating existing publication: {publication_data.get('title', 'Unknown')[:50]}...")
                # TODO: Implement update logic
                return False, best_match.existing_record, duplicate_matches
            
            elif best_match.action == DuplicateAction.MERGE:
                self.stats['duplicates_merged'] += 1
                logger.info(f"🔗 Merging with existing publication: {publication_data.get('title', 'Unknown')[:50]}...")
                # TODO: Implement merge logic
                return False, best_match.existing_record, duplicate_matches
            
            elif best_match.action == DuplicateAction.LINK:
                self.stats['duplicates_linked'] += 1
                logger.info(f"🔗 Linking to existing publication: {publication_data.get('title', 'Unknown')[:50]}...")
                # TODO: Implement link logic
                return False, best_match.existing_record, duplicate_matches
            
        except Exception as e:
            logger.error(f"❌ Error in publication deduplication: {e}")
            return False, None, None
    
    async def process_innovation_with_dedup(self, innovation_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[List[DuplicateMatch]]]:
        """
        Process an innovation with deduplication check
        
        Returns:
            (stored: bool, stored_record: Optional[Dict], duplicate_matches: Optional[List[DuplicateMatch]])
        """
        self.stats['total_checked'] += 1
        
        try:
            # DEBUG: Log the deduplication check
            logger.debug(f"🔍 Checking innovation for duplicates: {innovation_data.get('title', 'Unknown')[:50]}...")
            
            # Check for duplicates
            duplicate_matches = await self.dedup_service.check_innovation_duplicates(innovation_data)
            
            # DEBUG: Log duplicate check results
            logger.debug(f"🔍 Duplicate check result: {len(duplicate_matches) if duplicate_matches else 0} matches found")
            
            if not duplicate_matches:
                # No duplicates found, store the innovation
                logger.debug("✨ No duplicates found, proceeding to store innovation")
                stored_record = await self.db_service.create_innovation(innovation_data)
                
                if stored_record:
                    logger.info(f"✅ Stored new innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                    return True, stored_record, None
                else:
                    logger.error(f"❌ Failed to store innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                    return False, None, None
            
            # Handle duplicates
            self.stats['duplicates_found'] += 1
            logger.info(f"📋 Duplicate innovation detected: {', '.join([match.reason for match in duplicate_matches])}")
            
            # Use the highest confidence match
            best_match = max(duplicate_matches, key=lambda x: x.confidence)
            logger.debug(f"🎯 Best match selected with confidence: {best_match.confidence}")
            
            # Handle based on action
            if best_match.action == DuplicateAction.REJECT:
                self.stats['duplicates_rejected'] += 1
                logger.info(f"❌ Rejecting duplicate innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                return False, None, duplicate_matches
            
            elif best_match.action == DuplicateAction.UPDATE:
                self.stats['duplicates_updated'] += 1
                logger.info(f"🔄 Updating existing innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                # TODO: Implement update logic
                return False, best_match.existing_record, duplicate_matches
            
            elif best_match.action == DuplicateAction.MERGE:
                self.stats['duplicates_merged'] += 1
                logger.info(f"🔗 Merging with existing innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                # TODO: Implement merge logic
                return False, best_match.existing_record, duplicate_matches
            
            elif best_match.action == DuplicateAction.LINK:
                self.stats['duplicates_linked'] += 1
                logger.info(f"🔗 Linking to existing innovation: {innovation_data.get('title', 'Unknown')[:50]}...")
                # TODO: Implement link logic
                return False, best_match.existing_record, duplicate_matches
                
        except Exception as e:
            logger.error(f"❌ Error in innovation deduplication: {e}")
            return False, None, None
    
    async def process_organization_with_dedup(self, org_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[DuplicateMatch]]:
        """
        Process an organization with deduplication check
        
        Returns:
            (stored: bool, stored_record: Optional[Dict], duplicate_match: Optional[DuplicateMatch])
        """
        self.stats['total_checked'] += 1
        
        try:
            # Check for duplicates
            duplicate_match = await self.dedup_service.check_organization_duplicate(org_data)
            
            if duplicate_match.is_duplicate:
                self.stats['duplicates_found'] += 1
                logger.info(f"📋 Duplicate organization detected: {duplicate_match.reason}")
                
                # Handle based on action
                if duplicate_match.action == DuplicateAction.REJECT:
                    self.stats['duplicates_rejected'] += 1
                    logger.info(f"❌ Rejecting duplicate organization: {org_data.get('name', 'Unknown')}")
                    return False, None, duplicate_match
                
                elif duplicate_match.action == DuplicateAction.MERGE:
                    self.stats['duplicates_merged'] += 1
                    logger.info(f"🔗 Merging with existing organization: {org_data.get('name', 'Unknown')}")
                    # TODO: Implement merge logic
                    return False, duplicate_match.existing_record, duplicate_match
                
                elif duplicate_match.action == DuplicateAction.LINK:
                    self.stats['duplicates_linked'] += 1
                    logger.info(f"🔗 Linking to existing organization: {org_data.get('name', 'Unknown')}")
                    # TODO: Implement link logic
                    return False, duplicate_match.existing_record, duplicate_match
            
            # No duplicate found, store the organization
            stored_record = await self.db_service.create_organization(org_data)
            
            if stored_record:
                logger.info(f"✅ Stored new organization: {org_data.get('name', 'Unknown')}")
                return True, stored_record, None
            else:
                logger.error(f"❌ Failed to store organization: {org_data.get('name', 'Unknown')}")
                return False, None, None
                
        except Exception as e:
            logger.error(f"❌ Error in organization deduplication: {e}")
            return False, None, None
    
    async def bulk_process_publications_with_dedup(self, publications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk process publications with deduplication
        
        Returns summary of processing results
        """
        results = {
            'total_processed': len(publications),
            'stored': [],
            'duplicates': [],
            'errors': []
        }
        
        logger.info(f"📚 Processing {len(publications)} publications with deduplication...")
        
        for pub_data in publications:
            try:
                stored, record, duplicate_matches = await self.process_publication_with_dedup(pub_data)
                
                if stored and record:
                    results['stored'].append(record)
                elif duplicate_matches:
                    results['duplicates'].append({
                        'original_data': pub_data,
                        'duplicate_matches': duplicate_matches
                    })
                else:
                    results['errors'].append(pub_data)
                    
            except Exception as e:
                logger.error(f"❌ Error processing publication: {e}")
                results['errors'].append(pub_data)
        
        logger.info(f"📊 Bulk processing complete: {len(results['stored'])} stored, {len(results['duplicates'])} duplicates, {len(results['errors'])} errors")
        return results
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        duplicate_rate = (self.stats['duplicates_found'] / self.stats['total_checked']) * 100 if self.stats['total_checked'] > 0 else 0
        
        return {
            **self.stats,
            'duplicate_rate_percent': round(duplicate_rate, 2)
        }
    
    def reset_stats(self):
        """Reset deduplication statistics"""
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'duplicates_rejected': 0,
            'duplicates_merged': 0,
            'duplicates_updated': 0,
            'duplicates_linked': 0
        }


# Global ETL deduplication manager instance
etl_dedup_manager = ETLDeduplicationManager()


# Convenience functions for ETL modules
async def store_publication_with_dedup(publication_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Convenience function to store publication with deduplication"""
    stored, record, _ = await etl_dedup_manager.process_publication_with_dedup(publication_data)
    return stored, record


async def store_innovation_with_dedup(innovation_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Convenience function to store innovation with deduplication"""
    stored, record, _ = await etl_dedup_manager.process_innovation_with_dedup(innovation_data)
    return stored, record


async def store_organization_with_dedup(org_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Convenience function to store organization with deduplication"""
    stored, record, _ = await etl_dedup_manager.process_organization_with_dedup(org_data)
    return stored, record


async def bulk_store_publications_with_dedup(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to bulk store publications with deduplication"""
    results = await etl_dedup_manager.bulk_process_publications_with_dedup(publications)
    return results['stored']

async def check_and_handle_publication_duplicates(publication_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Legacy function name for backward compatibility
    Check for duplicates and handle them according to deduplication rules
    
    Returns:
        (should_store: bool, existing_record: Optional[Dict])
    """
    stored, record, duplicate_matches = await etl_dedup_manager.process_publication_with_dedup(publication_data)
    
    if stored:
        return True, record
    elif duplicate_matches:
        # Return the best match if duplicates were found
        best_match = max(duplicate_matches, key=lambda x: x.confidence)
        return False, best_match.existing_record
    else:
        return False, None


async def check_and_handle_innovation_duplicates(innovation_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Legacy function name for backward compatibility
    Check for duplicates and handle them according to deduplication rules
    
    Returns:
        (should_store: bool, existing_record: Optional[Dict])
    """
    stored, record, duplicate_matches = await etl_dedup_manager.process_innovation_with_dedup(innovation_data)
    
    if stored:
        return True, record
    elif duplicate_matches:
        # Return the best match if duplicates were found
        best_match = max(duplicate_matches, key=lambda x: x.confidence)
        return False, best_match.existing_record
    else:
        return False, None
