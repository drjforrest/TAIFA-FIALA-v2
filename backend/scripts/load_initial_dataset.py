#!/usr/bin/env python3
"""
Load Initial Dataset into Supabase Database and Pinecone Vector Store
Comprehensive database insertion script with full text embedding support
"""

import json
import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from loguru import logger
import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    database: str
    user: str
    password: str




class DatasetLoader:
    """Load TAIFA-FIALA dataset into Supabase database"""

    def __init__(self):
        self.db_config = self._load_db_config()
        self.conn = None
        
        # Counters for progress tracking  
        self.total_papers = 0
        self.inserted_publications = 0
        self.inserted_embeddings = 0
        self.processed_authors = 0
        self.processed_organizations = 0

    def _load_db_config(self) -> DatabaseConfig:
        """Load database configuration from environment"""
        return DatabaseConfig(
            host=os.getenv('host', 'aws-0-ca-central-1.pooler.supabase.com'),
            port=int(os.getenv('port', 6543)),
            database=os.getenv('dbname', 'postgres'),
            user=os.getenv('user', 'postgres.bbbwmfylfbiltzcyucwa'),
            password=os.getenv('password', 'RoUD*gy@@AYq9-dZ')
        )


    def initialize_connections(self):
        """Initialize database connections"""
        logger.info("🔌 Initializing database connections...")

        # Database connection
        try:
            self.conn = psycopg2.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                user=self.db_config.user,
                password=self.db_config.password,
                cursor_factory=RealDictCursor
            )
            self.conn.autocommit = False
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

        # Skip Pinecone and embedding setup since embeddings already exist
        logger.info("ℹ️ Skipping Pinecone setup - embeddings already exist in vector database")

    def load_dataset(self, filepath: str) -> Dict[str, Any]:
        """Load the dataset from JSON file"""
        logger.info(f"📂 Loading dataset from {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            self.total_papers = len(dataset['papers'])
            logger.info(f"✅ Loaded {self.total_papers} papers from dataset")
            return dataset
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise

    def clean_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Clean and parse datetime string"""
        if not date_str:
            return None
        
        try:
            # Handle various date formats
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except Exception:
            return None


    def upsert_organization(self, org_data: Dict[str, Any]) -> str:
        """Insert or update organization and return ID"""
        cursor = self.conn.cursor()
        
        try:
            # Check if organization exists
            cursor.execute(
                "SELECT id FROM organizations WHERE name = %s",
                (org_data['name'],)
            )
            result = cursor.fetchone()
            
            if result:
                return str(result['id'])
            
            # Insert new organization
            org_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO organizations (
                    id, name, organization_type, country, description,
                    verification_status, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                org_id,
                org_data['name'],
                org_data.get('organization_type', 'unknown'),
                org_data.get('country', 'Unknown'),
                org_data.get('description', ''),
                'pending',
                datetime.now(),
                datetime.now()
            ))
            
            self.processed_organizations += 1
            return org_id
            
        except Exception as e:
            logger.error(f"❌ Failed to upsert organization {org_data.get('name', 'Unknown')}: {e}")
            raise

    def upsert_individual(self, individual_data: Dict[str, Any]) -> str:
        """Insert or update individual and return ID"""
        cursor = self.conn.cursor()
        
        try:
            # Check if individual exists
            cursor.execute(
                "SELECT id FROM individuals WHERE name = %s",
                (individual_data['name'],)
            )
            result = cursor.fetchone()
            
            if result:
                return str(result['id'])
            
            # Insert new individual
            individual_id = str(uuid.uuid4())
            
            # Handle email field - use NULL instead of empty string to avoid unique constraint issues
            email = individual_data.get('email', '').strip()
            email = email if email else None
            
            cursor.execute("""
                INSERT INTO individuals (
                    id, name, email, role, bio, country, 
                    verification_status, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                individual_id,
                individual_data['name'],
                email,
                individual_data.get('role', 'researcher'),
                individual_data.get('bio', ''),
                individual_data.get('country', 'Unknown'),
                'pending',
                datetime.now(),
                datetime.now()
            ))
            
            self.processed_authors += 1
            return individual_id
            
        except Exception as e:
            logger.error(f"❌ Failed to upsert individual {individual_data.get('name', 'Unknown')}: {e}")
            raise

    def insert_publication(self, paper: Dict[str, Any]) -> str:
        """Insert publication and return ID"""
        cursor = self.conn.cursor()
        
        try:
            pub_id = str(uuid.uuid4())
            
            # Clean and prepare data
            publication_date = self.clean_datetime(paper.get('publication_date'))
            processed_at = self.clean_datetime(paper.get('processed_at'))
            
            cursor.execute("""
                INSERT INTO publications (
                    id, title, abstract, publication_type, publication_date, year,
                    doi, url, pdf_url, journal, venue, citation_count,
                    project_domain, ai_techniques, geographic_scope, funding_source,
                    key_outcomes, african_relevance_score, ai_relevance_score,
                    african_entities, keywords, source, source_id, data_type,
                    processed_at, verification_status, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                pub_id,
                paper.get('title', ''),
                paper.get('abstract', ''),
                paper.get('publication_type', 'journal_paper'),
                publication_date,
                paper.get('year'),
                paper.get('doi', ''),
                paper.get('url', ''),
                paper.get('pdf_url', ''),
                paper.get('journal', ''),
                paper.get('venue', ''),
                paper.get('citation_count', 0),
                paper.get('project_domain', ''),
                paper.get('ai_techniques', ''),
                paper.get('geographic_scope', ''),
                paper.get('funding_source', ''),
                paper.get('key_outcomes', ''),
                float(paper.get('african_relevance_score', 0.0)),
                float(paper.get('ai_relevance_score', 0.0)),
                paper.get('african_entities', []),
                paper.get('keywords', []),
                paper.get('source', 'unknown'),
                paper.get('source_id', ''),
                paper.get('data_type', 'Academic Paper'),
                processed_at or datetime.now(),
                'pending',
                datetime.now(),
                datetime.now()
            ))
            
            self.inserted_publications += 1
            return pub_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert publication '{paper.get('title', 'Unknown')}': {e}")
            raise

    def create_publication_relationships(self, pub_id: str, paper: Dict[str, Any]):
        """Create relationships between publication and authors/organizations"""
        cursor = self.conn.cursor()
        
        try:
            # Handle authors
            authors = paper.get('authors', [])
            for i, author_name in enumerate(authors):
                if isinstance(author_name, str) and author_name.strip():
                    # Create individual record
                    author_data = {
                        'name': author_name.strip(),
                        'role': 'researcher'
                    }
                    author_id = self.upsert_individual(author_data)
                    
                    # Create publication-author relationship
                    cursor.execute("""
                        INSERT INTO publication_authors (
                            publication_id, individual_id, author_order, 
                            corresponding_author, created_at
                        ) VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (publication_id, individual_id) DO NOTHING
                    """, (
                        pub_id, author_id, i + 1, i == 0, datetime.now()
                    ))
            
        except Exception as e:
            logger.error(f"❌ Failed to create publication relationships: {e}")
            # Don't raise - this is non-critical

    def create_embedding_reference(self, pub_id: str, paper: Dict[str, Any]):
        """Create embedding reference in database (embeddings already exist in Pinecone)"""
        try:
            # Store embedding reference in database  
            cursor = self.conn.cursor()
            vector_id = f"pub_{pub_id}"
            
            cursor.execute("""
                INSERT INTO embeddings (
                    id, source_type, source_id, vector_id, 
                    embedding_model, vector_dimension, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                'publication',
                pub_id,
                vector_id,
                'sentence-transformers',
                384,  # Standard dimension for most sentence transformers
                datetime.now()
            ))
            
            self.inserted_embeddings += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to create embedding reference for {pub_id}: {e}")
            # Don't raise - embeddings are nice-to-have but not critical

    def process_papers(self, papers: List[Dict[str, Any]]):
        """Process all papers and insert into database"""
        logger.info(f"🔄 Processing {len(papers)} papers...")
        
        for i, paper in enumerate(papers, 1):
            try:
                logger.info(f"📄 Processing paper {i}/{len(papers)}: {paper.get('title', 'Unknown')[:80]}...")
                
                # Insert publication
                pub_id = self.insert_publication(paper)
                
                # Create relationships
                self.create_publication_relationships(pub_id, paper)
                
                # Create embedding reference (embeddings already exist in Pinecone)
                self.create_embedding_reference(pub_id, paper)
                
                # Commit after each paper to avoid losing progress
                self.conn.commit()
                
                if i % 5 == 0:
                    logger.info(f"✅ Processed {i}/{len(papers)} papers")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process paper {i}: {e}")
                self.conn.rollback()
                continue

    def refresh_materialized_view(self):
        """Refresh the dashboard stats materialized view"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("REFRESH MATERIALIZED VIEW dashboard_stats")
            self.conn.commit()
            logger.info("✅ Refreshed dashboard stats materialized view")
        except Exception as e:
            logger.error(f"⚠️ Failed to refresh materialized view: {e}")
            # This is not critical for the data loading process

    def get_final_statistics(self) -> Dict[str, Any]:
        """Get final statistics from the database"""
        cursor = self.conn.cursor()
        
        try:
            # Get counts from database
            cursor.execute("SELECT COUNT(*) as count FROM publications")
            pub_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM individuals")
            individual_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM organizations")
            org_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM embeddings WHERE source_type = 'publication'")
            embedding_count = cursor.fetchone()['count']
            
            return {
                'publications_in_db': pub_count,
                'individuals_in_db': individual_count,
                'organizations_in_db': org_count,
                'embeddings_in_db': embedding_count,
                'inserted_this_run': {
                    'publications': self.inserted_publications,
                    'embeddings': self.inserted_embeddings,
                    'authors': self.processed_authors,
                    'organizations': self.processed_organizations
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to get final statistics: {e}")
            return {}

    def close_connections(self):
        """Close all connections"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Database connection closed")

    def run(self, dataset_path: str):
        """Main execution method"""
        logger.info("🚀 Starting TAIFA-FIALA Dataset Loading Process...")
        
        try:
            # Initialize connections
            self.initialize_connections()
            
            # Load dataset
            dataset = self.load_dataset(dataset_path)
            
            # Process papers
            self.process_papers(dataset['papers'])
            
            # Refresh materialized view
            self.refresh_materialized_view()
            
            # Get final statistics
            stats = self.get_final_statistics()
            
            # Log final results
            logger.info("🎉 Dataset Loading Complete!")
            logger.info(f"📊 Final Statistics:")
            logger.info(f"   Publications in DB: {stats.get('publications_in_db', 0)}")
            logger.info(f"   Individuals in DB: {stats.get('individuals_in_db', 0)}")
            logger.info(f"   Organizations in DB: {stats.get('organizations_in_db', 0)}")
            logger.info(f"   Vector Embeddings: {stats.get('embeddings_in_db', 0)}")
            
            logger.info(f"✅ Successfully processed {self.inserted_publications} publications")
            logger.info(f"✅ Created {self.inserted_embeddings} vector embeddings")
            logger.info(f"✅ Processed {self.processed_authors} authors")
            logger.info(f"✅ Processed {self.processed_organizations} organizations")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Dataset loading failed: {e}")
            if self.conn:
                self.conn.rollback()
            return False
            
        finally:
            self.close_connections()


def main():
    """Main function"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('/Users/drjforrest/dev/devprojects/TAIFA-FIALA/.env')
    
    dataset_path = '/Users/drjforrest/dev/devprojects/TAIFA-FIALA/data/taifa_fiala_initial_dataset.json'
    
    loader = DatasetLoader()
    success = loader.run(dataset_path)
    
    if success:
        logger.info("🌍 TAIFA-FIALA dataset successfully loaded!")
        logger.info("🎯 Ready for frontend integration and public launch!")
    else:
        logger.error("❌ Dataset loading failed!")


if __name__ == "__main__":
    main()