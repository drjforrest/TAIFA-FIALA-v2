'use client'

import { useState } from 'react'
import { usePublications, PublicationFilters } from '@/hooks/usePublications'
import { Search, Filter, ExternalLink, Calendar, Star, Globe, Cpu } from 'lucide-react'

export default function PublicationsTable() {
  const [filters, setFilters] = useState<PublicationFilters>({
    limit: 20,
    offset: 0
  })
  const [searchTerm, setSearchTerm] = useState('')

  const { publications, total, loading, error } = usePublications(filters)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setFilters(prev => ({
      ...prev,
      search: searchTerm,
      offset: 0
    }))
  }

  const handleFilterChange = (key: keyof PublicationFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      offset: 0
    }))
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'No date'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
    if (score >= 0.6) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
    return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20'
  }

  const getSourceBadge = (source: string) => {
    const colors = {
      'arxiv': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      'pubmed': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      'google_scholar': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      'systematic_review': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
      'manual': 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
    return colors[source as keyof typeof colors] || colors.manual
  }

  if (loading && publications.length === 0) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-32"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Research Publications
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {total.toLocaleString()} African AI research papers and publications
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 mb-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search publications by title or abstract..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </form>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <select
            value={filters.source || ''}
            onChange={(e) => handleFilterChange('source', e.target.value || undefined)}
            className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Sources</option>
            <option value="arxiv">ArXiv</option>
            <option value="pubmed">PubMed</option>
            <option value="google_scholar">Google Scholar</option>
            <option value="systematic_review">Systematic Review</option>
          </select>

          <select
            value={filters.year || ''}
            onChange={(e) => handleFilterChange('year', e.target.value ? parseInt(e.target.value) : undefined)}
            className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Years</option>
            {Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - i).map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>

          <select
            value={filters.minAfricanScore || ''}
            onChange={(e) => handleFilterChange('minAfricanScore', e.target.value ? parseFloat(e.target.value) : undefined)}
            className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Any African Relevance</option>
            <option value="0.8">High (80%+)</option>
            <option value="0.6">Medium (60%+)</option>
            <option value="0.4">Low (40%+)</option>
          </select>

          <select
            value={filters.minAiScore || ''}
            onChange={(e) => handleFilterChange('minAiScore', e.target.value ? parseFloat(e.target.value) : undefined)}
            className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Any AI Relevance</option>
            <option value="0.8">High (80%+)</option>
            <option value="0.6">Medium (60%+)</option>
            <option value="0.4">Low (40%+)</option>
          </select>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">Error loading publications: {error}</p>
        </div>
      )}

      {/* Publications List */}
      <div className="space-y-4">
        {publications.length === 0 && !loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              No publications found. Try adjusting your search criteria or load data into the database.
            </p>
          </div>
        ) : (
          publications.map((publication) => (
            <div
              key={publication.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {publication.title}
                  </h3>
                  
                  {publication.abstract && (
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                      {publication.abstract}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center gap-4 mb-4">
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(publication.publication_date)}
                    </div>

                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSourceBadge(publication.source)}`}>
                      {publication.source.replace('_', ' ')}
                    </span>

                    {publication.journal && (
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {publication.journal}
                      </span>
                    )}

                    {publication.project_domain && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                        {publication.project_domain}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <Globe className="w-4 h-4 mr-1 text-gray-400" />
                      <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">African:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(publication.african_relevance_score)}`}>
                        {(publication.african_relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="flex items-center">
                      <Cpu className="w-4 h-4 mr-1 text-gray-400" />
                      <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">AI:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(publication.ai_relevance_score)}`}>
                        {(publication.ai_relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>

                    {publication.african_entities && publication.african_entities.length > 0 && (
                      <div className="flex items-center">
                        <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">Countries:</span>
                        <span className="text-xs text-gray-600 dark:text-gray-300">
                          {publication.african_entities.slice(0, 3).join(', ')}
                          {publication.african_entities.length > 3 && ` +${publication.african_entities.length - 3} more`}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {publication.url && (
                    <a
                      href={publication.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                      title="View publication"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Loading indicator */}
      {loading && publications.length > 0 && (
        <div className="text-center py-4">
          <div className="inline-flex items-center px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Loading more publications...
          </div>
        </div>
      )}

      {/* Pagination */}
      {total > (filters.limit || 20) && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Showing {(filters.offset || 0) + 1} to {Math.min((filters.offset || 0) + (filters.limit || 20), total)} of {total} results
          </p>
          <div className="flex space-x-2">
            <button
              onClick={() => handleFilterChange('offset', Math.max(0, (filters.offset || 0) - (filters.limit || 20)))}
              disabled={!filters.offset}
              className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Previous
            </button>
            <button
              onClick={() => handleFilterChange('offset', (filters.offset || 0) + (filters.limit || 20))}
              disabled={(filters.offset || 0) + (filters.limit || 20) >= total}
              className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}