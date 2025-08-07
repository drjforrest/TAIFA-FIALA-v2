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
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
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

    # Database URL (can be override or constructed from components)
    DATABASE_URL: Optional[str] = None
    
    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_HOST: str
    PINECONE_INDEX: str
    PINECONE_INDEX_NAME: str
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
    
    # Development control flags (overridden in DevelopmentSettings)
    DISABLE_AI_ENRICHMENT: bool = False
    DISABLE_EXTERNAL_SEARCH: bool = False
    DISABLE_RSS_MONITORING: bool = False
    DISABLE_ACADEMIC_SCRAPING: bool = False
    ENABLE_MOCK_DATA: bool = False
    REDIS_REQUIRED: bool = True
    MAX_ETL_BATCH_SIZE: int = 50
    MAX_AI_CALLS_PER_MINUTE: int = 60

    # Academic Sources
    ARXIV_BASE_URL: str = "http://export.arxiv.org/api/query"
    PUBMED_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    CROSSREF_BASE_URL: str = "https://api.crossref.org/works"

    # RSS Feeds  
    RSS_FEEDS: Optional[List[str]] = None

    @property
    def rss_feeds(self) -> List[str]:
        """Get RSS feeds with default values"""
        return self.RSS_FEEDS or [
            "https://techcabal.com/feed/",
            "https://ventureburn.com/feed/",
            "https://disrupt-africa.com/feed/",
            "https://itnewsafrica.com/feed/"
        ]

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

    # African Countries for ETL filtering
    AFRICAN_COUNTRIES: List[str] = [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
        "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
        "Congo", "Democratic Republic of Congo", "Djibouti", "Egypt",
        "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
        "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya",
        "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali",
        "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
        "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles",
        "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan",
        "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
    ]

    # African institutions for research filtering
    AFRICAN_INSTITUTIONS: List[str] = [
        "University of Cape Town", "University of the Witwatersrand", "Stellenbosch University",
        "Cairo University", "American University in Cairo", "University of Nairobi",
        "Makerere University", "University of Ghana", "University of Lagos",
        "Addis Ababa University", "Mohammed V University", "University of Tunis"
    ]

    # AI keywords for academic search
    AFRICAN_AI_KEYWORDS: List[str] = [
        "artificial intelligence", "machine learning", "deep learning",
        "neural networks", "computer vision", "natural language processing",
        "data science", "automation", "robotics"
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields from environment
    }


class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # More permissive CORS for development
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://taifa-fiala.vercel.app"
    ]
    
    # Redis Configuration for development (use in-memory fallback if not available)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_REQUIRED: bool = False
    
    # Development flags to disable expensive operations
    DISABLE_AI_ENRICHMENT: bool = True
    DISABLE_EXTERNAL_SEARCH: bool = True
    DISABLE_RSS_MONITORING: bool = True
    DISABLE_ACADEMIC_SCRAPING: bool = True
    ENABLE_MOCK_DATA: bool = True
    
    # Limit batch sizes in development
    MAX_ETL_BATCH_SIZE: int = 5
    MAX_AI_CALLS_PER_MINUTE: int = 2


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
