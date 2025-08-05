'use client'

import { useState } from 'react'
import { CheckCircle, Zap, FileText, ChevronDown, ChevronUp, ExternalLink, Clock } from 'lucide-react'
import { EnrichmentCitation } from '@/lib/supabase'

export interface DataProvenanceProps {
  dataSource?: 'primary' | 'enriched' | 'systematic_review'
  enrichmentConfidence?: number
  enrichmentCitations?: EnrichmentCitation[]
  originalDiscoveryMethod?: string
  showExpanded?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export default function DataProvenance({
  dataSource = 'primary',
  enrichmentConfidence,
  enrichmentCitations = [],
  originalDiscoveryMethod,
  showExpanded = false,
  size = 'md'
}: DataProvenanceProps) {
  const [isExpanded, setIsExpanded] = useState(showExpanded)

  const getSourceConfig = () => {
    switch (dataSource) {
      case 'primary':
        return {
          icon: CheckCircle,
          label: 'Primary Source',
          color: 'text-green-600 dark:text-green-400',
          bgColor: 'bg-green-50 dark:bg-green-900/20',
          borderColor: 'border-green-200 dark:border-green-800',
          description: 'Directly sourced from original publication or verified source'
        }
      case 'enriched':
        return {
          icon: Zap,
          label: 'AI Enhanced',
          color: 'text-orange-600 dark:text-orange-400',
          bgColor: 'bg-orange-50 dark:bg-orange-900/20',
          borderColor: 'border-orange-200 dark:border-orange-800',
          description: 'Enhanced with AI-powered research and verification'
        }
      case 'systematic_review':
        return {
          icon: FileText,
          label: 'Systematic Review',
          color: 'text-blue-600 dark:text-blue-400',
          bgColor: 'bg-blue-50 dark:bg-blue-900/20',
          borderColor: 'border-blue-200 dark:border-blue-800',
          description: 'Extracted from peer-reviewed systematic review'
        }
    }
  }

  const config = getSourceConfig()
  const Icon = config.icon

  const sizeClasses = {
    sm: {
      badge: 'px-2 py-1 text-xs',
      icon: 'h-3 w-3',
      text: 'text-xs'
    },
    md: {
      badge: 'px-3 py-1 text-sm',
      icon: 'h-4 w-4',
      text: 'text-sm'
    },
    lg: {
      badge: 'px-4 py-2 text-base',
      icon: 'h-5 w-5',
      text: 'text-base'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="data-provenance">
      {/* Main Badge */}
      <div className={`inline-flex items-center ${sizeClasses[size].badge} rounded-full font-medium border ${config.color} ${config.bgColor} ${config.borderColor}`}>
        <Icon className={`${sizeClasses[size].icon} mr-1`} />
        <span>{config.label}</span>
        {dataSource === 'enriched' && enrichmentConfidence && (
          <span className="ml-1 opacity-75">
            ({(enrichmentConfidence * 100).toFixed(0)}%)
          </span>
        )}
        
        {/* Expand button for enriched data */}
        {dataSource === 'enriched' && enrichmentCitations.length > 0 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="ml-2 hover:opacity-70 transition-opacity"
            title={isExpanded ? 'Hide sources' : 'Show sources'}
          >
            {isExpanded ? (
              <ChevronUp className="h-3 w-3" />
            ) : (
              <ChevronDown className="h-3 w-3" />
            )}
          </button>
        )}
      </div>

      {/* Expanded Details */}
      {isExpanded && dataSource === 'enriched' && (
        <div className={`mt-3 p-3 rounded-lg border ${config.borderColor} ${config.bgColor}`}>
          <div className={`${sizeClasses[size].text} ${config.color} font-medium mb-2`}>
            Enhancement Sources
          </div>
          
          {originalDiscoveryMethod && (
            <div className={`${sizeClasses[size].text} text-gray-600 dark:text-gray-400 mb-3`}>
              <strong>Discovery Method:</strong> {originalDiscoveryMethod}
            </div>
          )}

          <div className="space-y-2">
            {enrichmentCitations.map((citation, index) => (
              <div
                key={citation.id}
                className="flex items-start space-x-2 p-2 rounded border bg-white/50 dark:bg-gray-800/50"
              >
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-bold text-gray-600 dark:text-gray-300">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {citation.url ? (
                        <a
                          href={citation.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`${sizeClasses[size].text} font-medium ${config.color} hover:underline line-clamp-2`}
                          title={citation.title}
                        >
                          {citation.title}
                          <ExternalLink className="inline h-3 w-3 ml-1" />
                        </a>
                      ) : (
                        <span className={`${sizeClasses[size].text} font-medium text-gray-900 dark:text-gray-100 line-clamp-2`}>
                          {citation.title}
                        </span>
                      )}
                      
                      {citation.citation_text && (
                        <p className={`${sizeClasses[size].text} text-gray-600 dark:text-gray-400 mt-1 line-clamp-2`}>
                          {citation.citation_text}
                        </p>
                      )}
                      
                      <div className="flex items-center space-x-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <div className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatTimestamp(citation.discovered_at)}
                        </div>
                        <div className="flex items-center">
                          <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                            citation.confidence_score >= 0.8 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                              : citation.confidence_score >= 0.6
                              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                              : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                          }`}>
                            {(citation.confidence_score * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                        {!citation.processed && (
                          <span className="px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                            Pending ingestion
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {enrichmentCitations.length === 0 && (
            <p className={`${sizeClasses[size].text} text-gray-500 dark:text-gray-400 italic`}>
              No source citations available
            </p>
          )}
        </div>
      )}

      {/* Description tooltip for non-expanded */}
      {!isExpanded && (
        <div className={`${sizeClasses[size].text} text-gray-500 dark:text-gray-400 mt-1`}>
          {config.description}
        </div>
      )}
    </div>
  )
}