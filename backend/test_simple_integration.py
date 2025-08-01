#!/usr/bin/env python3
"""
TAIFA-FIALA Simple Integration Test
===================================

Basic test to check:
1. What columns actually exist in Supabase
2. What type of Pinecone index we're working with
3. Basic connectivity

Usage:
    python test_simple_integration.py
"""

import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from config.database import get_supabase
from pinecone import Pinecone

class SimpleIntegrationTester:
    """Simple integration tester to understand current setup"""

    def __init__(self):
        self.supabase = None
        self.pinecone_client = None
        self.pinecone_index = None

    def log(self, message: str):
        """Log message with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    async def check_supabase_schema(self):
        """Check what columns actually exist in the innovations table"""
        self.log("🔍 Checking Supabase database schema...")

        try:
            # Initialize Supabase client
            self.supabase = get_supabase()
            self.log("✅ Supabase client initialized")

            # Try to get table info by querying with limit 0
            response = self.supabase.table('innovations').select('*').limit(1).execute()

            if response.data:
                # If we have data, show the columns
                sample_record = response.data[0]
                columns = list(sample_record.keys())
                self.log(f"📋 Found {len(columns)} columns in innovations table:")
                for col in sorted(columns):
                    self.log(f"    - {col}")
            else:
                self.log("📭 No data in innovations table, but connection works")

            # Try a simple insert with minimal data to see what's required
            test_innovation = {
                "id": str(uuid4()),
                "title": "Test Innovation - Simple Integration",
                "description": "Testing database schema",
                "innovation_type": "TestTech",
                "domain": "TestDomain",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            try:
                insert_response = self.supabase.table('innovations').insert(test_innovation).execute()
                if insert_response.data:
                    self.log("✅ Basic insert successful")
                    # Clean up immediately
                    self.supabase.table('innovations').delete().eq('id', test_innovation['id']).execute()
                    self.log("🧹 Test record cleaned up")
                else:
                    self.log("⚠️  Insert response empty")
            except Exception as insert_error:
                self.log(f"❌ Insert failed: {insert_error}")
                # This tells us what columns are missing or wrong

            return True

        except Exception as e:
            self.log(f"❌ Supabase check failed: {e}")
            return False

    async def check_pinecone_setup(self):
        """Check Pinecone index configuration"""
        self.log("🎯 Checking Pinecone setup...")

        try:
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.log("✅ Pinecone client initialized")

            # List available indexes
            indexes = self.pinecone_client.list_indexes()
            self.log(f"📋 Found {len(indexes)} Pinecone indexes:")
            for idx in indexes:
                self.log(f"    - {idx.name}")

            # Check our specific index
            if settings.PINECONE_INDEX_NAME in [idx.name for idx in indexes]:
                self.log(f"✅ Found target index: {settings.PINECONE_INDEX_NAME}")

                # Get index details
                index_info = self.pinecone_client.describe_index(settings.PINECONE_INDEX_NAME)
                self.log(f"📊 Index details:")
                self.log(f"    - Status: {index_info.status}")
                self.log(f"    - Dimension: {index_info.dimension}")
                self.log(f"    - Metric: {index_info.metric}")
                self.log(f"    - Spec: {index_info.spec}")

                # Connect to the index
                self.pinecone_index = self.pinecone_client.Index(settings.PINECONE_INDEX_NAME)

                # Get index stats
                stats = self.pinecone_index.describe_index_stats()
                self.log(f"📈 Index stats:")
                self.log(f"    - Total vectors: {stats.total_vector_count}")
                self.log(f"    - Index fullness: {stats.index_fullness}")

                # Check if this is an inference-enabled index
                try:
                    # Try a simple text-based query to see if inference is enabled
                    test_query_response = self.pinecone_index.query(
                        data="test query",  # Text-based query
                        top_k=1,
                        include_metadata=True
                    )
                    self.log("✅ Index supports text-based queries (inference enabled)")
                    self.log(f"    - Query returned {len(test_query_response.matches)} matches")
                except Exception as query_error:
                    self.log(f"⚠️  Text-based query failed: {query_error}")
                    self.log("    - Index may require vector inputs instead of text")

            else:
                self.log(f"❌ Target index '{settings.PINECONE_INDEX_NAME}' not found")
                return False

            return True

        except Exception as e:
            self.log(f"❌ Pinecone check failed: {e}")
            return False

    async def test_basic_operations(self):
        """Test basic operations between services"""
        self.log("🔄 Testing basic operations...")

        if not self.supabase or not self.pinecone_index:
            self.log("❌ Services not initialized, skipping operations test")
            return False

        try:
            # Test 1: Simple Supabase operation
            test_id = str(uuid4())
            basic_innovation = {
                "id": test_id,
                "title": "Integration Test Innovation",
                "description": "Testing basic database operations",
                "innovation_type": "TestTech",
                "domain": "TestDomain"
            }

            # Add only the fields we know exist
            supabase_response = self.supabase.table('innovations').insert(basic_innovation).execute()

            if supabase_response.data:
                self.log("✅ Basic Supabase insert works")

                # Test retrieval
                get_response = self.supabase.table('innovations').select('*').eq('id', test_id).execute()
                if get_response.data:
                    self.log("✅ Basic Supabase retrieval works")
                    retrieved_data = get_response.data[0]
                    self.log(f"    - Retrieved: {retrieved_data.get('title', 'No title')}")

                # Clean up
                self.supabase.table('innovations').delete().eq('id', test_id).execute()
                self.log("🧹 Supabase test data cleaned up")

            # Test 2: Basic Pinecone operation (if it supports it)
            try:
                # Try to upsert a simple record
                test_record = {
                    "id": f"test_{uuid4()}",
                    "metadata": {
                        "title": "Test Record",
                        "content": "This is a test record for integration testing",
                        "test": True
                    }
                }

                # Note: This might fail if we need vectors instead of text
                self.pinecone_index.upsert(vectors=[test_record])
                self.log("✅ Basic Pinecone upsert works")

                # Try to query
                query_response = self.pinecone_index.query(
                    id=test_record["id"],
                    top_k=1,
                    include_metadata=True
                )

                if query_response.matches:
                    self.log("✅ Basic Pinecone query works")

                # Clean up
                self.pinecone_index.delete(ids=[test_record["id"]])
                self.log("🧹 Pinecone test data cleaned up")

            except Exception as pinecone_error:
                self.log(f"⚠️  Pinecone operations need adjustment: {pinecone_error}")

            return True

        except Exception as e:
            self.log(f"❌ Basic operations test failed: {e}")
            return False

    def print_configuration_summary(self):
        """Print current configuration"""
        self.log("⚙️  Configuration Summary:")
        self.log(f"    - Pinecone Index: {settings.PINECONE_INDEX_NAME}")
        self.log(f"    - Embedding Model: {settings.EMBEDDING_MODEL}")
        self.log(f"    - Embedding Dimension: {settings.EMBEDDING_DIMENSION}")
        self.log(f"    - Supabase URL: {settings.SUPABASE_URL[:50]}...")
        self.log(f"    - Database URL: {settings.DATABASE_URL.split('@', 1)[0]}@***")

    async def run_all_checks(self):
        """Run all integration checks"""
        self.log("🚀 Starting Simple Integration Test")
        self.log("=" * 60)

        self.print_configuration_summary()
        self.log("")

        # Run checks
        supabase_ok = await self.check_supabase_schema()
        self.log("")

        pinecone_ok = await self.check_pinecone_setup()
        self.log("")

        operations_ok = await self.test_basic_operations()
        self.log("")

        # Summary
        self.log("📋 SUMMARY:")
        self.log(f"    - Supabase: {'✅ OK' if supabase_ok else '❌ Issues'}")
        self.log(f"    - Pinecone: {'✅ OK' if pinecone_ok else '❌ Issues'}")
        self.log(f"    - Operations: {'✅ OK' if operations_ok else '❌ Issues'}")

        if supabase_ok and pinecone_ok:
            self.log("🎉 Basic integration looks good!")
            self.log("💡 Next steps: Fix any schema mismatches and adjust vector operations")
        else:
            self.log("🔧 Issues found that need attention")

        return supabase_ok and pinecone_ok

async def main():
    """Run the simple integration test"""
    tester = SimpleIntegrationTester()

    try:
        success = await tester.run_all_checks()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
