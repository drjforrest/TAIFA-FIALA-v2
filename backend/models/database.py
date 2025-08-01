"""
Database models for TAIFA-FIALA Innovation Archive
Implements the schema from the Product Requirements Document
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, Date, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, Field

Base = declarative_base()

# Association tables for many-to-many relationships
innovation_organizations = Table(
    'innovation_organizations',
    Base.metadata,
    Column('innovation_id', PostgreSQLUUID(as_uuid=True), ForeignKey('innovations.id'), primary_key=True),
    Column('organization_id', PostgreSQLUUID(as_uuid=True), ForeignKey('organizations.id'), primary_key=True),
    Column('relationship_type', String, nullable=False)
)

innovation_individuals = Table(
    'innovation_individuals', 
    Base.metadata,
    Column('innovation_id', PostgreSQLUUID(as_uuid=True), ForeignKey('innovations.id'), primary_key=True),
    Column('individual_id', PostgreSQLUUID(as_uuid=True), ForeignKey('individuals.id'), primary_key=True),
    Column('relationship_type', String, nullable=False)
)

innovation_publications = Table(
    'innovation_publications',
    Base.metadata,
    Column('innovation_id', PostgreSQLUUID(as_uuid=True), ForeignKey('innovations.id'), primary_key=True),
    Column('publication_id', PostgreSQLUUID(as_uuid=True), ForeignKey('publications.id'), primary_key=True),
    Column('relationship_type', String, nullable=False)
)

class Innovation(Base):
    __tablename__ = "innovations"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    innovation_type: Mapped[str] = mapped_column(String, nullable=False)
    creation_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    verification_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    visibility: Mapped[str] = mapped_column(String, nullable=False, default="public")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields for enhanced innovation tracking
    problem_solved: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution_approach: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    impact_metrics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Data source tracking
    source_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'academic', 'community', 'manual'
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    extraction_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    organizations = relationship("Organization", secondary=innovation_organizations, back_populates="innovations")
    individuals = relationship("Individual", secondary=innovation_individuals, back_populates="innovations")
    publications = relationship("Publication", secondary=innovation_publications, back_populates="innovations")
    fundings = relationship("Funding", back_populates="innovation")


class Organization(Base):
    __tablename__ = "organizations"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    organization_type: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    founded_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional organization fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    twitter_handle: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Data source tracking
    source_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    innovations = relationship("Innovation", secondary=innovation_organizations, back_populates="organizations")
    fundings_given = relationship("Funding", back_populates="funder_org")


class Individual(Base):
    __tablename__ = "individuals"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional individual fields
    linkedin_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    twitter_handle: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    github_username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    orcid_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Data source tracking
    source_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    innovations = relationship("Innovation", secondary=innovation_individuals, back_populates="individuals")


class Funding(Base):
    __tablename__ = "fundings"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    innovation_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey('innovations.id'))
    funder_org_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey('organizations.id'))
    amount: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    funding_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    funding_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional funding fields
    funding_round: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'seed', 'series_a', etc.
    announcement_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Data source tracking
    source_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    innovation = relationship("Innovation", back_populates="fundings")
    funder_org = relationship("Organization", back_populates="fundings_given")


class Publication(Base):
    __tablename__ = "publications"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    publication_type: Mapped[str] = mapped_column(String, nullable=False)  # 'journal', 'conference', 'preprint'
    publication_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional publication fields
    authors: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    citation_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    volume: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    issue: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pages: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Academic source tracking
    arxiv_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pubmed_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    crossref_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Data source tracking
    source_type: Mapped[str] = mapped_column(String, nullable=False, default="academic")
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    extraction_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    innovations = relationship("Innovation", secondary=innovation_publications, back_populates="publications")


class Embedding(Base):
    __tablename__ = "embeddings"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # 'innovation', 'publication', 'organization'
    source_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    vector_id: Mapped[str] = mapped_column(String, nullable=False)  # Pinecone vector ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Embedding metadata
    embedding_model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original text that was embedded


class LegacyFundingAnnouncement(Base):
    __tablename__ = "legacy_funding_announcements"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    original_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    archived_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Migration tracking
    migrated_to_innovation_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=True)
    migration_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CommunitySubmission(Base):
    """Track community-submitted innovations and their verification process"""
    __tablename__ = "community_submissions"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    innovation_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey('innovations.id'))
    submitter_name: Mapped[str] = mapped_column(String, nullable=False)
    submitter_email: Mapped[str] = mapped_column(String, nullable=False)
    submission_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # pending, verified, rejected
    evidence_files: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    community_votes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    expert_reviews: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    innovation = relationship("Innovation")


class NewsArticle(Base):
    """Track news articles and community monitoring data"""
    __tablename__ = "news_articles"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)  # RSS feed source
    
    # AI Analysis
    extracted_innovations: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    ai_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    
    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)