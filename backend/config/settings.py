"""
Configuration settings for TAIFA-FIALA backend
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "TAIFA-FIALA API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATABASE_URL: str
    
    # Vector Database (Pinecone)
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "taifa-fiala-innovations"
    
    # Search APIs
    SERPER_API_KEY: str
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    
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
    
    # RSS Feeds for Community Monitoring
    RSS_FEEDS: List[str] = [
        "https://techcabal.com/feed/",
        "https://ventureburn.com/feed/",
        "https://disrupt-africa.com/feed/",
        "https://africanbusinesscentral.com/feed/",
        "https://www.itnewsafrica.com/feed/"
    ]
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "video/mp4",
        "video/quicktime"
    ]
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://taifa-fiala.vercel.app"
    ]
    
    # Academic Search Keywords
    AFRICAN_AI_KEYWORDS: List[str] = [
        "artificial intelligence africa",
        "machine learning africa",
        "AI africa",
        "ML africa",
        "deep learning africa",
        "natural language processing africa",
        "computer vision africa",
        "robotics africa",
        "data science africa",
        "tech innovation africa",
        "african AI research",
        "african machine learning",
        "AI for development africa",
        "AI4D africa"
    ]
    
    # African Countries for Filtering
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
    
    # African Universities and Research Institutions
    AFRICAN_INSTITUTIONS: List[str] = [
        "University of Cape Town",
        "University of the Witwatersrand",
        "Stellenbosch University",
        "University of Pretoria",
        "Cairo University",
        "American University in Cairo",
        "University of Nairobi",
        "Makerere University",
        "University of Ghana",
        "Addis Ababa University",
        "Mohammed V University",
        "University of Lagos",
        "Obafemi Awolowo University",
        "Covenant University",
        "Nelson Mandela University",
        "Rhodes University",
        "University of KwaZulu-Natal",
        "Ashesi University",
        "African Institute for Mathematical Sciences",
        "Data Science Africa"
    ]
    
    # ETL Configuration
    ETL_BATCH_SIZE: int = 50
    ETL_CONCURRENT_WORKERS: int = 3
    ETL_RETRY_ATTEMPTS: int = 3
    ETL_RETRY_DELAY: int = 5  # seconds
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Search Configuration
    SEARCH_RESULTS_PER_PAGE: int = 20
    MAX_SEARCH_RESULTS: int = 100
    
    # Community Verification Settings
    MIN_COMMUNITY_VOTES: int = 5
    MIN_EXPERT_REVIEWS: int = 1
    EXPERT_VERIFICATION_THRESHOLD: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    class Config:
        env_file = ".env.development"


class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    
    class Config:
        env_file = ".env.production"


class TestingSettings(Settings):
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/15"  # Different DB for testing
    
    class Config:
        env_file = ".env.testing"


def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()