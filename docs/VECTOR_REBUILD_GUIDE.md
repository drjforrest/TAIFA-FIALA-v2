# Vector Database Rebuild Guide

## Overview

Your TAIFA-FIALA system uses **Pinecone** with **multilingual-e5-large** embeddings for semantic search. This guide explains how to recreate and monitor your full-text vector database.

## How Vector Search Works

### Traditional vs Vector Search

```bash
# Traditional (current problem)
"machine learning" → Only finds exact matches

# Vector Search (what you have built)
"machine learning" → Finds: "AI", "artificial intelligence", "neural networks", "deep learning"
```

### Your Vector Pipeline

1. **Text Preparation**: `Title + Description + Metadata`
2. **Embedding**: `multilingual-e5-large` (1024 dimensions)
3. **Storage**: Pinecone vector database
4. **Search**: Semantic similarity matching

## Quick Status Check

```bash
# Check current vector database status
cd backend
python scripts/check_vectors.py

# Test search quality
python scripts/check_vectors.py --quick-test

# Test custom search
python scripts/check_vectors.py --search "AI healthcare Nigeria"
```

## Full Vector Rebuild

### When to Rebuild

- **No search results**: Vector database is empty
- **Poor search quality**: Embeddings are outdated
- **New data**: Added many innovations/publications
- **Coverage < 90%**: Missing vector embeddings

### Rebuild Process

```bash
# Full rebuild (recommended)
cd backend
python scripts/rebuild_vectors.py

# This will:
# ✅ Process all innovations from Supabase
# ✅ Process all publications from Supabase  
# ✅ Generate multilingual embeddings
# ✅ Upload to Pinecone in batches
# ✅ Provide detailed statistics
```

### Via API (Background)

```bash
# Trigger rebuild via API
curl -X POST "https://api.taifa-fiala.net/api/vector/rebuild" \
  -H "Content-Type: application/json"

# Check progress
curl "https://api.taifa-fiala.net/api/vector/stats"
```

## Monitoring Vector Quality

### API Endpoints

```bash
# Vector database statistics
GET /api/vector/stats
{
  "coverage": {
    "total_documents_in_db": 74,
    "total_vectors": 68,
    "coverage_percentage": 91.9,
    "estimated_missing": 6
  },
  "status": "healthy"
}

# Search quality test
GET /api/vector/search-quality
{
  "overall_quality": {
    "average_relevance_score": 0.847,
    "quality_rating": "excellent"
  }
}
```

### Coverage Metrics

| Coverage | Status | Action |
|----------|--------|---------|
| 0% | 🔴 Critical | Rebuild immediately |
| < 50% | 🟡 Poor | Rebuild recommended |
| 50-89% | 🟠 Partial | Monitor, consider rebuild |
| 90%+ | 🟢 Good | Healthy, monitor regularly |

## What Gets Vectorized

### Innovations
```python
# Combined text for embedding
text = f"""
Title: {title}
Description: {description}
Type: {innovation_type}
Country: {country}
Organizations: {org_names}
Tags: {tags}
Publications: {related_pub_titles}
"""
```

### Publications
```python
# Combined text for embedding  
text = f"""
Title: {title}
Abstract: {abstract}
Authors: {authors}
Type: {publication_type}
Keywords: {keywords}
African Entities: {african_entities}
"""
```

## Embedding Model Details

- **Model**: `multilingual-e5-large`
- **Dimensions**: 1024
- **Languages**: Multilingual (excellent for African content)
- **Context**: 8192 tokens max
- **Provider**: Pinecone Inference API

## Troubleshooting

### Common Issues

1. **No search results**
   ```bash
   python scripts/check_vectors.py
   # If vectors = 0, run rebuild
   ```

2. **Poor search quality**
   ```bash
   # Check average scores
   curl "https://api.taifa-fiala.net/api/vector/search-quality"
   # If avg_score < 0.6, consider rebuild
   ```

3. **Pinecone errors**
   - Check `PINECONE_API_KEY` in environment
   - Verify `PINECONE_INDEX` name
   - Ensure index exists and is active

4. **Memory issues during rebuild**
   - Script processes in batches (50 documents)
   - Has exponential backoff for rate limits
   - Saves progress regularly

### Recovery Steps

```bash
# 1. Check current status
python scripts/check_vectors.py

# 2. If broken, rebuild
python scripts/rebuild_vectors.py

# 3. Verify quality
python scripts/check_vectors.py --quick-test

# 4. Monitor via API
curl "https://api.taifa-fiala.net/api/vector/stats"
```

## Integration with Main API

⚠️ **Current Issue**: Main `/api/innovations` endpoint doesn't use vector search

### Fix Needed
The main innovations endpoint should:
1. Use vector search when `query` parameter provided
2. Return relevance scores
3. Combine vector + traditional filtering

### Temporary Workaround
Use the vector search endpoint directly:
```bash
# Vector search endpoint
GET /api/search?query=machine+learning+agriculture
```

## Performance Expectations

- **Rebuild Time**: 5-15 minutes for ~100 documents
- **Search Latency**: < 200ms for most queries
- **Batch Size**: 50 documents per batch
- **Rate Limits**: Built-in exponential backoff

## Best Practices

1. **Regular Monitoring**: Check coverage weekly
2. **Incremental Updates**: Add new documents to vectors immediately
3. **Quality Testing**: Run search quality tests monthly
4. **Backup**: Keep rebuild statistics for troubleshooting

## Next Steps

1. **Fix Main API**: Integrate vector search into `/api/innovations`
2. **Add UX Indicators**: Show search quality to users
3. **Incremental Updates**: Auto-vectorize new content
4. **Monitoring Dashboard**: Real-time vector health metrics