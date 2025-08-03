'use client'

import { useState, useEffect } from 'react'
import { supabase, Publication } from '@/lib/supabase'

export interface PublicationFilters {
  search?: string
  domain?: string
  source?: string
  year?: number
  minAfricanScore?: number
  minAiScore?: number
  limit?: number
  offset?: number
}

export interface PublicationsResult {
  publications: Publication[]
  total: number
  loading: boolean
  error: string | null
}

export function usePublications(filters: PublicationFilters = {}): PublicationsResult {
  const [publications, setPublications] = useState<Publication[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPublications()
  }, [
    filters.search,
    filters.domain,
    filters.source,
    filters.year,
    filters.minAfricanScore,
    filters.minAiScore,
    filters.limit,
    filters.offset
  ])

  const fetchPublications = async () => {
    try {
      setLoading(true)
      setError(null)

      // Build query
      let query = supabase
        .from('publications')
        .select('*', { count: 'exact' })
        .order('publication_date', { ascending: false })

      // Apply filters
      if (filters.search) {
        query = query.or(`title.ilike.%${filters.search}%,abstract.ilike.%${filters.search}%`)
      }

      if (filters.domain) {
        query = query.eq('project_domain', filters.domain)
      }

      if (filters.source) {
        query = query.eq('source', filters.source)
      }

      if (filters.year) {
        query = query.eq('year', filters.year)
      }

      if (filters.minAfricanScore !== undefined) {
        query = query.gte('african_relevance_score', filters.minAfricanScore)
      }

      if (filters.minAiScore !== undefined) {
        query = query.gte('ai_relevance_score', filters.minAiScore)
      }

      // Apply pagination
      if (filters.limit) {
        query = query.limit(filters.limit)
      }

      if (filters.offset) {
        query = query.range(filters.offset, filters.offset + (filters.limit || 10) - 1)
      }

      const { data, error: queryError, count } = await query

      if (queryError) {
        throw queryError
      }

      setPublications(data || [])
      setTotal(count || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch publications')
      console.error('Error fetching publications:', err)
    } finally {
      setLoading(false)
    }
  }

  return { publications, total, loading, error }
}

// Hook for getting publication statistics
export function usePublicationStats() {
  const [stats, setStats] = useState({
    totalPublications: 0,
    bySource: {} as Record<string, number>,
    byYear: {} as Record<string, number>,
    byDomain: {} as Record<string, number>,
    avgAfricanScore: 0,
    avgAiScore: 0,
    loading: true,
    error: null as string | null
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      // Get total count
      const { count: totalCount, error: countError } = await supabase
        .from('publications')
        .select('*', { count: 'exact', head: true })

      if (countError) throw countError

      // Get aggregated stats
      const { data: publications, error: dataError } = await supabase
        .from('publications')
        .select('source, year, project_domain, african_relevance_score, ai_relevance_score')

      if (dataError) throw dataError

      // Process stats
      const bySource: Record<string, number> = {}
      const byYear: Record<string, number> = {}
      const byDomain: Record<string, number> = {}
      let africanScoreSum = 0
      let aiScoreSum = 0
      let scoresCount = 0

      publications?.forEach(pub => {
        // Source stats
        bySource[pub.source] = (bySource[pub.source] || 0) + 1

        // Year stats
        if (pub.year) {
          byYear[pub.year.toString()] = (byYear[pub.year.toString()] || 0) + 1
        }

        // Domain stats
        if (pub.project_domain) {
          byDomain[pub.project_domain] = (byDomain[pub.project_domain] || 0) + 1
        }

        // Score averages
        if (pub.african_relevance_score > 0 && pub.ai_relevance_score > 0) {
          africanScoreSum += pub.african_relevance_score
          aiScoreSum += pub.ai_relevance_score
          scoresCount++
        }
      })

      setStats({
        totalPublications: totalCount || 0,
        bySource,
        byYear,
        byDomain,
        avgAfricanScore: scoresCount > 0 ? africanScoreSum / scoresCount : 0,
        avgAiScore: scoresCount > 0 ? aiScoreSum / scoresCount : 0,
        loading: false,
        error: null
      })
    } catch (err) {
      setStats(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch stats'
      }))
      console.error('Error fetching publication stats:', err)
    }
  }

  return stats
}