'use client'

import { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, FileText, Users, Globe, Lightbulb, Zap, RefreshCw, Activity } from 'lucide-react'
import { Section3Text } from '@/components/ui/adaptive-text'
import EnrichmentResultsTable from '@/components/Dashboard/EnrichmentResultsTable'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8030'

interface AnalyticsData {
  monthly_innovations: Array<{
    month: string
    innovations: number
    publications: number
    enrichments: number
  }>
  domain_distribution: Array<{
    domain: string
    count: number
    percentage: number
  }>
  country_distribution: Array<{
    country: string
    count: number
    innovations: number
    publications: number
  }>
  verification_pipeline: Array<{
    status: string
    count: number
    percentage: number
  }>
  recent_activity: Array<{
    id: string
    type: 'innovation' | 'publication' | 'enrichment'
    title: string
    timestamp: string
    country?: string
  }>
  enrichment_stats: {
    total_reports: number
    reports_this_week: number
    avg_confidence: number
  }
}

const COLORS = [
  '#3B82F6', // blue
  '#10B981', // emerald
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // violet
  '#06B6D4', // cyan
  '#F97316', // orange
  '#84CC16', // lime
]

export default function RealTimeAnalytics() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  useEffect(() => {
    fetchAnalyticsData()
    // Refresh every 2 minutes
    const interval = setInterval(() => {
      fetchAnalyticsData()
      setLastUpdated(new Date())
    }, 2 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const fetchAnalyticsData = async () => {
    try {
      setError(null)
      
      // Try to fetch real data from multiple endpoints
      const [innovationsResponse, enrichmentResponse] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/api/analytics/innovations`),
        fetch(`${API_BASE_URL}/api/etl/results/enrichment`)
      ])

      // Use mock data for now while building the interface
      const mockData: AnalyticsData = {
        monthly_innovations: [
          { month: 'Jan 2024', innovations: 45, publications: 32, enrichments: 8 },
          { month: 'Feb 2024', innovations: 52, publications: 38, enrichments: 12 },
          { month: 'Mar 2024', innovations: 67, publications: 45, enrichments: 15 },
          { month: 'Apr 2024', innovations: 58, publications: 41, enrichments: 18 },
          { month: 'May 2024', innovations: 71, publications: 52, enrichments: 22 },
          { month: 'Jun 2024', innovations: 83, publications: 61, enrichments: 28 },
          { month: 'Jul 2024', innovations: 92, publications: 68, enrichments: 34 },
          { month: 'Aug 2024', innovations: 89, publications: 72, enrichments: 41 }
        ],
        domain_distribution: [
          { domain: 'Healthcare AI', count: 89, percentage: 23.5 },
          { domain: 'AgriTech', count: 72, percentage: 19.0 },
          { domain: 'FinTech', count: 65, percentage: 17.2 },
          { domain: 'EdTech', count: 54, percentage: 14.3 },
          { domain: 'Climate Tech', count: 43, percentage: 11.4 },
          { domain: 'Other', count: 55, percentage: 14.6 }
        ],
        country_distribution: [
          { country: 'South Africa', count: 124, innovations: 89, publications: 35 },
          { country: 'Kenya', count: 98, innovations: 67, publications: 31 },
          { country: 'Nigeria', count: 87, innovations: 62, publications: 25 },
          { country: 'Egypt', count: 76, innovations: 54, publications: 22 },
          { country: 'Ghana', count: 45, innovations: 32, publications: 13 },
          { country: 'Tunisia', count: 38, innovations: 28, publications: 10 },
          { country: 'Rwanda', count: 32, innovations: 21, publications: 11 },
          { country: 'Other', count: 78, innovations: 56, publications: 22 }
        ],
        verification_pipeline: [
          { status: 'Verified', count: 234, percentage: 62.1 },
          { status: 'Under Review', count: 89, percentage: 23.6 },
          { status: 'Community Validated', count: 54, percentage: 14.3 }
        ],
        recent_activity: [
          { id: '1', type: 'innovation', title: 'AI-Powered Medical Diagnosis Platform', timestamp: '2024-08-05T10:30:00Z', country: 'Nigeria' },
          { id: '2', type: 'enrichment', title: 'Weekly Innovation Landscape Report', timestamp: '2024-08-05T09:15:00Z' },
          { id: '3', type: 'publication', title: 'Machine Learning for Crop Yield Prediction', timestamp: '2024-08-05T08:45:00Z', country: 'Kenya' },
          { id: '4', type: 'innovation', title: 'Blockchain-Based Supply Chain Tracker', timestamp: '2024-08-05T07:20:00Z', country: 'Ghana' },
          { id: '5', type: 'enrichment', title: 'Funding Landscape Analysis', timestamp: '2024-08-05T06:10:00Z' }
        ],
        enrichment_stats: {
          total_reports: 156,
          reports_this_week: 12,
          avg_confidence: 0.87
        }
      }
      
      setData(mockData)
      
    } catch (err) {
      console.error('Error fetching analytics data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'innovation':
        return <Lightbulb className="h-4 w-4 text-yellow-600" />
      case 'publication':
        return <FileText className="h-4 w-4 text-blue-600" />
      case 'enrichment':
        return <Zap className="h-4 w-4 text-purple-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-600" />
    }
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
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-card rounded-lg h-32 border" style={{ backgroundColor: "var(--color-muted)" }}></div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-card rounded-lg h-80 border" style={{ backgroundColor: "var(--color-muted)" }}></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
        <p style={{ color: "var(--color-destructive)" }}>Failed to load analytics: {error}</p>
        <button
          onClick={fetchAnalyticsData}
          className="mt-4 px-4 py-2 rounded-lg transition-colors"
          style={{
            backgroundColor: "var(--color-primary)",
            color: "var(--color-primary-foreground)",
          }}
        >
          Retry
        </button>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-8">
      {/* Header with Last Updated */}
      <div className="flex items-center justify-between">
        <div>
          <Section3Text as="h2" className="text-2xl font-bold">
            Real-time Innovation Analytics
          </Section3Text>
          <p style={{ color: "var(--color-text-section-subheading)" }} className="text-sm opacity-70">
            Live insights into African AI innovation ecosystem
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm" style={{ color: "var(--color-text-section-subheading)" }}>
          <RefreshCw className="h-4 w-4" />
          <span>Updated: {lastUpdated.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {data.monthly_innovations[data.monthly_innovations.length - 1]?.innovations || 0}
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                New This Month
              </p>
            </div>
            <Lightbulb className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>

        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {data.enrichment_stats.reports_this_week}
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                AI Reports This Week
              </p>
            </div>
            <Zap className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>

        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {(data.enrichment_stats.avg_confidence * 100).toFixed(0)}%
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                Avg Confidence
              </p>
            </div>
            <TrendingUp className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>

        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {data.country_distribution.length - 1}
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                Active Countries
              </p>
            </div>
            <Globe className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>
      </div>

      {/* Enrichment Results Section */}
      <div className="mb-8">
        <EnrichmentResultsTable />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Monthly Trends */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Monthly Innovation Trends
            </h3>
            <TrendingUp className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.monthly_innovations}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.3} />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" fontSize={12} />
              <YAxis stroke="var(--color-muted-foreground)" fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-card-foreground)'
                }}
              />
              <Line type="monotone" dataKey="innovations" stroke="#3B82F6" strokeWidth={3} name="Innovations" />
              <Line type="monotone" dataKey="publications" stroke="#10B981" strokeWidth={3} name="Publications" />
              <Line type="monotone" dataKey="enrichments" stroke="#8B5CF6" strokeWidth={3} name="AI Reports" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Domain Distribution */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Innovation Domains
            </h3>
            <FileText className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.domain_distribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ domain, percentage }) => `${domain}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {data.domain_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-card-foreground)'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Geographic Distribution */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Geographic Distribution
            </h3>
            <Globe className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.country_distribution.slice(0, 6)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.3} />
              <XAxis type="number" stroke="var(--color-muted-foreground)" fontSize={12} />
              <YAxis 
                dataKey="country" 
                type="category" 
                stroke="var(--color-muted-foreground)" 
                fontSize={12}
                width={80}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-card-foreground)'
                }}
              />
              <Bar dataKey="innovations" fill="#8B5CF6" name="Innovations" />
              <Bar dataKey="publications" fill="#06B6D4" name="Publications" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Activity */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Recent Activity
            </h3>
            <Activity className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <div className="space-y-4 max-h-[280px] overflow-y-auto">
            {data.recent_activity.map((item) => (
              <div key={item.id} className="flex items-start space-x-3">
                <div className="flex-shrink-0 p-2 rounded-full" style={{ backgroundColor: "var(--color-muted)" }}>
                  {getActivityIcon(item.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium" style={{ color: "var(--color-card-foreground)" }}>
                    {item.title}
                  </p>
                  <div className="flex items-center space-x-2 text-xs" style={{ color: "var(--color-muted-foreground)" }}>
                    <span>{formatTimestamp(item.timestamp)}</span>
                    {item.country && (
                      <>
                        <span>•</span>
                        <span>{item.country}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  )
}