'use client'

import { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, FileText, Users, Globe } from 'lucide-react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface PublicationData {
  monthly_publications: Array<{
    month: string
    publications: number
    innovations: number
  }>
  domain_distribution: Array<{
    domain: string
    count: number
    percentage: number
  }>
  country_distribution: Array<{
    country: string
    count: number
    publications: number
    innovations: number
  }>
  verification_pipeline: Array<{
    status: string
    count: number
    percentage: number
  }>
  trending_keywords: Array<{
    keyword: string
    count: number
    growth: number
  }>
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

export default function PublicationCharts() {
  const [data, setData] = useState<PublicationData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPublicationData()
    // Refresh every 5 minutes
    const interval = setInterval(fetchPublicationData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const fetchPublicationData = async () => {
    try {
      setError(null)
      
      const response = await fetch(`${API_BASE_URL}/api/analytics/publications`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch publication data: ${response.status}`)
      }

      const responseData = await response.json()
      setData(responseData)
      
    } catch (err) {
      console.error('Error fetching publication data:', err)
      
      // Fallback to mock data for development
      const mockData: PublicationData = {
        monthly_publications: [
          { month: 'Jan 2024', publications: 45, innovations: 12 },
          { month: 'Feb 2024', publications: 52, innovations: 18 },
          { month: 'Mar 2024', publications: 67, innovations: 23 },
          { month: 'Apr 2024', publications: 58, innovations: 19 },
          { month: 'May 2024', publications: 71, innovations: 28 },
          { month: 'Jun 2024', publications: 83, innovations: 34 },
          { month: 'Jul 2024', publications: 92, innovations: 41 },
          { month: 'Aug 2024', publications: 89, innovations: 38 }
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
          { country: 'South Africa', count: 124, publications: 89, innovations: 35 },
          { country: 'Kenya', count: 98, publications: 67, innovations: 31 },
          { country: 'Nigeria', count: 87, publications: 62, innovations: 25 },
          { country: 'Egypt', count: 76, publications: 54, innovations: 22 },
          { country: 'Ghana', count: 45, publications: 32, innovations: 13 },
          { country: 'Tunisia', count: 38, publications: 28, innovations: 10 },
          { country: 'Rwanda', count: 32, publications: 21, innovations: 11 },
          { country: 'Other', count: 78, publications: 56, innovations: 22 }
        ],
        verification_pipeline: [
          { status: 'Verified', count: 234, percentage: 62.1 },
          { status: 'Under Review', count: 89, percentage: 23.6 },
          { status: 'Community Validated', count: 54, percentage: 14.3 }
        ],
        trending_keywords: [
          { keyword: 'Machine Learning', count: 156, growth: 23.4 },
          { keyword: 'Computer Vision', count: 98, growth: 18.7 },
          { keyword: 'Natural Language Processing', count: 87, growth: 15.2 },
          { keyword: 'Deep Learning', count: 76, growth: 12.8 },
          { keyword: 'Predictive Analytics', count: 65, growth: 28.3 }
        ]
      }
      setData(mockData)
      setError(err instanceof Error ? `Using mock data: ${err.message}` : 'Using mock data due to API error')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Research Analytics</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-80"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Research Analytics</h2>
        {error && (
          <div className="text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-2 py-1 rounded">
            {error}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Publication Trends */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Monthly Discovery Trends
            </h3>
            <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data?.monthly_publications}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="month" 
                stroke="#6B7280"
                fontSize={12}
              />
              <YAxis stroke="#6B7280" fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="publications" 
                stroke="#3B82F6" 
                strokeWidth={3}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                name="Publications"
              />
              <Line 
                type="monotone" 
                dataKey="innovations" 
                stroke="#10B981" 
                strokeWidth={3}
                dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                name="Innovations"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Domain Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Innovation Domains
            </h3>
            <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data?.domain_distribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ domain, percentage }) => `${domain}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {data?.domain_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Geographic Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Geographic Distribution
            </h3>
            <Globe className="h-5 w-5 text-purple-600 dark:text-purple-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data?.country_distribution} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis type="number" stroke="#6B7280" fontSize={12} />
              <YAxis 
                dataKey="country" 
                type="category" 
                stroke="#6B7280" 
                fontSize={12}
                width={80}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
              <Bar dataKey="innovations" fill="#8B5CF6" name="Innovations" />
              <Bar dataKey="publications" fill="#06B6D4" name="Publications" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Verification Pipeline Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Verification Pipeline
            </h3>
            <Users className="h-5 w-5 text-orange-600 dark:text-orange-400" />
          </div>
          <div className="space-y-4">
            {data?.verification_pipeline.map((item, index) => (
              <div key={item.status} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {item.status}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {item.count.toLocaleString()}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-500">
                    ({item.percentage}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="flex h-2 rounded-full overflow-hidden">
                {data?.verification_pipeline.map((item, index) => (
                  <div
                    key={item.status}
                    className="h-full"
                    style={{
                      width: `${item.percentage}%`,
                      backgroundColor: COLORS[index % COLORS.length]
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trending Keywords */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Trending Research Keywords
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {data?.trending_keywords.map((keyword, index) => (
            <div key={keyword.keyword} className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {keyword.count}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                {keyword.keyword}
              </div>
              <div className={`text-xs font-medium ${
                keyword.growth > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              }`}>
                {keyword.growth > 0 ? '+' : ''}{keyword.growth}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}