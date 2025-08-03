'use client'

import { useRecentActivity } from '@/hooks/useDashboard'
import { FileText, Lightbulb, Calendar, ExternalLink, Star } from 'lucide-react'
import Link from 'next/link'

export default function RecentActivity() {
  const { recentPublications, recentInnovations, loading, error } = useRecentActivity()

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-96"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-600 dark:text-red-400">Failed to load recent activity: {error}</p>
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'No date'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 dark:text-green-400'
    if (score >= 0.6) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'production': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'pilot': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
      case 'prototype': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'concept': return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getVerificationBadge = (status: string) => {
    switch (status) {
      case 'verified': return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
          <Star className="w-3 h-3 mr-1" />
          Verified
        </span>
      )
      case 'community_verified': return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
          Community Verified
        </span>
      )
      default: return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400">
          Pending
        </span>
      )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Recent Activity
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Latest additions to the African AI innovation archive
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Publications */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2" />
              <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                Recent Publications
              </h4>
            </div>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {recentPublications.length === 0 ? (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                No publications found. Upload data to see recent activity.
              </div>
            ) : (
              recentPublications.map((pub, index) => (
                <div key={pub.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h5 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {pub.title}
                      </h5>
                      <div className="flex items-center mt-2 space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <div className="flex items-center">
                          <Calendar className="w-3 h-3 mr-1" />
                          {formatDate(pub.publication_date)}
                        </div>
                        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                          {pub.source}
                        </span>
                      </div>
                      <div className="flex items-center mt-2 space-x-4">
                        <div className="text-xs">
                          <span className="text-gray-500 dark:text-gray-400">African: </span>
                          <span className={getScoreColor(pub.african_relevance_score)}>
                            {(pub.african_relevance_score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="text-xs">
                          <span className="text-gray-500 dark:text-gray-400">AI: </span>
                          <span className={getScoreColor(pub.ai_relevance_score)}>
                            {(pub.ai_relevance_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
            <Link 
              href="/publications" 
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
            >
              View all publications →
            </Link>
          </div>
        </div>

        {/* Recent Innovations */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <Lightbulb className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-2" />
              <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                Recent Innovations
              </h4>
            </div>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {recentInnovations.length === 0 ? (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                No innovations found. Submit innovations to see activity.
              </div>
            ) : (
              recentInnovations.map((innovation, index) => (
                <div key={innovation.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h5 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {innovation.title}
                      </h5>
                      <div className="flex items-center mt-2 space-x-2">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 rounded text-xs">
                          {innovation.domain}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${getStageColor(innovation.development_stage)}`}>
                          {innovation.development_stage}
                        </span>
                      </div>
                      <div className="mt-2">
                        {getVerificationBadge(innovation.verification_status)}
                      </div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
            <Link 
              href="/innovations" 
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
            >
              View all innovations →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}