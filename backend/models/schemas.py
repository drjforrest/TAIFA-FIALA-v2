"""
Pydantic schemas for TAIFA-FIALA API requests and responses
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, HttpUrl


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    COMMUNITY = "community"
    REJECTED = "rejected"


class InnovationType(str, Enum):
    HEALTHTECH = "HealthTech"
    AGRITECH = "AgriTech"
    FINTECH = "FinTech"
    EDTECH = "EdTech"
    CLEANTECH = "CleanTech"
    LOGISTICS = "Logistics"
    EGOVERNMENT = "E-Government"
    MEDIA = "Media & Entertainment"
    SECURITY = "Security"
    OTHER = "Other"


class OrganizationType(str, Enum):
    STARTUP = "startup"
    UNIVERSITY = "university"
    RESEARCH_INSTITUTE = "research_institute"
    NGO = "ngo"
    CORPORATION = "corporation"
    GOVERNMENT = "government"
    OTHER = "other"


class PublicationType(str, Enum):
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    BOOK = "book"
    THESIS = "thesis"


class SourceType(str, Enum):
    ACADEMIC = "academic"
    COMMUNITY = "community"
    NEWS = "news"
    MANUAL = "manual"


# Base Models
class InnovationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=10)
    innovation_type: InnovationType
    creation_date: Optional[date] = None
    problem_solved: Optional[str] = None
    solution_approach: Optional[str] = None
    impact_metrics: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    website_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None


class InnovationCreate(InnovationBase):
    # Additional fields for creation
    submitter_name: str = Field(..., min_length=1, max_length=100)
    submitter_email: EmailStr
    organization_name: Optional[str] = None
    country: str = Field(..., min_length=2, max_length=100)
    team_size: Optional[int] = Field(None, ge=1)
    funding_amount: Optional[float] = Field(None, ge=0)
    funding_currency: Optional[str] = Field(None, max_length=3)


class InnovationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=10)
    innovation_type: Optional[InnovationType] = None
    problem_solved: Optional[str] = None
    solution_approach: Optional[str] = None
    impact_metrics: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    website_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    verification_status: Optional[VerificationStatus] = None


class InnovationResponse(InnovationBase):
    id: UUID
    verification_status: VerificationStatus
    visibility: str
    created_at: datetime
    updated_at: datetime
    source_type: Optional[SourceType] = None
    source_url: Optional[HttpUrl] = None
    
    # Related data
    organizations: List['OrganizationSummary'] = []
    individuals: List['IndividualSummary'] = []
    publications: List['PublicationSummary'] = []
    fundings: List['FundingSummary'] = []

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    organization_type: OrganizationType
    country: str = Field(..., min_length=2, max_length=100)
    website: Optional[HttpUrl] = None
    founded_date: Optional[date] = None
    description: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[HttpUrl] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    source_type: Optional[SourceType] = None
    source_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class OrganizationSummary(BaseModel):
    id: UUID
    name: str
    organization_type: OrganizationType
    country: str
    website: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class IndividualBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    country: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = Field(None, max_length=50)
    github_username: Optional[str] = Field(None, max_length=50)
    orcid_id: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[HttpUrl] = None


class IndividualCreate(IndividualBase):
    pass


class IndividualResponse(IndividualBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    source_type: Optional[SourceType] = None
    source_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class IndividualSummary(BaseModel):
    id: UUID
    name: str
    role: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True


class PublicationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    publication_type: PublicationType
    publication_date: Optional[date] = None
    doi: Optional[str] = Field(None, max_length=100)
    url: Optional[HttpUrl] = None
    journal: Optional[str] = Field(None, max_length=200)
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    citation_count: Optional[int] = Field(None, ge=0)
    venue: Optional[str] = Field(None, max_length=200)
    volume: Optional[str] = Field(None, max_length=20)
    issue: Optional[str] = Field(None, max_length=20)
    pages: Optional[str] = Field(None, max_length=50)


class PublicationCreate(PublicationBase):
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    crossref_id: Optional[str] = None


class PublicationResponse(PublicationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    source_type: SourceType
    source_url: Optional[HttpUrl] = None
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    crossref_id: Optional[str] = None

    class Config:
        from_attributes = True


class PublicationSummary(BaseModel):
    id: UUID
    title: str
    publication_type: PublicationType
    publication_date: Optional[date] = None
    journal: Optional[str] = None

    class Config:
        from_attributes = True


class FundingBase(BaseModel):
    amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    funding_date: Optional[date] = None
    funding_type: Optional[str] = Field(None, max_length=100)
    funding_round: Optional[str] = Field(None, max_length=50)
    announcement_url: Optional[HttpUrl] = None
    notes: Optional[str] = None


class FundingCreate(FundingBase):
    innovation_id: UUID
    funder_org_id: UUID


class FundingResponse(FundingBase):
    id: UUID
    innovation_id: UUID
    funder_org_id: UUID
    verified: bool
    created_at: datetime
    updated_at: datetime
    source_type: Optional[SourceType] = None
    source_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class FundingSummary(BaseModel):
    id: UUID
    amount: Optional[float] = None
    currency: Optional[str] = None
    funding_date: Optional[date] = None
    funding_type: Optional[str] = None
    verified: bool

    class Config:
        from_attributes = True


class CommunitySubmissionCreate(BaseModel):
    innovation_data: InnovationCreate
    evidence_files: Optional[List[str]] = None  # File paths/URLs


class CommunitySubmissionResponse(BaseModel):
    id: UUID
    innovation_id: UUID
    submitter_name: str
    submitter_email: EmailStr
    submission_status: str
    evidence_files: Optional[List[str]] = None
    community_votes: Optional[Dict[str, int]] = None
    expert_reviews: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunityVote(BaseModel):
    submission_id: UUID
    vote_type: str = Field(..., pattern="^(positive|negative|neutral)$")
    comment: Optional[str] = None
    voter_email: EmailStr


class ExpertReview(BaseModel):
    submission_id: UUID
    reviewer_name: str
    reviewer_email: EmailStr
    review_status: str = Field(..., pattern="^(approve|reject|needs_info)$")
    review_comments: str
    expertise_areas: List[str]


class NewsArticleResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str] = None
    url: HttpUrl
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    source: str
    extracted_innovations: Optional[List[Dict[str, Any]]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    relevance_score: Optional[float] = None
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Search and Filter Models
class InnovationSearchParams(BaseModel):
    query: Optional[str] = None
    innovation_type: Optional[InnovationType] = None
    country: Optional[str] = None
    verification_status: Optional[VerificationStatus] = None
    tags: Optional[List[str]] = None
    min_funding: Optional[float] = None
    max_funding: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|title|funding_amount)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class InnovationSearchResponse(BaseModel):
    innovations: List[InnovationResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# Analytics and Stats Models
class InnovationStats(BaseModel):
    total_innovations: int
    verified_innovations: int
    pending_innovations: int
    innovations_by_type: Dict[str, int]
    innovations_by_country: Dict[str, int]
    innovations_by_month: Dict[str, int]
    total_funding: Optional[float] = None
    average_funding: Optional[float] = None


class ETLJobStatus(BaseModel):
    job_id: UUID
    job_type: str  # 'academic', 'news', 'community'
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results_summary: Optional[Dict[str, Any]] = None


# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


# Update forward references
InnovationResponse.model_rebuild()
OrganizationResponse.model_rebuild()
IndividualResponse.model_rebuild()
PublicationResponse.model_rebuild()