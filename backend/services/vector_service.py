"""
Vector Database Service for TAIFA-FIALA
Pinecone integration for semantic search and similarity matching
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from loguru import logger
from pydantic import BaseModel

from config.settings import settings


class VectorDocument(BaseModel):
    """Document for vector storage"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    """Vector search result"""
    id: str
    score: float
    metadata: Dict[str, Any]
    content: Optional[str] = None


class VectorService:
    """Service for vector operations using Pinecone v4.0.0"""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.embedding_model = None
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embedding_dimension = settings.EMBEDDING_DIMENSION
        
    async def initialize(self):
        """Initialize Pinecone client and embedding model"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Get or create index
            await self._ensure_index_exists()
            
            # Get index reference
            self.index = self.pc.Index(self.index_name)
            
            logger.info(f"Vector service initialized with index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing vector service: {e}")
            raise
    
    async def _ensure_index_exists(self):
        """Ensure the Pinecone index exists"""
        try:
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                
                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",  # or "gcp", "azure"
                        region="us-east-1"  # adjust based on your preference
                    )
                )
                
                # Wait for index to be ready
                import time
                while not self.pc.describe_index(self.index_name).status['ready']:
                    logger.info(f"Waiting for index {self.index_name} to be ready...")
                    time.sleep(1)
                
                logger.info(f"Index {self.index_name} created and ready")
            else:
                logger.info(f"Using existing index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            # Clean and prepare text
            cleaned_text = text.strip()
            if not cleaned_text:
                return [0.0] * self.embedding_dimension
            
            # Generate embedding
            embedding = self.embedding_model.encode(cleaned_text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * self.embedding_dimension
    
    async def upsert_documents(self, documents: List[VectorDocument]) -> bool:
        """Upsert documents to vector database"""
        try:
            if not self.index:
                await self.initialize()
            
            # Prepare vectors for upsert
            vectors = []
            for doc in documents:
                # Generate embedding if not provided
                if not doc.embedding:
                    doc.embedding = self.generate_embedding(doc.content)
                
                vector = {
                    "id": doc.id,
                    "values": doc.embedding,
                    "metadata": {
                        **doc.metadata,
                        "content": doc.content[:1000]  # Store truncated content in metadata
                    }
                }
                vectors.append(vector)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
                
                # Small delay between batches
                if len(vectors) > batch_size:
                    await asyncio.sleep(0.1)
            
            logger.info(f"Successfully upserted {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            return False
    
    async def search_similar(self, query: str, top_k: int = 10, 
                           filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search for similar documents"""
        try:
            if not self.index:
                await self.initialize()
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Perform search
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            # Parse results
            results = []
            for match in search_response.matches:
                result = SearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata,
                    content=match.metadata.get('content', '')
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return []
    
    async def search_innovations(self, query: str, innovation_type: Optional[str] = None,
                               country: Optional[str] = None, top_k: int = 20) -> List[SearchResult]:
        """Search for innovations with filters"""
        
        # Build filter
        filter_dict = {"document_type": "innovation"}
        
        if innovation_type:
            filter_dict["innovation_type"] = innovation_type
        
        if country:
            filter_dict["country"] = country
        
        return await self.search_similar(query, top_k, filter_dict)
    
    async def search_publications(self, query: str, publication_type: Optional[str] = None,
                                year_from: Optional[int] = None, top_k: int = 20) -> List[SearchResult]:
        """Search for publications with filters"""
        
        # Build filter
        filter_dict = {"document_type": "publication"}
        
        if publication_type:
            filter_dict["publication_type"] = publication_type
        
        if year_from:
            filter_dict["year"] = {"$gte": year_from}
        
        return await self.search_similar(query, top_k, filter_dict)
    
    async def add_innovation(self, innovation_id: UUID, title: str, description: str,
                           innovation_type: str, country: str, 
                           additional_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add innovation to vector database"""
        
        # Combine text for embedding
        combined_text = f"{title}. {description}"
        
        # Prepare metadata
        metadata = {
            "document_type": "innovation",
            "innovation_id": str(innovation_id),
            "title": title,
            "innovation_type": innovation_type,
            "country": country,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Create document
        document = VectorDocument(
            id=f"innovation_{innovation_id}",
            content=combined_text,
            metadata=metadata
        )
        
        return await self.upsert_documents([document])
    
    async def add_publication(self, publication_id: UUID, title: str, abstract: str,
                            publication_type: str, authors: List[str],
                            year: Optional[int] = None,
                            additional_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add publication to vector database"""
        
        # Combine text for embedding
        authors_text = ", ".join(authors) if authors else ""
        combined_text = f"{title}. {abstract}. Authors: {authors_text}"
        
        # Prepare metadata
        metadata = {
            "document_type": "publication",
            "publication_id": str(publication_id),
            "title": title,
            "publication_type": publication_type,
            "authors": authors,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        if year:
            metadata["year"] = year
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Create document
        document = VectorDocument(
            id=f"publication_{publication_id}",
            content=combined_text,
            metadata=metadata
        )
        
        return await self.upsert_documents([document])
    
    async def add_news_article(self, article_id: UUID, title: str, content: str,
                             source: str, relevance_scores: Dict[str, float],
                             additional_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add news article to vector database"""
        
        # Combine text for embedding
        combined_text = f"{title}. {content[:2000]}"  # Limit content length
        
        # Prepare metadata
        metadata = {
            "document_type": "news_article",
            "article_id": str(article_id),
            "title": title,
            "source": source,
            "ai_relevance_score": relevance_scores.get("ai_relevance_score", 0.0),
            "african_relevance_score": relevance_scores.get("african_relevance_score", 0.0),
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Create document
        document = VectorDocument(
            id=f"article_{article_id}",
            content=combined_text,
            metadata=metadata
        )
        
        return await self.upsert_documents([document])
    
    async def find_similar_innovations(self, innovation_id: UUID, top_k: int = 5) -> List[SearchResult]:
        """Find innovations similar to a given innovation"""
        
        # First, get the innovation's embedding
        try:
            fetch_response = self.index.fetch(ids=[f"innovation_{innovation_id}"])
            
            if not fetch_response.vectors:
                logger.warning(f"Innovation {innovation_id} not found in vector database")
                return []
            
            innovation_vector = fetch_response.vectors[f"innovation_{innovation_id}"].values
            
            # Search for similar innovations (excluding the original)
            search_response = self.index.query(
                vector=innovation_vector,
                top_k=top_k + 1,  # +1 to account for the original
                include_metadata=True,
                filter={"document_type": "innovation"}
            )
            
            # Filter out the original innovation
            results = []
            for match in search_response.matches:
                if match.id != f"innovation_{innovation_id}":
                    result = SearchResult(
                        id=match.id,
                        score=match.score,
                        metadata=match.metadata,
                        content=match.metadata.get('content', '')
                    )
                    results.append(result)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar innovations: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        try:
            if not self.index:
                await self.initialize()
            
            # Get index stats
            stats = self.index.describe_index_stats()
            
            return {
                "total_vectors": stats.total_vector_count,
                "index_fullness": stats.index_fullness,
                "dimension": stats.dimension,
                "namespaces": stats.namespaces
            }
            
        except Exception as e:
            logger.error(f"Error getting vector database stats: {e}")
            return {}
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from vector database"""
        try:
            if not self.index:
                await self.initialize()
            
            self.index.delete(ids=[document_id])
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False


# Global vector service instance
vector_service = VectorService()


async def get_vector_service() -> VectorService:
    """Get initialized vector service"""
    if not vector_service.index:
        await vector_service.initialize()
    return vector_service


if __name__ == "__main__":
    # Test the vector service
    async def test_vector_service():
        service = await get_vector_service()
        
        # Test adding a document
        success = await service.add_innovation(
            innovation_id=uuid4(),
            title="AI-Powered Crop Disease Detection",
            description="Mobile app using computer vision to identify crop diseases in Kenya",
            innovation_type="AgriTech",
            country="Kenya"
        )
        
        print(f"Document added: {success}")
        
        # Test search
        results = await service.search_innovations("crop disease detection Kenya")
        print(f"Search results: {len(results)}")
        
        for result in results:
            print(f"- {result.metadata.get('title', 'No title')} (score: {result.score:.3f})")
    
    asyncio.run(test_vector_service())