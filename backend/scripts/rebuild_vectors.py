#!/usr/bin/env python3
"""
Vector Database Rebuilder for TAIFA-FIALA
Recreates full-text embeddings for all innovations, publications, and news articles
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from config.settings import settings
from config.database import get_supabase
from services.vector_service import get_vector_service, VectorDocument
from services.database_service import DatabaseService


class VectorRebuilder:
    """Rebuilds vector database from scratch"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.vector_service = None
        self.db_service = DatabaseService()
        
        # Stats tracking
        self.stats = {
            "innovations_processed": 0,
            "innovations_vectorized": 0,
            "publications_processed": 0,
            "publications_vectorized": 0,
            "news_processed": 0,
            "news_vectorized": 0,
            "errors": [],
            "start_time": datetime.now(),
            "total_vectors_created": 0
        }
    
    async def initialize(self):
        """Initialize services"""
        logger.info("🚀 Initializing Vector Rebuilder...")
        
        try:
            # Initialize vector service
            self.vector_service = await get_vector_service()
            logger.info("✅ Vector service initialized")
            
            # Initialize database service
            await self.db_service.initialize()
            logger.info("✅ Database service initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            return False
    
    def prepare_innovation_text(self, innovation: Dict[str, Any]) -> str:
        """Prepare comprehensive text for innovation embedding"""
        parts = []
        
        # Core content
        if innovation.get('title'):
            parts.append(f"Title: {innovation['title']}")
        
        if innovation.get('description'):
            parts.append(f"Description: {innovation['description']}")
        
        # Metadata for better search
        if innovation.get('innovation_type'):
            parts.append(f"Type: {innovation['innovation_type']}")
        
        if innovation.get('country'):
            parts.append(f"Country: {innovation['country']}")
        
        # Organizations
        if innovation.get('organizations'):
            org_names = [org.get('name', '') for org in innovation['organizations'] if org.get('name')]
            if org_names:
                parts.append(f"Organizations: {', '.join(org_names)}")
        
        # Tags/Keywords
        if innovation.get('tags'):
            parts.append(f"Tags: {', '.join(innovation['tags'])}")
        
        # Publications titles for context
        if innovation.get('publications'):
            pub_titles = [pub.get('title', '') for pub in innovation['publications'] if pub.get('title')]
            if pub_titles:
                parts.append(f"Related Publications: {'; '.join(pub_titles[:3])}")  # Limit to first 3
        
        return " | ".join(parts)
    
    def prepare_publication_text(self, publication: Dict[str, Any]) -> str:
        """Prepare comprehensive text for publication embedding"""
        parts = []
        
        if publication.get('title'):
            parts.append(f"Title: {publication['title']}")
        
        if publication.get('abstract'):
            parts.append(f"Abstract: {publication['abstract']}")
        
        if publication.get('authors'):
            authors = publication['authors']
            if isinstance(authors, list):
                parts.append(f"Authors: {', '.join(authors[:5])}")  # Limit to first 5
            elif isinstance(authors, str):
                parts.append(f"Authors: {authors}")
        
        if publication.get('publication_type'):
            parts.append(f"Type: {publication['publication_type']}")
        
        if publication.get('keywords'):
            keywords = publication['keywords']
            if isinstance(keywords, list):
                parts.append(f"Keywords: {', '.join(keywords[:10])}")  # Limit to first 10
        
        if publication.get('african_entities'):
            entities = publication['african_entities']
            if isinstance(entities, list):
                parts.append(f"African Entities: {', '.join(entities[:5])}")
        
        return " | ".join(parts)
    
    async def rebuild_innovations(self) -> bool:
        """Rebuild vector embeddings for all innovations"""
        logger.info("🔄 Rebuilding innovation vectors...")
        
        try:
            # Fetch all innovations from Supabase
            response = self.supabase.table('innovations').select('*').execute()
            
            if not response.data:
                logger.warning("⚠️ No innovations found in database")
                return True
            
            innovations = response.data
            logger.info(f"📊 Found {len(innovations)} innovations to process")
            
            # Prepare vector documents
            vector_docs = []
            
            for innovation in innovations:
                try:
                    self.stats["innovations_processed"] += 1
                    
                    # Prepare text content
                    content = self.prepare_innovation_text(innovation)
                    
                    if not content.strip():
                        logger.warning(f"⚠️ Skipping innovation {innovation.get('id')} - no content")
                        continue
                    
                    # Create vector document
                    doc = VectorDocument(
                        id=f"innovation_{innovation['id']}",
                        content=content,
                        metadata={
                            "document_type": "innovation",
                            "innovation_id": innovation['id'],
                            "title": innovation.get('title', ''),
                            "innovation_type": innovation.get('innovation_type', ''),
                            "country": innovation.get('country', ''),
                            "verification_status": innovation.get('verification_status', ''),
                            "creation_date": innovation.get('creation_date', ''),
                            "timestamp": str(datetime.now().timestamp())
                        }
                    )
                    
                    vector_docs.append(doc)
                    self.stats["innovations_vectorized"] += 1
                    
                    if len(vector_docs) >= 50:  # Process in batches
                        success = await self.vector_service.upsert_documents(vector_docs)
                        if success:
                            logger.info(f"✅ Processed batch of {len(vector_docs)} innovations")
                            self.stats["total_vectors_created"] += len(vector_docs)
                        vector_docs = []
                    
                except Exception as e:
                    logger.error(f"❌ Error processing innovation {innovation.get('id')}: {e}")
                    self.stats["errors"].append(f"Innovation {innovation.get('id')}: {str(e)}")
            
            # Process remaining documents
            if vector_docs:
                success = await self.vector_service.upsert_documents(vector_docs)
                if success:
                    logger.info(f"✅ Processed final batch of {len(vector_docs)} innovations")
                    self.stats["total_vectors_created"] += len(vector_docs)
            
            logger.info(f"✅ Innovation vectorization complete: {self.stats['innovations_vectorized']}/{self.stats['innovations_processed']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rebuild innovation vectors: {e}")
            self.stats["errors"].append(f"Innovation rebuild: {str(e)}")
            return False
    
    async def rebuild_publications(self) -> bool:
        """Rebuild vector embeddings for all publications"""
        logger.info("🔄 Rebuilding publication vectors...")
        
        try:
            # Fetch all publications from Supabase
            response = self.supabase.table('publications').select('*').execute()
            
            if not response.data:
                logger.warning("⚠️ No publications found in database")
                return True
            
            publications = response.data
            logger.info(f"📊 Found {len(publications)} publications to process")
            
            # Prepare vector documents
            vector_docs = []
            
            for publication in publications:
                try:
                    self.stats["publications_processed"] += 1
                    
                    # Prepare text content
                    content = self.prepare_publication_text(publication)
                    
                    if not content.strip():
                        logger.warning(f"⚠️ Skipping publication {publication.get('id')} - no content")
                        continue
                    
                    # Create vector document
                    doc = VectorDocument(
                        id=f"publication_{publication['id']}",
                        content=content,
                        metadata={
                            "document_type": "publication",
                            "publication_id": publication['id'],
                            "title": publication.get('title', ''),
                            "publication_type": publication.get('publication_type', ''),
                            "authors": publication.get('authors', []),
                            "year": publication.get('publication_year'),
                            "african_relevance_score": publication.get('african_relevance_score', 0),
                            "ai_relevance_score": publication.get('ai_relevance_score', 0),
                            "timestamp": str(datetime.now().timestamp())
                        }
                    )
                    
                    vector_docs.append(doc)
                    self.stats["publications_vectorized"] += 1
                    
                    if len(vector_docs) >= 50:  # Process in batches
                        success = await self.vector_service.upsert_documents(vector_docs)
                        if success:
                            logger.info(f"✅ Processed batch of {len(vector_docs)} publications")
                            self.stats["total_vectors_created"] += len(vector_docs)
                        vector_docs = []
                    
                except Exception as e:
                    logger.error(f"❌ Error processing publication {publication.get('id')}: {e}")
                    self.stats["errors"].append(f"Publication {publication.get('id')}: {str(e)}")
            
            # Process remaining documents
            if vector_docs:
                success = await self.vector_service.upsert_documents(vector_docs)
                if success:
                    logger.info(f"✅ Processed final batch of {len(vector_docs)} publications")
                    self.stats["total_vectors_created"] += len(vector_docs)
            
            logger.info(f"✅ Publication vectorization complete: {self.stats['publications_vectorized']}/{self.stats['publications_processed']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rebuild publication vectors: {e}")
            self.stats["errors"].append(f"Publication rebuild: {str(e)}")
            return False
    
    async def get_vector_stats(self) -> Dict[str, Any]:
        """Get current vector database statistics"""
        try:
            if not self.vector_service:
                return {}
            
            stats = await self.vector_service.get_stats()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get vector stats: {e}")
            return {}
    
    def print_stats(self):
        """Print comprehensive statistics"""
        duration = datetime.now() - self.stats["start_time"]
        
        print("\n" + "="*60)
        print("🎯 VECTOR REBUILD COMPLETE")
        print("="*60)
        print(f"⏱️  Duration: {duration}")
        print(f"📊 Total Vectors Created: {self.stats['total_vectors_created']}")
        print()
        print("📈 INNOVATIONS:")
        print(f"   • Processed: {self.stats['innovations_processed']}")
        print(f"   • Vectorized: {self.stats['innovations_vectorized']}")
        print()
        print("📄 PUBLICATIONS:")
        print(f"   • Processed: {self.stats['publications_processed']}")
        print(f"   • Vectorized: {self.stats['publications_vectorized']}")
        print()
        if self.stats["errors"]:
            print(f"❌ ERRORS ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:5]:  # Show first 5
                print(f"   • {error}")
            if len(self.stats["errors"]) > 5:
                print(f"   • ... and {len(self.stats['errors']) - 5} more")
        else:
            print("✅ NO ERRORS")
        print("="*60)
    
    async def save_stats(self):
        """Save statistics to file"""
        stats_file = Path(__file__).parent / "vector_rebuild_stats.json"
        
        # Add vector database stats
        vector_stats = await self.get_vector_stats()
        self.stats["vector_db_stats"] = vector_stats
        self.stats["end_time"] = datetime.now()
        self.stats["duration_seconds"] = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        # Convert datetime objects to strings for JSON serialization
        stats_for_json = {
            **self.stats,
            "start_time": self.stats["start_time"].isoformat(),
            "end_time": self.stats["end_time"].isoformat()
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats_for_json, f, indent=2)
        
        logger.info(f"📊 Stats saved to {stats_file}")


async def main():
    """Main rebuild process"""
    rebuilder = VectorRebuilder()
    
    # Initialize
    if not await rebuilder.initialize():
        logger.error("❌ Failed to initialize - aborting")
        return
    
    logger.info("🎯 Starting vector database rebuild...")
    
    # Get initial stats
    initial_stats = await rebuilder.get_vector_stats()
    logger.info(f"📊 Initial vector count: {initial_stats.get('total_vectors', 0)}")
    
    # Rebuild vectors
    success = True
    
    # Rebuild innovations
    if not await rebuilder.rebuild_innovations():
        success = False
    
    # Rebuild publications
    if not await rebuilder.rebuild_publications():
        success = False
    
    # Get final stats
    final_stats = await rebuilder.get_vector_stats()
    logger.info(f"📊 Final vector count: {final_stats.get('total_vectors', 0)}")
    
    # Print and save statistics
    rebuilder.print_stats()
    await rebuilder.save_stats()
    
    if success:
        logger.info("🎉 Vector rebuild completed successfully!")
    else:
        logger.warning("⚠️ Vector rebuild completed with some errors")
    
    return success


if __name__ == "__main__":
    # Run the rebuild process
    result = asyncio.run(main())
    sys.exit(0 if result else 1)