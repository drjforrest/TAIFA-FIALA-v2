"""
Configuration settings for TAIFA-FIALA backend
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    # Application Settings
    APP_NAME: str = "TAIFA-FIALA API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Supabase Configuration
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_SECRET_KEY: str
    NEXT_PUBLIC_SUPABASE_URL: str
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY: str

    # Database Configuration (for SQLAlchemy pooling)
    user: str
    password: str
    host: str
    port: str
    dbname: str

    # Database URL for SQLAlchemy (constructed from components)
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_HOST: str
    PINECONE_INDEX: str
    PINECONE_INTEGRATED_EMBEDDING: bool
    PINECONE_ENVIRONMENT: str

    # Email Configuration
    SMTP_TLS: Optional[str] = None
    SMTP_PORT: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # AI Services
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None

    # Search APIs
    SERPER_API_KEY: Optional[str] = None
    SERP_API_KEY: Optional[str] = None
    PUBMED_API_KEY: Optional[str] = None

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"

    # Crawl4AI Settings
    CRAWL4AI_MAX_CONCURRENT: int = 5
    CRAWL4AI_TIMEOUT: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Academic Sources
    ARXIV_BASE_URL: str = "http://export.arxiv.org/api/query"
    PUBMED_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    CROSSREF_BASE_URL: str = "https://api.crossref.org/works"

    # RSS Feeds
    RSS_FEEDS: str = "https://techcabal.com/feed/"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Webhook Configuration
    N8N_WEBHOOK_URL: Optional[str] = None

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://taifa-fiala.vercel.app"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"


def get_settings() -> Settings:
    """Get settings based on environment"""
    environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()
