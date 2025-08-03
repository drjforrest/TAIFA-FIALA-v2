'use client'

import { useDashboard } from '@/hooks/useDashboard'
import { BarChart3, Users, FileText, Building2, Globe, Hash, TrendingUp } from 'lucide-react'

export default function DashboardStats() {
  const {
    total_publications,
    total_innovations,
    total_organizations,
    verified_individuals,
    african_countries_covered,
    unique_keywords,
    avg_african_relevance,
    avg_ai_relevance,
    loading,
    error
  } = useDashboard()

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-32"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-600 dark:text-red-400">Failed to load dashboard statistics: {error}</p>
      </div>
    )
  }

  const stats = [
    {
      label: 'Research Publications',
      value: total_publications,
      icon: FileText,
      description: 'Academic papers and research outputs',
      color: 'text-blue-600 dark:text-blue-400'
    },
    {
      label: 'AI Innovations',
      value: total_innovations,
      icon: BarChart3,
      description: 'Documented AI projects and solutions',
      color: 'text-green-600 dark:text-green-400'
    },
    {
      label: 'Organizations',
      value: total_organizations,
      icon: Building2,
      description: 'Universities, companies, and institutions',
      color: 'text-purple-600 dark:text-purple-400'
    },
    {
      label: 'Verified Contributors',
      value: verified_individuals,
      icon: Users,
      description: 'Researchers and innovators',
      color: 'text-orange-600 dark:text-orange-400'
    },
    {
      label: 'African Countries',
      value: african_countries_covered,
      icon: Globe,
      description: 'Geographic coverage across Africa',
      color: 'text-teal-600 dark:text-teal-400'
    },
    {
      label: 'Research Keywords',
      value: unique_keywords,
      icon: Hash,
      description: 'Unique research topics and domains',
      color: 'text-indigo-600 dark:text-indigo-400'
    },
    {
      label: 'African Relevance',
      value: `${(avg_african_relevance * 100).toFixed(1)}%`,
      icon: TrendingUp,
      description: 'Average African context relevance',
      color: 'text-red-600 dark:text-red-400'
    },
    {
      label: 'AI Technology Focus',
      value: `${(avg_ai_relevance * 100).toFixed(1)}%`,
      icon: TrendingUp,
      description: 'Average AI/ML technology relevance',
      color: 'text-cyan-600 dark:text-cyan-400'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          TAIFA-FIALA Innovation Archive
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Documenting African AI Excellence
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const IconComponent = stat.icon
          return (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                    {stat.label}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {stat.description}
                  </p>
                </div>
                <div className={`p-3 rounded-lg bg-gray-50 dark:bg-gray-700 ${stat.color}`}>
                  <IconComponent className="w-6 h-6" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-teal-500 rounded-lg p-6 text-white">
        <div className="text-center">
          <h3 className="text-xl font-bold mb-2">African AI Innovation Ecosystem</h3>
          <p className="text-blue-100 mb-4">
            Transforming research evidence into innovation opportunities across {african_countries_covered} African countries
          </p>
          <div className="flex justify-center space-x-8 text-sm">
            <div>
              <span className="block text-2xl font-bold">{total_publications}</span>
              <span className="text-blue-100">Research Papers</span>
            </div>
            <div>
              <span className="block text-2xl font-bold">{total_innovations}</span>
              <span className="text-blue-100">Innovations</span>
            </div>
            <div>
              <span className="block text-2xl font-bold">{african_countries_covered}</span>
              <span className="text-blue-100">Countries</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}