'use client'

import { useState, useEffect } from 'react'
import { useRecentActivity } from '@/hooks/useDashboard'
import { 
  Activity, 
  FileText, 
  Lightbulb, 
  Users, 
  ExternalLink, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  MapPin,
  Building2,
  ArrowUpRight,
  RefreshCw
} from 'lucide-react'
import Link from 'next/link'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ActivityItem {
  id: string
  type: 'innovation' | 'publication' | 'submission' | 'verification'
  title: string
  description?: string
  timestamp: string
  status?: string
  country?: string
  organization?: string
  url?: string
  metadata?: {
    innovation_type?: string
    verification_status?: string
    publication_type?: string
    domain?: string
    funding_amount?: number
  }
}

export default function RecentActivity() {
  const { 
    recentInnovations, 
    recentPublications, 
    loading, 
    error 
  } = useRecentActivity()

  const [allActivity, setAllActivity] = useState<ActivityItem[]>([])
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    // Combine all activity types into a single feed
    const combinedActivity: ActivityItem[] = [
      // Recent innovations
      ...recentInnovations.map(innovation => ({
        id: innovation.id,
        type: 'innovation' as const,
        title: innovation.title,
        description: innovation.description,
        timestamp: innovation.created_at || innovation.creation_date,
        country: innovation.country,
        organization: innovation.organizations?.[0]?.name,
        metadata: {
          innovation_type: innovation.innovation_type,
          verification_status: innovation.verification_status
        }
      })),
      // Recent publications
      ...recentPublications.map(publication => ({
        id: publication.id,
        type: 'publication' as const,
        title: publication.title,
        timestamp: publication.created_at || publication.publication_date,
        url: publication.url || publication.source,
        metadata: {
          publication_type: publication.publication_type,
          domain: publication.domain
        }
      }))
    ]

    // Sort by timestamp (most recent first)
    const sortedActivity = combinedActivity.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    ).slice(0, 20) // Limit to 20 most recent items

    setAllActivity(sortedActivity)
  }, [recentInnovations, recentPublications])

  const handleRefresh = async () => {
    setRefreshing(true)
    // The useRecentActivity hook will automatically refresh
    setTimeout(() => setRefreshing(false), 2000)
  }

  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'innovation':
        return <Lightbulb className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
      case 'publication':
        return <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
      case 'submission':
        return <Users className="h-5 w-5 text-green-600 dark:text-green-400" />
      case 'verification':
        return <CheckCircle className="h-5 w-5 text-purple-600 dark:text-purple-400" />
      default:
        return <Activity className="h-5 w-5 text-gray-600 dark:text-gray-400" />
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'verified':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
      case 'pending':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
      case 'community':
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
      case 'rejected':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20'
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}d ago`
    return date.toLocaleDateString()
  }

  if (loading && allActivity.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Recent Activity</h2>
        <div className="space-y-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="animate-pulse flex items-center space-x-4 p-4">
              <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Recent Activity
        </h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 mr-2" />
            <p className="text-sm text-amber-700 dark:text-amber-300">{error}</p>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {allActivity.length === 0 ? (
          <div className="p-8 text-center">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No recent activity
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Innovation discoveries and research publications will appear here as they're processed.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {allActivity.map((item, index) => (
              <div 
                key={`${item.type}-${item.id}-${index}`} 
                className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-start space-x-4">
                  {/* Activity Icon */}
                  <div className="flex-shrink-0 p-2 rounded-full bg-gray-100 dark:bg-gray-700">
                    {getActivityIcon(item.type)}
                  </div>

                  {/* Activity Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                          {item.title}
                        </h4>
                        
                        {item.description && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                            {item.description}
                          </p>
                        )}

                        <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            {formatTimestamp(item.timestamp)}
                          </span>
                          
                          {item.country && (
                            <span className="flex items-center">
                              <MapPin className="h-3 w-3 mr-1" />
                              {item.country}
                            </span>
                          )}
                          
                          {item.organization && (
                            <span className="flex items-center">
                              <Building2 className="h-3 w-3 mr-1" />
                              {item.organization}
                            </span>
                          )}
                        </div>

                        {/* Metadata Tags */}
                        <div className="flex items-center space-x-2 mt-2">
                          {item.metadata?.innovation_type && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                              {item.metadata.innovation_type}
                            </span>
                          )}
                          
                          {item.metadata?.verification_status && (
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.metadata.verification_status)}`}>
                              {item.metadata.verification_status}
                            </span>
                          )}
                          
                          {item.metadata?.publication_type && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                              {item.metadata.publication_type}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Action Button */}
                      <div className="flex-shrink-0 ml-4">
                        {item.type === 'innovation' ? (
                          <Link
                            href={`/innovations/${item.id}`}
                            className="inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                          >
                            View
                            <ArrowUpRight className="h-3 w-3 ml-1" />
                          </Link>
                        ) : item.url ? (
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                          >
                            View
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        ) : (
                          <span className="text-xs text-gray-400 dark:text-gray-500">
                            Processing...
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* View All Activity Link */}
        {allActivity.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
            <Link
              href="/activity"
              className="flex items-center justify-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              View All Activity
              <ArrowUpRight className="h-4 w-4 ml-1" />
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}