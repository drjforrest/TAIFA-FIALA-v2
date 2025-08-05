'use client'

import { useState, useEffect } from 'react'
import { Section3Text } from '@/components/ui/adaptive-text'
import { TrendingUp, FileText, Lightbulb, Zap, Clock, CheckCircle, AlertCircle, Globe, Cpu } from 'lucide-react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface EnrichmentResult {
  id: string
  title: string
  type: 'innovation' | 'publication'
  original_date: string
  enrichment_date: string
  enrichment_confidence: number
  ai_relevance_score: number
  african_relevance_score: number
  enrichment_summary: string
  domain: string
  country?: string
  status: 'completed' | 'processing' | 'failed'
  processing_time_ms?: number
}

export default function EnrichmentResultsTable() {
  const [results, setResults] = useState<EnrichmentResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchEnrichmentResults()
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchEnrichmentResults, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchEnrichmentResults = async () => {
    try {
      setError(null)
      
      // Try to fetch real data from the enrichment API
      let response
      try {
        response = await fetch(`${API_BASE_URL}/api/etl/results/enrichment?limit=50`)
      } catch (corsError) {
        console.log('CORS error, using mock data...', corsError)
        // Use mock data for development
        setResults(mockEnrichmentResults)
        setLoading(false)
        return
      }

      if (response && response.ok) {
        const data = await response.json()
        // Transform API data to our interface if needed
        setResults(data.results || mockEnrichmentResults)
      } else {
        // Fallback to mock data
        setResults(mockEnrichmentResults)
      }
      
    } catch (err) {
      console.error('Error fetching enrichment results:', err)
      setError(err instanceof Error ? err.message : 'Failed to load enrichment results')
      // Use mock data as fallback
      setResults(mockEnrichmentResults)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
      case 'processing':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
      case 'failed':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20'
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />
      case 'processing':
        return <Clock className="h-4 w-4" />
      case 'failed':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
    if (score >= 0.6) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
    return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20'
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-24"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Section3Text as="h3" className="text-xl font-semibold">
            Recent AI Enrichment Results
          </Section3Text>
          <p style={{ color: "var(--color-card-foreground)" }} className="text-sm mt-1 opacity-70">
            Latest entries processed through AI intelligence pipelines
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm" style={{ color: "var(--color-muted-foreground)" }}>
          <Zap className="h-4 w-4" />
          <span>Auto-refreshing</span>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">Error loading enrichment results: {error}</p>
        </div>
      )}

      {/* Results Table */}
      <div className="overflow-x-auto rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
        {results.length === 0 && !loading ? (
          <div className="text-center py-12">
            <Zap className="h-12 w-12 mx-auto mb-4" style={{ color: "var(--color-muted-foreground)" }} />
            <p style={{ color: "var(--color-muted-foreground)" }}>
              No enrichment results available. Run the AI Enrichment pipeline to see processed data.
            </p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b" style={{ borderColor: "var(--color-border)" }}>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  Type & Status
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  Title
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  African Score
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  AI Score
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  Confidence
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  Domain
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  Country
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                  Processed
                </th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr 
                  key={result.id} 
                  className="border-b hover:bg-opacity-50 transition-colors"
                  style={{ 
                    borderColor: "var(--color-border)",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--color-muted)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }}
                >
                  {/* Type & Status */}
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div className="flex items-center">
                        {result.type === 'innovation' ? (
                          <Lightbulb className="h-4 w-4 text-yellow-600" />
                        ) : (
                          <FileText className="h-4 w-4 text-blue-600" />
                        )}
                        <span className="ml-1 text-xs font-medium capitalize" style={{ color: "var(--color-muted-foreground)" }}>
                          {result.type}
                        </span>
                      </div>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                        {getStatusIcon(result.status)}
                        <span className="ml-1 capitalize">{result.status}</span>
                      </span>
                    </div>
                  </td>

                  {/* Title */}
                  <td className="py-3 px-4 max-w-xs">
                    <div className="truncate">
                      <span className="text-sm font-medium" style={{ color: "var(--color-card-foreground)" }} title={result.title}>
                        {result.title}
                      </span>
                      <p className="text-xs mt-1 text-gray-500 truncate" title={result.enrichment_summary}>
                        {result.enrichment_summary}
                      </p>
                    </div>
                  </td>

                  {/* African Score */}
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <Globe className="w-3 h-3 mr-1 text-gray-400" />
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(result.african_relevance_score)}`}>
                        {(result.african_relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>

                  {/* AI Score */}
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <Cpu className="w-3 h-3 mr-1 text-gray-400" />
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(result.ai_relevance_score)}`}>
                        {(result.ai_relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>

                  {/* Confidence */}
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <TrendingUp className="w-3 h-3 mr-1 text-gray-400" />
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(result.enrichment_confidence)}`}>
                        {(result.enrichment_confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>

                  {/* Domain */}
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                      {result.domain}
                    </span>
                  </td>

                  {/* Country */}
                  <td className="py-3 px-4">
                    <span className="text-sm" style={{ color: "var(--color-card-foreground)" }}>
                      {result.country || '—'}
                    </span>
                  </td>

                  {/* Processed Time */}
                  <td className="py-3 px-4">
                    <div className="text-xs" style={{ color: "var(--color-muted-foreground)" }}>
                      <div>{formatTimestamp(result.enrichment_date)}</div>
                      {result.processing_time_ms && (
                        <div className="flex items-center mt-1">
                          <Zap className="w-3 h-3 mr-1" />
                          {result.processing_time_ms}ms
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

// Mock data for development/fallback
const mockEnrichmentResults: EnrichmentResult[] = [
  {
    id: '1',
    title: 'AI-Powered Medical Diagnosis Platform for Rural Clinics',
    type: 'innovation',
    original_date: '2024-08-04T14:30:00Z',
    enrichment_date: '2024-08-05T09:15:00Z',
    enrichment_confidence: 0.92,
    ai_relevance_score: 0.89,
    african_relevance_score: 0.95,
    enrichment_summary: 'Advanced diagnostic AI system specifically designed for resource-constrained healthcare environments across Sub-Saharan Africa. Leverages edge computing and local medical expertise.',
    domain: 'HealthTech',
    country: 'Nigeria',
    status: 'completed',
    processing_time_ms: 1450
  },
  {
    id: '2',
    title: 'Machine Learning for Crop Yield Prediction in Smallholder Farms',
    type: 'publication',
    original_date: '2024-08-04T11:20:00Z',
    enrichment_date: '2024-08-05T08:45:00Z',
    enrichment_confidence: 0.88,
    ai_relevance_score: 0.91,
    african_relevance_score: 0.87,
    enrichment_summary: 'Research paper demonstrating 23% improvement in yield prediction accuracy using satellite imagery and local weather data. Field tested across 500+ farms in East Africa.',
    domain: 'AgriTech',
    country: 'Kenya',
    status: 'completed',
    processing_time_ms: 2100
  },
  {
    id: '3',
    title: 'Blockchain-Based Supply Chain Tracker for Cocoa Farmers',
    type: 'innovation',
    original_date: '2024-08-04T16:45:00Z',
    enrichment_date: '2024-08-05T07:20:00Z',
    enrichment_confidence: 0.85,
    ai_relevance_score: 0.76,
    african_relevance_score: 0.93,
    enrichment_summary: 'Transparent supply chain solution enabling direct farmer-to-consumer traceability. Integrates mobile payments and quality verification through IoT sensors.',
    domain: 'AgriTech',
    country: 'Ghana',
    status: 'completed',
    processing_time_ms: 1800
  },
  {
    id: '4',
    title: 'Natural Language Processing for African Languages',
    type: 'publication',
    original_date: '2024-08-04T13:15:00Z',
    enrichment_date: '2024-08-05T06:55:00Z',
    enrichment_confidence: 0.94,
    ai_relevance_score: 0.96,
    african_relevance_score: 0.98,
    enrichment_summary: 'Comprehensive study on developing NLP models for Swahili, Hausa, and Amharic. Includes novel techniques for low-resource language processing and cultural context preservation.',
    domain: 'AI Research',
    country: 'South Africa',
    status: 'completed',
    processing_time_ms: 3200
  },
  {
    id: '5',
    title: 'Mobile Banking Security Enhancement through Biometric Authentication',
    type: 'innovation',
    original_date: '2024-08-04T09:30:00Z',
    enrichment_date: '2024-08-05T06:10:00Z',
    enrichment_confidence: 0.79,
    ai_relevance_score: 0.82,
    african_relevance_score: 0.91,
    enrichment_summary: 'Advanced security platform combining fingerprint and voice recognition for mobile banking in areas with limited internet connectivity. Deployed across 12 African countries.',
    domain: 'FinTech',
    country: 'Rwanda',
    status: 'processing',
    processing_time_ms: 950
  },
  {
    id: '6',
    title: 'Solar Panel Efficiency Optimization using Computer Vision',
    type: 'innovation',
    original_date: '2024-08-04T08:00:00Z',
    enrichment_date: '2024-08-05T05:30:00Z',
    enrichment_confidence: 0.87,
    ai_relevance_score: 0.84,
    african_relevance_score: 0.89,
    enrichment_summary: 'AI system for automatically detecting and diagnosing solar panel defects using drone imagery. Reduces maintenance costs by 40% for off-grid installations.',
    domain: 'ClimateReach',
    country: 'Morocco',
    status: 'completed',
    processing_time_ms: 2750
  }
]