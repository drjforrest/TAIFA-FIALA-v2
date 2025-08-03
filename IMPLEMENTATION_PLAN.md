# TAIFA-FIALA Dashboard & Explore Data Implementation Guide

## Overview
This guide implements the enhanced Dashboard and Explore Data pages that connect to your FastAPI backend for real-time monitoring of the African AI innovation discovery pipeline.

## Architecture Summary

### Dashboard Purpose
- **Monitor** the systematic documentation pipeline (ETL status, data quality)
- **Visualise** key metrics (innovations discovered, verification pipeline, geographic coverage)
- **Control** manual ETL triggers for academic, news, and Serper discovery pipelines

### Explore Data Purpose  
- **Search** and filter documented AI innovations across Africa
- **Interactive cards** displaying project details, funding, verification status
- **Public interface** for researchers, funders, and innovators to discover projects

---

## File Implementation Order

### 1. Update the Dashboard Hook
**File**: `frontend/src/hooks/useDashboard.ts`
**Artifact**: `enhanced_dashboard_hook`

Replace the existing file with the enhanced version that:
- Connects to FastAPI `/api/stats` and `/api/etl/status` endpoints
- Provides real-time ETL monitoring with `useETLMonitoring()` hook
- Includes manual pipeline trigger functions
- Updates every 30 seconds for live monitoring

### 2. Create Missing Dashboard Components

#### PublicationCharts Component
**File**: `frontend/src/components/Dashboard/PublicationCharts.tsx` 
**Artifact**: `publication_charts_component`

Creates visualisations for:
- Monthly discovery trends (publications vs innovations)
- Domain distribution (HealthTech, AgriTech, etc.)
- Geographic distribution across African countries
- Verification pipeline status
- Trending research keywords

#### RecentActivity Component  
**File**: `frontend/src/components/Dashboard/RecentActivity.tsx`
**Artifact**: `recent_activity_component`

Displays live feed of:
- Recently discovered innovations
- New research publications processed
- Community submissions and verification updates
- Real-time timestamps and metadata

### 3. Enhance Dashboard Stats
**File**: `frontend/src/components/Dashboard/DashboardStats.tsx`
**Artifact**: `enhanced_dashboard_stats`

Replace existing component with enhanced version that:
- Shows core metrics from backend API
- Displays ETL pipeline status with indicators
- Provides manual trigger buttons for each pipeline
- Real-time processing activity monitoring

### 4. Replace Explore Data Page
**File**: `frontend/src/app/innovations/page.tsx`
**Artifact**: `enhanced_explore_data`

Replace the mock data version with fully functional:
- Real-time search with debounced queries
- Advanced filtering (type, country, verification status, funding)  
- Responsive card layout with verification badges
- Load more pagination
- Connect to `/api/innovations` backend endpoint

---

## Backend API Requirements

Ensure these FastAPI endpoints are implemented and responding:

### Core Statistics
```
GET /api/stats
Returns: {
  total_publications: number,
  total_innovations: number, 
  total_organizations: number,
  verified_individuals: number,
  african_countries_covered: number,
  unique_keywords: number,
  avg_african_relevance: number,
  avg_ai_relevance: number,
  last_updated: string
}
```

### ETL Pipeline Monitoring
```
GET /api/etl/status
Returns: {
  academic_pipeline_active: boolean,
  news_pipeline_active: boolean,
  serper_pipeline_active: boolean,
  last_academic_run: string,
  last_news_run: string, 
  last_serper_run: string,
  total_processed_today: number,
  errors_today: number
}

GET /api/etl/health
Returns: {
  status: "healthy" | "degraded" | "unhealthy",
  recent_logs: Array<LogEntry>,
  performance_metrics: object
}
```

### Innovation Search
```
GET /api/innovations?query=&innovation_type=&country=&verification_status=&limit=&offset=
Returns: {
  innovations: Array<Innovation>,
  total: number,
  metadata: {
    innovation_types: string[],
    countries: string[],
    organizations: string[]
  }
}
```

### Pipeline Triggers
```
POST /api/etl/academic
POST /api/etl/news  
POST /api/etl/serper-search
Body: { query?: string }
```

### Analytics (for charts)
```
GET /api/analytics/publications
Returns: {
  monthly_publications: Array<MonthlyData>,
  domain_distribution: Array<DomainData>,
  country_distribution: Array<CountryData>,
  verification_pipeline: Array<StatusData>,
  trending_keywords: Array<KeywordData>
}
```

---

## Configuration

### Environment Variables
Ensure `NEXT_PUBLIC_API_URL` is set in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## Testing Checklist

### Dashboard Functionality
- [ ] Core metrics load from backend API
- [ ] ETL pipeline status indicators show correctly  
- [ ] Manual trigger buttons work (academic, news, serper)
- [ ] Charts render with real data
- [ ] Recent activity feed updates automatically
- [ ] Real-time refresh (30-second intervals) functioning
- [ ] Error handling displays appropriately

### Explore Data Functionality  
- [ ] Search queries connect to backend
- [ ] Filters work (innovation type, country, verification status)
- [ ] Innovation cards display with correct data
- [ ] Verification status badges show properly
- [ ] Load more pagination works
- [ ] Empty states handle gracefully
- [ ] Responsive design on mobile/tablet

### Error Handling
- [ ] API connection failures show user-friendly messages
- [ ] Graceful fallbacks when backend is unavailable
- [ ] Loading states prevent UI confusion
- [ ] Network errors don't crash the application

---

## Success Metrics

When successfully implemented, you'll have:

1. **Real-time monitoring** of your innovation discovery pipeline
2. **Public-facing search** interface for African AI innovations
3. **Stakeholder alignment** - funders can showcase impact, innovators gain visibility
4. **Research foundation** - systematic documentation of African AI excellence
5. **Scalable platform** ready for the 2-3 year validation study expansion

This transforms TAIFA-FIALA from a funding tracker to the innovation archive described in your strategic vision - where the focus shifts from "who promised what" to "who's building what" with rigorous documentation and community engagement.