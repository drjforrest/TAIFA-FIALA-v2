'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area, ScatterChart, Scatter, Cell } from 'recharts'
import { TrendingUp, Cpu, Globe, Zap, RefreshCw, Award, Target, Layers, Activity } from 'lucide-react'
import { Section3Text } from '@/components/ui/adaptive-text'

// Import the smart API detection
const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname.includes('taifa-fiala') || hostname.includes('vercel.app') || hostname.includes('netlify.app')) {
      return 'https://api.taifa-fiala.net';
    }
  }
  return 'http://localhost:8030';
};

const API_BASE_URL = getApiBaseUrl()

interface TechnologyTrend {
  technology: string
  category: string
  adoption_rate: number
  growth_rate: number
  maturity_stage: 'emerging' | 'growing' | 'mature' | 'declining'
  geographic_spread: number
  total_implementations: number
  monthly_data: Array<{
    month: string
    implementations: number
    publications: number
    adoption_score: number
  }>
}

interface GeographicInnovation {
  country: string
  total_innovations: number
  population: number
  innovations_per_capita: number
  dominant_technologies: string[]
  innovation_density_score: number
  yearly_growth: number
}

interface TechnologyAdoptionAnalytics {
  trending_technologies: TechnologyTrend[]
  declining_technologies: TechnologyTrend[]
  geographic_innovation_density: GeographicInnovation[]
  technology_lifecycle: Array<{
    quarter: string
    emerging_count: number
    growing_count: number
    mature_count: number
    declining_count: number
  }>
  cross_domain_adoption: Array<{
    technology: string
    healthcare: number
    agriculture: number
    finance: number
    education: number
    climate: number
  }>
  innovation_hotspots: Array<{
    region: string
    city: string
    country: string
    innovation_count: number
    density_per_million: number
    key_technologies: string[]
    ecosystem_strength: number
  }>
}

const TECHNOLOGY_COLORS: Record<string, string> = {
  'machine_learning': '#3B82F6',
  'deep_learning': '#8B5CF6',
  'nlp': '#10B981',
  'computer_vision': '#F59E0B',
  'blockchain': '#EF4444',
  'iot': '#06B6D4',
  'robotics': '#F97316',
  'quantum_computing': '#84CC16'
}

const MATURITY_COLORS: Record<string, string> = {
  'emerging': '#10B981',
  'growing': '#F59E0B',
  'mature': '#3B82F6',
  'declining': '#EF4444'
}

const COUNTRY_COLORS: Record<string, string> = {
  'South Africa': '#3B82F6',
  'Nigeria': '#F59E0B',
  'Kenya': '#10B981',
  'Egypt': '#EF4444',
  'Ghana': '#8B5CF6',
  'Rwanda': '#06B6D4',
  'Tunisia': '#F97316',
  'Morocco': '#84CC16'
}

export default function TechnologyAdoptionCurves() {
  const [data, setData] = useState<TechnologyAdoptionAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [selectedTechnology, setSelectedTechnology] = useState<string | null>(null)

  useEffect(() => {
    fetchTechnologyData()
  }, [])

  const fetchTechnologyData = async (isRefresh = false) => {
    try {
      setError(null)
      if (isRefresh) setRefreshing(true)
      
      // Try to fetch real data from intelligence endpoints
      const publicationIntelligenceResponse = await fetch(`${API_BASE_URL}/api/data-intelligence/publications/intelligence-report`)
      const citationAnalyticsResponse = await fetch(`${API_BASE_URL}/api/data-intelligence/citations/network-analytics`)

      // For now, use comprehensive mock data
      const mockData: TechnologyAdoptionAnalytics = {
        trending_technologies: [
          {
            technology: 'Large Language Models',
            category: 'nlp',
            adoption_rate: 78.4,
            growth_rate: 145.2,
            maturity_stage: 'growing',
            geographic_spread: 12,
            total_implementations: 89,
            monthly_data: [
              { month: 'Jan 2024', implementations: 12, publications: 8, adoption_score: 34.2 },
              { month: 'Feb 2024', implementations: 18, publications: 12, adoption_score: 42.8 },
              { month: 'Mar 2024', implementations: 25, publications: 16, adoption_score: 51.3 },
              { month: 'Apr 2024', implementations: 31, publications: 19, adoption_score: 58.7 },
              { month: 'May 2024', implementations: 38, publications: 23, adoption_score: 65.1 },
              { month: 'Jun 2024', implementations: 47, publications: 28, adoption_score: 71.4 },
              { month: 'Jul 2024', implementations: 58, publications: 34, adoption_score: 75.9 },
              { month: 'Aug 2024', implementations: 67, publications: 41, adoption_score: 78.4 }
            ]
          },
          {
            technology: 'Computer Vision',
            category: 'computer_vision',
            adoption_rate: 71.8,
            growth_rate: 89.3,
            maturity_stage: 'mature',
            geographic_spread: 15,
            total_implementations: 134,
            monthly_data: [
              { month: 'Jan 2024', implementations: 89, publications: 23, adoption_score: 61.2 },
              { month: 'Feb 2024', implementations: 95, publications: 26, adoption_score: 63.8 },
              { month: 'Mar 2024', implementations: 102, publications: 28, adoption_score: 65.9 },
              { month: 'Apr 2024', implementations: 108, publications: 31, adoption_score: 67.4 },
              { month: 'May 2024', implementations: 115, publications: 33, adoption_score: 68.9 },
              { month: 'Jun 2024', implementations: 122, publications: 36, adoption_score: 70.1 },
              { month: 'Jul 2024', implementations: 128, publications: 38, adoption_score: 71.2 },
              { month: 'Aug 2024', implementations: 134, publications: 41, adoption_score: 71.8 }
            ]
          },
          {
            technology: 'Edge AI',
            category: 'machine_learning',
            adoption_rate: 45.7,
            growth_rate: 167.8,
            maturity_stage: 'emerging',
            geographic_spread: 8,
            total_implementations: 43,
            monthly_data: [
              { month: 'Jan 2024', implementations: 8, publications: 3, adoption_score: 18.4 },
              { month: 'Feb 2024', implementations: 12, publications: 5, adoption_score: 24.1 },
              { month: 'Mar 2024', implementations: 17, publications: 7, adoption_score: 29.8 },
              { month: 'Apr 2024', implementations: 23, publications: 9, adoption_score: 34.5 },
              { month: 'May 2024', implementations: 28, publications: 12, adoption_score: 38.9 },
              { month: 'Jun 2024', implementations: 34, publications: 14, adoption_score: 42.1 },
              { month: 'Jul 2024', implementations: 39, publications: 16, adoption_score: 44.2 },
              { month: 'Aug 2024', implementations: 43, publications: 18, adoption_score: 45.7 }
            ]
          },
          {
            technology: 'Federated Learning',
            category: 'machine_learning',
            adoption_rate: 38.9,
            growth_rate: 198.4,
            maturity_stage: 'emerging',
            geographic_spread: 6,
            total_implementations: 29,
            monthly_data: [
              { month: 'Jan 2024', implementations: 4, publications: 2, adoption_score: 12.1 },
              { month: 'Feb 2024', implementations: 7, publications: 3, adoption_score: 16.8 },
              { month: 'Mar 2024', implementations: 11, publications: 5, adoption_score: 22.3 },
              { month: 'Apr 2024', implementations: 15, publications: 7, adoption_score: 26.9 },
              { month: 'May 2024', implementations: 19, publications: 9, adoption_score: 30.7 },
              { month: 'Jun 2024', implementations: 23, publications: 11, adoption_score: 34.1 },
              { month: 'Jul 2024', implementations: 26, publications: 13, adoption_score: 36.8 },
              { month: 'Aug 2024', implementations: 29, publications: 15, adoption_score: 38.9 }
            ]
          }
        ],
        declining_technologies: [
          {
            technology: 'Traditional Neural Networks',
            category: 'machine_learning',
            adoption_rate: 34.2,
            growth_rate: -23.7,
            maturity_stage: 'declining',
            geographic_spread: 18,
            total_implementations: 67,
            monthly_data: [
              { month: 'Jan 2024', implementations: 78, publications: 15, adoption_score: 45.3 },
              { month: 'Feb 2024', implementations: 75, publications: 14, adoption_score: 43.8 },
              { month: 'Mar 2024', implementations: 73, publications: 13, adoption_score: 42.1 },
              { month: 'Apr 2024', implementations: 71, publications: 12, adoption_score: 40.7 },
              { month: 'May 2024', implementations: 69, publications: 11, adoption_score: 39.2 },
              { month: 'Jun 2024', implementations: 68, publications: 10, adoption_score: 37.8 },
              { month: 'Jul 2024', implementations: 67, publications: 9, adoption_score: 36.1 },
              { month: 'Aug 2024', implementations: 67, publications: 8, adoption_score: 34.2 }
            ]
          }
        ],
        geographic_innovation_density: [
          {
            country: 'South Africa',
            total_innovations: 156,
            population: 60_000_000,
            innovations_per_capita: 2.60,
            dominant_technologies: ['Computer Vision', 'Machine Learning', 'NLP'],
            innovation_density_score: 8.7,
            yearly_growth: 34.2
          },
          {
            country: 'Nigeria',
            total_innovations: 134,
            population: 220_000_000,
            innovations_per_capita: 0.61,
            dominant_technologies: ['FinTech AI', 'Mobile AI', 'Healthcare AI'],
            innovation_density_score: 7.9,
            yearly_growth: 45.8
          },
          {
            country: 'Kenya',
            total_innovations: 89,
            population: 55_000_000,
            innovations_per_capita: 1.62,
            dominant_technologies: ['AgriTech', 'Mobile Money', 'IoT'],
            innovation_density_score: 7.2,
            yearly_growth: 38.6
          },
          {
            country: 'Egypt',
            total_innovations: 78,
            population: 105_000_000,
            innovations_per_capita: 0.74,
            dominant_technologies: ['Computer Vision', 'Healthcare AI', 'Smart Cities'],
            innovation_density_score: 6.8,
            yearly_growth: 29.4
          },
          {
            country: 'Ghana',
            total_innovations: 56,
            population: 33_000_000,
            innovations_per_capita: 1.70,
            dominant_technologies: ['EdTech', 'AgriTech', 'Healthcare AI'],
            innovation_density_score: 6.1,
            yearly_growth: 42.3
          },
          {
            country: 'Rwanda',
            total_innovations: 43,
            population: 13_000_000,
            innovations_per_capita: 3.31,
            dominant_technologies: ['Digital ID', 'Healthcare AI', 'AgriTech'],
            innovation_density_score: 5.9,
            yearly_growth: 67.2
          }
        ],
        technology_lifecycle: [
          { quarter: 'Q1 2024', emerging_count: 12, growing_count: 23, mature_count: 45, declining_count: 8 },
          { quarter: 'Q2 2024', emerging_count: 18, growing_count: 28, mature_count: 47, declining_count: 12 },
          { quarter: 'Q3 2024', emerging_count: 24, growing_count: 34, mature_count: 49, declining_count: 15 }
        ],
        cross_domain_adoption: [
          { technology: 'Machine Learning', healthcare: 89, agriculture: 67, finance: 78, education: 45, climate: 34 },
          { technology: 'Computer Vision', healthcare: 67, agriculture: 89, finance: 23, education: 34, climate: 45 },
          { technology: 'NLP', healthcare: 34, agriculture: 12, finance: 56, education: 89, climate: 23 },
          { technology: 'IoT', healthcare: 45, agriculture: 78, finance: 34, education: 23, climate: 67 },
          { technology: 'Blockchain', healthcare: 23, agriculture: 34, finance: 89, education: 12, climate: 45 }
        ],
        innovation_hotspots: [
          {
            region: 'Western Cape',
            city: 'Cape Town',
            country: 'South Africa',
            innovation_count: 89,
            density_per_million: 14.2,
            key_technologies: ['Computer Vision', 'FinTech', 'HealthTech'],
            ecosystem_strength: 9.2
          },
          {
            region: 'Lagos State',
            city: 'Lagos',
            country: 'Nigeria',
            innovation_count: 78,
            density_per_million: 5.1,
            key_technologies: ['FinTech', 'Mobile AI', 'E-commerce'],
            ecosystem_strength: 8.7
          },
          {
            region: 'Nairobi',
            city: 'Nairobi',
            country: 'Kenya',
            innovation_count: 67,
            density_per_million: 11.8,
            key_technologies: ['AgriTech', 'Mobile Money', 'logistics'],
            ecosystem_strength: 8.3
          },
          {
            region: 'Cairo',
            city: 'Cairo',
            country: 'Egypt',
            innovation_count: 45,
            density_per_million: 4.3,
            key_technologies: ['Smart Cities', 'Healthcare', 'Education'],
            ecosystem_strength: 7.6
          }
        ]
      }
      
      setData(mockData)
      
    } catch (err) {
      console.error('Error fetching technology data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load technology data')
    } finally {
      setLoading(false)
      if (isRefresh) setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    fetchTechnologyData(true)
  }

  const getMaturityStageColor = (stage: string) => {
    return MATURITY_COLORS[stage] || '#6B7280'
  }

  const getMaturityIcon = (stage: string) => {
    switch (stage) {
      case 'emerging':
        return <Zap className="h-4 w-4 text-green-600" />
      case 'growing':
        return <TrendingUp className="h-4 w-4 text-yellow-600" />
      case 'mature':
        return <Award className="h-4 w-4 text-blue-600" />
      case 'declining':
        return <Activity className="h-4 w-4 text-red-600" />
      default:
        return <Layers className="h-4 w-4 text-gray-600" />
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="bg-card rounded-lg h-80 border" style={{ backgroundColor: "var(--color-muted)" }}></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
        <p style={{ color: "var(--color-destructive)" }}>Failed to load technology data: {error}</p>
        <button
          onClick={() => fetchTechnologyData()}
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Section3Text as="h2" className="text-2xl font-bold">
            Technology Adoption Curves
          </Section3Text>
          <p style={{ color: "var(--color-text-section-subheading)" }} className="text-sm opacity-70">
            AI method popularity over time and geographic innovation density patterns
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors"
          style={{
            backgroundColor: "var(--color-primary)",
            color: "var(--color-primary-foreground)",
          }}
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {data.trending_technologies.length}
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                Trending Technologies
              </p>
            </div>
            <TrendingUp className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>

        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {data.trending_technologies.reduce((acc, tech) => acc + tech.total_implementations, 0)}
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                Total Implementations
              </p>
            </div>
            <Cpu className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>

        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {data.geographic_innovation_density.length}
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                Innovation Hubs
              </p>
            </div>
            <Globe className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>

        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                {(data.trending_technologies.reduce((acc, tech) => acc + tech.growth_rate, 0) / data.trending_technologies.length).toFixed(1)}%
              </p>
              <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                Avg Growth Rate
              </p>
            </div>
            <Target className="h-8 w-8" style={{ color: "var(--color-primary)" }} />
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Technology Adoption Timeline */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Technology Adoption Timeline
            </h3>
            <TrendingUp className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trending_technologies[0]?.monthly_data || []}>
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
              {data.trending_technologies.slice(0, 3).map((tech, index) => (
                <Line 
                  key={tech.technology}
                  type="monotone" 
                  dataKey="adoption_score" 
                  data={tech.monthly_data}
                  stroke={Object.values(TECHNOLOGY_COLORS)[index]}
                  strokeWidth={3}
                  name={tech.technology}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Geographic Innovation Density */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Innovation Density by Country
            </h3>
            <Globe className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.geographic_innovation_density} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.3} />
              <XAxis type="number" stroke="var(--color-muted-foreground)" fontSize={12} />
              <YAxis 
                dataKey="country" 
                type="category" 
                stroke="var(--color-muted-foreground)" 
                fontSize={11}
                width={100}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-card-foreground)'
                }}
              />
              <Bar dataKey="innovations_per_capita" name="Innovations per Capita">
                {data.geographic_innovation_density.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COUNTRY_COLORS[entry.country] || '#8B5CF6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Technology Lifecycle Distribution */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Technology Lifecycle Distribution
            </h3>
            <Layers className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.technology_lifecycle}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.3} />
              <XAxis dataKey="quarter" stroke="var(--color-muted-foreground)" fontSize={12} />
              <YAxis stroke="var(--color-muted-foreground)" fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-card-foreground)'
                }}
              />
              <Area type="monotone" dataKey="emerging_count" stackId="1" stroke="#10B981" fill="#10B981" name="Emerging" />
              <Area type="monotone" dataKey="growing_count" stackId="1" stroke="#F59E0B" fill="#F59E0B" name="Growing" />
              <Area type="monotone" dataKey="mature_count" stackId="1" stroke="#3B82F6" fill="#3B82F6" name="Mature" />
              <Area type="monotone" dataKey="declining_count" stackId="1" stroke="#EF4444" fill="#EF4444" name="Declining" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Cross-Domain Technology Adoption */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Cross-Domain Adoption
            </h3>
            <Target className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.cross_domain_adoption}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.3} />
              <XAxis dataKey="technology" stroke="var(--color-muted-foreground)" fontSize={11} angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="var(--color-muted-foreground)" fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-card-foreground)'
                }}
              />
              <Bar dataKey="healthcare" fill="#3B82F6" name="Healthcare" />
              <Bar dataKey="agriculture" fill="#10B981" name="Agriculture" />
              <Bar dataKey="finance" fill="#F59E0B" name="Finance" />
              <Bar dataKey="education" fill="#8B5CF6" name="Education" />
              <Bar dataKey="climate" fill="#06B6D4" name="Climate" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Technology Trends List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Trending Technologies */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Trending Technologies
            </h3>
            <TrendingUp className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <div className="space-y-4 max-h-[400px] overflow-y-auto">
            {data.trending_technologies.map((tech, index) => (
              <div key={index} className="p-4 rounded-lg border" style={{ backgroundColor: "var(--color-muted)", borderColor: "var(--color-border)" }}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    {getMaturityIcon(tech.maturity_stage)}
                    <span className="text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                      {tech.technology}
                    </span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded capitalize" 
                        style={{ 
                          backgroundColor: `${getMaturityStageColor(tech.maturity_stage)}20`,
                          color: getMaturityStageColor(tech.maturity_stage)
                        }}>
                    {tech.maturity_stage}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs" style={{ color: "var(--color-muted-foreground)" }}>
                  <div>
                    <span className="font-medium">{tech.adoption_rate.toFixed(1)}%</span>
                    <span className="block">Adoption Rate</span>
                  </div>
                  <div>
                    <span className="font-medium" style={{ color: tech.growth_rate > 0 ? '#10B981' : '#EF4444' }}>
                      +{tech.growth_rate.toFixed(1)}%
                    </span>
                    <span className="block">Growth Rate</span>
                  </div>
                  <div>
                    <span className="font-medium">{tech.geographic_spread}</span>
                    <span className="block">Countries</span>
                  </div>
                  <div>
                    <span className="font-medium">{tech.total_implementations}</span>
                    <span className="block">Implementations</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Innovation Hotspots */}
        <div className="p-6 rounded-lg border" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              Innovation Hotspots
            </h3>
            <Award className="h-5 w-5" style={{ color: "var(--color-primary)" }} />
          </div>
          <div className="space-y-4 max-h-[400px] overflow-y-auto">
            {data.innovation_hotspots.map((hotspot, index) => (
              <div key={index} className="p-4 rounded-lg border" style={{ backgroundColor: "var(--color-muted)", borderColor: "var(--color-border)" }}>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="text-sm font-semibold" style={{ color: "var(--color-card-foreground)" }}>
                      {hotspot.city}, {hotspot.country}
                    </span>
                    <p className="text-xs" style={{ color: "var(--color-muted-foreground)" }}>
                      {hotspot.region}
                    </p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded" 
                        style={{ 
                          backgroundColor: `${COUNTRY_COLORS[hotspot.country] || '#8B5CF6'}20`,
                          color: COUNTRY_COLORS[hotspot.country] || '#8B5CF6'
                        }}>
                    Score: {hotspot.ecosystem_strength}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs mb-3" style={{ color: "var(--color-muted-foreground)" }}>
                  <div>
                    <span className="font-medium">{hotspot.innovation_count}</span>
                    <span className="block">Innovations</span>
                  </div>
                  <div>
                    <span className="font-medium">{hotspot.density_per_million.toFixed(1)}</span>
                    <span className="block">Per Million</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1">
                  {hotspot.key_technologies.map((tech, techIndex) => (
                    <span key={techIndex} className="text-xs px-2 py-1 rounded" 
                          style={{ 
                            backgroundColor: `${Object.values(TECHNOLOGY_COLORS)[techIndex % Object.values(TECHNOLOGY_COLORS).length]}20`,
                            color: Object.values(TECHNOLOGY_COLORS)[techIndex % Object.values(TECHNOLOGY_COLORS).length]
                          }}>
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
