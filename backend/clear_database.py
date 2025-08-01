#!/usr/bin/env python3
"""
Clear all data from TAIFA-FIALA database tables
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger


def clear_database():
    """Clear all data from database tables"""
    
    # Database configuration
    conn = psycopg2.connect(
        host=os.getenv('host', 'aws-0-ca-central-1.pooler.supabase.com'),
        port=int(os.getenv('port', 6543)),
        database=os.getenv('dbname', 'postgres'),
        user=os.getenv('user', 'postgres.bbbwmfylfbiltzcyucwa'),
        password=os.getenv('password', 'RoUD*gy@@AYq9-dZ'),
        cursor_factory=RealDictCursor
    )
    
    try:
        cursor = conn.cursor()
        
        # List of tables to clear (in order to respect foreign key constraints)
        tables_to_clear = [
            'publication_authors',
            'publication_organizations', 
            'innovation_publications',
            'innovation_individuals',
            'innovation_organizations',
            'embeddings',
            'comments',
            'ratings',
            'articles',
            'fundings',
            'publications',
            'innovations',
            'individuals',
            'organizations',
            'ingestion_logs',
            'user_sessions',
            'legacy_funding_announcements'
        ]
        
        logger.info("🧹 Clearing database tables...")
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                deleted_count = cursor.rowcount
                logger.info(f"   ✅ Cleared {deleted_count} records from {table}")
            except Exception as e:
                logger.warning(f"   ⚠️ Could not clear {table}: {e}")
        
        # Refresh materialized view
        try:
            cursor.execute("REFRESH MATERIALIZED VIEW dashboard_stats")
            logger.info("   ✅ Refreshed dashboard stats materialized view")
        except Exception as e:
            logger.warning(f"   ⚠️ Could not refresh materialized view: {e}")
        
        conn.commit()
        logger.info("🎉 Database cleared successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to clear database: {e}")
        conn.rollback()
        
    finally:
        conn.close()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv('/Users/drjforrest/dev/devprojects/TAIFA-FIALA/.env')
    
    clear_database()