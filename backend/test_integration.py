#!/usr/bin/env python3
"""
TAIFA-FIALA Integration Test
============================

Comprehensive test to verify that:
1. Pinecone vector database is correctly configured for full-text vectorization
2. Supabase client is properly set up for metadata storage
3. Complete ETL pipeline works end-to-end
4. Data flows correctly between services

Usage:
    python test_integration.py
"""

import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from config.database import get_supabase, get_db
from services.vector_service import get_vector_service, VectorDocument
# from models.database import Innovation, Organization, Publication
from sqlalchemy.orm import Session

class IntegrationTester:
    """Comprehensive integration tester for TAIFA-FIALA services"""

    def __init__(self):
        self.supabase = None
        self.vector_service = None
        self.db_session = None
        self.test_results = []

    async def initialize(self):
        """Initialize all services"""
        print("🔧 Initializing integration test services...")

        try:
            # Initialize Supabase client
            self.supabase = get_supabase()
            print("✅ Supabase client initialized")

            # Initialize Vector service
            self.vector_service = await get_vector_service()
            print("✅ Pinecone vector service initialized")

            # Get database session
            self.db_session = next(get_db())
            print("✅ Database session established")

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")

        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    async def test_pinecone_connection(self):
        """Test Pinecone vector database connection and basic operations"""
        print("\n🔍 Testing Pinecone Vector Database...")

        try:
            # Test connection by getting stats
            stats = await self.vector_service.get_stats()
            self.log_test("Pinecone Connection", True, f"Connected to index with {stats.get('total_vectors', 0)} vectors")

            # Test embedding generation
            test_text = "AI-powered crop disease detection using computer vision in Kenya"
            embedding = self.vector_service.generate_embedding(test_text)

            expected_dimension = settings.EMBEDDING_DIMENSION
            actual_dimension = len(embedding)

            self.log_test(
                "Embedding Generation",
                actual_dimension == expected_dimension,
                f"Generated {actual_dimension}D embedding (expected {expected_dimension}D)"
            )

            # Test document vectorization
            test_doc = VectorDocument(
                id=f"test_integration_{uuid4()}",
                content=test_text,
                metadata={
                    "title": "Test Innovation",
                    "innovation_type": "AgriTech",
                    "country": "Kenya",
                    "test": True
                }
            )

            success = await self.vector_service.upsert_documents([test_doc])
            self.log_test("Document Vectorization", success, "Successfully vectorized and stored document")

            # Test similarity search
            search_results = await self.vector_service.search_similar("crop disease Kenya", top_k=5)
            found_test_doc = any(result.metadata.get("test") == True for result in search_results)

            self.log_test(
                "Vector Similarity Search",
                found_test_doc,
                f"Found {len(search_results)} similar documents, including test document"
            )

            return True

        except Exception as e:
            self.log_test("Pinecone Integration", False, f"Error: {e}")
            return False

    async def test_supabase_connection(self):
        """Test Supabase connection and metadata operations"""
        print("\n🗄️  Testing Supabase Database...")

        try:
            # Test basic connection by querying health
            response = self.supabase.table('innovations').select('id').limit(1).execute()
            self.log_test("Supabase Connection", True, "Successfully connected and queried innovations table")

            # Test metadata insertion
            test_innovation = {
                "id": str(uuid4()),
                "title": "Test AI Innovation for Integration",
                "description": "This is a test innovation to verify Supabase integration works correctly",
                "innovation_type": "TestTech",
                "verification_status": "pending",
                "visibility": "public",
                "source_type": "integration_test",
                "tags": ["test", "integration", "ai"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Insert test innovation
            insert_response = self.supabase.table('innovations').insert(test_innovation).execute()
            insertion_success = len(insert_response.data) > 0

            self.log_test(
                "Metadata Storage",
                insertion_success,
                f"Inserted test innovation with ID: {test_innovation['id']}"
            )

            # Test metadata retrieval
            if insertion_success:
                retrieve_response = self.supabase.table('innovations').select('*').eq('id', test_innovation['id']).execute()
                retrieval_success = len(retrieve_response.data) > 0

                self.log_test(
                    "Metadata Retrieval",
                    retrieval_success,
                    f"Retrieved innovation: {retrieve_response.data[0]['title'] if retrieval_success else 'None'}"
                )

                # Cleanup test data
                self.supabase.table('innovations').delete().eq('id', test_innovation['id']).execute()
                self.log_test("Test Data Cleanup", True, "Removed test innovation from database")

            return True

        except Exception as e:
            self.log_test("Supabase Integration", False, f"Error: {e}")
            return False

    async def test_full_text_vectorization(self):
        """Test complete full-text vectorization pipeline"""
        print("\n📄 Testing Full-Text Vectorization...")

        try:
            # Test different types of content
            test_documents = [
                {
                    "title": "Mobile Health App for Rural Tanzania",
                    "description": "A comprehensive mobile application that uses AI to provide healthcare diagnostics and treatment recommendations for rural communities in Tanzania. The app leverages machine learning algorithms trained on local health data to provide culturally appropriate medical advice.",
                    "type": "HealthTech",
                    "country": "Tanzania"
                },
                {
                    "title": "Agricultural Yield Prediction System",
                    "description": "Deep learning system that analyzes satellite imagery, weather patterns, and soil data to predict crop yields for smallholder farmers across West Africa. The system provides early warnings for potential crop failures and optimization recommendations.",
                    "type": "AgriTech",
                    "country": "Ghana"
                },
                {
                    "title": "Financial Inclusion Platform",
                    "description": "Blockchain-based microfinance platform that uses natural language processing to assess creditworthiness from alternative data sources including mobile money transactions and social media activity for unbanked populations in Kenya.",
                    "type": "FinTech",
                    "country": "Kenya"
                }
            ]

            # Vectorize each document
            vectorized_docs = []
            for i, doc_data in enumerate(test_documents):
                full_text = f"{doc_data['title']}. {doc_data['description']}"

                vector_doc = VectorDocument(
                    id=f"fulltext_test_{i}_{uuid4()}",
                    content=full_text,
                    metadata={
                        "title": doc_data["title"],
                        "innovation_type": doc_data["type"],
                        "country": doc_data["country"],
                        "document_type": "innovation",
                        "test_batch": "full_text_vectorization"
                    }
                )

                vectorized_docs.append(vector_doc)

            # Batch upsert all documents
            success = await self.vector_service.upsert_documents(vectorized_docs)
            self.log_test(
                "Batch Full-Text Vectorization",
                success,
                f"Successfully vectorized {len(vectorized_docs)} full-text documents"
            )

            # Test semantic search across all documents
            search_queries = [
                "healthcare mobile app Tanzania",
                "crop prediction satellite imagery",
                "microfinance blockchain Kenya",
                "AI for agriculture West Africa"
            ]

            total_relevant_results = 0
            for query in search_queries:
                results = await service.search_similar(query)
                # Count results from our test batch
                relevant_results = [r for r in results if r.metadata.get("test_batch") == "full_text_vectorization"]
                total_relevant_results += len(relevant_results)

                print(f"    Query: '{query}' -> {len(relevant_results)} relevant results")

            self.log_test(
                "Semantic Search Accuracy",
                total_relevant_results > 0,
                f"Found {total_relevant_results} semantically relevant results across all queries"
            )

            return True

        except Exception as e:
            self.log_test("Full-Text Vectorization", False, f"Error: {e}")
            return False

    async def test_end_to_end_pipeline(self):
        """Test complete end-to-end data pipeline"""
        print("\n🔄 Testing End-to-End Pipeline...")

        try:
            # Simulate a complete innovation record
            innovation_id = uuid4()
            innovation_data = {
                "id": str(innovation_id),
                "title": "E2E Test: AI-Powered Education Platform",
                "description": "An intelligent tutoring system that adapts to individual student learning patterns using reinforcement learning. The platform provides personalized educational content for students across multiple African languages and curricula, addressing the educational technology gap in underserved communities.",
                "innovation_type": "EdTech",
                "problem_solved": "Lack of personalized education in resource-constrained environments",
                "solution_approach": "AI-driven adaptive learning with multilingual support",
                "impact_metrics": "Improved learning outcomes for 10,000+ students",
                "tech_stack": ["Python", "TensorFlow", "React", "Node.js"],
                "tags": ["education", "ai", "adaptive-learning", "multilingual"],
                "verification_status": "verified",
                "visibility": "public",
                "source_type": "integration_test",
                "website_url": "https://example-edtech.com",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Step 1: Store metadata in Supabase
            supabase_response = self.supabase.table('innovations').insert(innovation_data).execute()
            metadata_stored = len(supabase_response.data) > 0

            self.log_test(
                "E2E: Metadata Storage",
                metadata_stored,
                f"Stored innovation metadata in Supabase"
            )

            # Step 2: Vectorize full text content for Pinecone
            if metadata_stored:
                full_content = f"{innovation_data['title']}. {innovation_data['description']}. Problem: {innovation_data['problem_solved']}. Solution: {innovation_data['solution_approach']}. Impact: {innovation_data['impact_metrics']}"

                vector_success = await self.vector_service.add_innovation(
                    innovation_id=innovation_id,
                    title=innovation_data['title'],
                    description=full_content,
                    innovation_type=innovation_data['innovation_type'],
                    country="Multi-country",
                    additional_metadata={
                        "tech_stack": innovation_data['tech_stack'],
                        "website_url": innovation_data['website_url'],
                        "test_type": "e2e_pipeline"
                    }
                )

                self.log_test(
                    "E2E: Vector Storage",
                    vector_success,
                    "Vectorized and stored full-text content in Pinecone"
                )

                # Step 3: Test retrieval and search
                if vector_success:
                    # Test metadata retrieval from Supabase
                    metadata_query = self.supabase.table('innovations').select('*').eq('id', str(innovation_id)).execute()
                    metadata_retrieved = len(metadata_query.data) > 0

                    # Test vector search in Pinecone
                    vector_results = await self.vector_service.search_innovations(
                        query="educational technology adaptive learning",
                        top_k=5
                    )
                    vector_found = any(
                        result.metadata.get("innovation_id") == str(innovation_id)
                        for result in vector_results
                    )

                    self.log_test(
                        "E2E: Data Retrieval",
                        metadata_retrieved and vector_found,
                        f"Successfully retrieved from both Supabase and Pinecone"
                    )

                    # Step 4: Test cross-referencing
                    if metadata_retrieved and vector_found:
                        supabase_title = metadata_query.data[0]['title']
                        vector_title = next(
                            (r.metadata.get('title') for r in vector_results
                             if r.metadata.get("innovation_id") == str(innovation_id)), None)

                        titles_match = supabase_title == vector_title
                    self.log_test(
                            "E2E: Data Consistency",
                            titles_match,
                            f"Data consistent across services: {supabase_title == vector_title}"
                        )

            # Cleanup
            self.supabase.table('innovations').delete().eq('id', str(innovation_id)).execute()
            await self.vector_service.delete_document(f"innovation_{innovation_id}")

            return True

        except Exception as e:
            self.log_test("End-to-End Pipeline", False, f"Error: {e}")
            return False

    async def test_environment_configuration(self):
        """Test that all required environment variables are configured"""
        print("\n⚙️  Testing Environment Configuration...")

        required_vars = [
            ("PINECONE_API_KEY", "Pinecone API key"),
            ("PINECONE_INDEX_NAME", "Pinecone index name"),
            ("SUPABASE_URL", "Supabase URL"),
            ("SUPABASE_SERVICE_ROLE_KEY", "Supabase service role key"),
            ("DATABASE_URL", "Database connection string")
        ]

        all_configured = True
        for var_name, description in required_vars:
            value = getattr(settings, var_name, None)
            is_configured = value is not None and value != ""

        self.log_test(
        f"Config: {description}",
        #     is_configured,
        # "Configured" if is_configured else "Missing or empty"
        # )

        if not is_configured:
            all_configured = False

    if __name__ == "__main__":
        tester = IntegrationTester()
        asyncio.run(tester.initialize())
            asyncio.run(tester.test_pinecone_connection())
            asyncio.run(tester.test_supabase_connection())
            asyncio.run(tester.test_full_text_vectorization())
            asyncio.run(tester.test_end_to_end_pipeline())
            asyncio.run(tester.test_environment_configuration())
        print("All tests completed.")
    # embedding_dimension = settings.EMBEDDING_DIMENSION

    # self.log_test(
    "Embedding Model Config",
    bool(embedding_model and embedding_dimension > 0),
    f"Model: {embedding_model}, Dimension: {embedding_dimension}"
    # )

        # return all_configured

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📋 INTEGRATION TEST SUMMARY")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['details']}")

        print("\n🎯 INTEGRATION STATUS:")
        if failed_tests == 0:
            print("✅ ALL SYSTEMS OPERATIONAL")
            print("🚀 Pinecone and Supabase integration working perfectly!")
        else:
            print("⚠️  ISSUES DETECTED")
            print("🔧 Please review failed tests and fix configuration issues.")

        return failed_tests == 0


async def main():
    """Run all integration tests"""
    print("🚀 TAIFA-FIALA Integration Test Suite")
    print("="*60)

    tester = IntegrationTester()

    try:
        # Initialize services
        await tester.initialize()

        # Run all tests
        await tester.test_environment_configuration()
        await tester.test_pinecone_connection()
        await tester.test_supabase_connection()
        await tester.test_full_text_vectorization()
        await tester.test_end_to_end_pipeline()

        # Print summary
        success = tester.print_summary()

        # Save detailed results
        with open('integration_test_results.json', 'w') as f:
            json.dump(tester.test_results, f, indent=2)

        print(f"\n📁 Detailed results saved to: integration_test_results.json")

        return 0 if success else 1

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        print("🔧 Please check your configuration and try again.")
        return 1

    finally:
        # Cleanup
        if tester.db_session:
            tester.db_session.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
