# TAIFA-FIALA Backend API

FastAPI-based backend for the TAIFA-FIALA African AI Innovation Archive platform.

## Features

- **Academic ETL Pipeline**: ArXiv paper scraping for African AI research
- **RSS News Monitoring**: Community monitoring of African tech news
- **Crawl4AI Integration**: Advanced web scraping for innovation discovery
- **Serper.dev Search**: Precision search for African AI innovations
- **Vector Database**: Pinecone-powered semantic search
- **Community Verification**: Multi-tier validation system

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT`
- `SERPER_API_KEY`
- `OPENAI_API_KEY` (optional, for enhanced extraction)

### 3. Database Setup

The application uses Supabase as the primary database. Run migrations:

```bash
# Using Alembic (if set up)
alembic upgrade head
```

### 4. Run the Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Core Endpoints

- `GET /api/innovations` - List innovations with filtering
- `POST /api/innovations` - Submit new innovation
- `GET /api/innovations/{id}` - Get specific innovation
- `GET /api/search` - Vector-powered semantic search

### ETL Endpoints

- `POST /api/etl/academic` - Trigger academic paper scraping
- `POST /api/etl/news` - Trigger RSS news monitoring
- `POST /api/etl/serper-search` - Trigger Serper.dev search

### Community Endpoints

- `GET /api/community/submissions` - Get pending submissions
- `POST /api/community/vote` - Submit community verification vote

### Statistics

- `GET /api/stats` - Platform statistics
- `GET /api/health` - Health check

## Data Pipeline Architecture

### Academic ETL
- **ArXiv Scraper**: Searches for African AI papers using targeted queries
- **Relevance Scoring**: Calculates African and AI relevance scores
- **Entity Extraction**: Identifies African countries, institutions, and individuals

### News Monitoring
- **RSS Feeds**: Monitors major African tech news sources
- **Content Analysis**: Extracts innovation mentions and funding announcements
- **Relevance Filtering**: Filters for African AI innovations

### Web Discovery
- **Serper.dev Integration**: Precision Google searches for African innovations
- **Crawl4AI Processing**: Advanced content extraction from innovation websites
- **LLM Enhancement**: Optional OpenAI integration for structured data extraction

### Vector Database
- **Pinecone Integration**: Semantic search across all content types
- **Embedding Generation**: sentence-transformers for text embeddings
- **Similarity Matching**: Find related innovations and publications

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI application
├── run.py              # Startup script
├── config/             # Configuration management
├── models/             # Database models and schemas
├── services/           # External service integrations
├── etl/                # ETL pipelines
│   ├── academic/       # Academic paper processing
│   ├── news/          # News monitoring
│   └── community/     # Community contributions
├── api/               # API route handlers
└── tests/             # Test suite
```

### Testing

```bash
pytest tests/
```

### Deployment

The backend is designed to be deployed using Docker containers on AWS/GCP with the frontend on Vercel.

## Rate Limiting

- Most endpoints: 30 requests/minute
- ETL triggers: 3-5 requests/minute
- Community votes: 50 requests/minute

## Monitoring

The application includes:
- Structured logging with Loguru
- Health check endpoints
- Background task monitoring
- Vector database performance metrics