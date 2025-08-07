"use client";

import { API_ENDPOINTS, apiCall } from "@/lib/api";
import { DashboardStats, supabase } from "@/lib/supabase";
import { useEffect, useState } from "react";

export interface DashboardData extends DashboardStats {
  loading: boolean;
  error: string | null;
  etl_status?: ETLStatus;
}

export interface ETLMetrics {
  batch_size: number;
  duplicates_removed: number;
  processing_time_ms: number;
  success_rate: number;
  items_processed: number;
  items_failed: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
}

export interface ETLStatus {
  academic_pipeline_active: boolean;
  news_pipeline_active: boolean;
  serper_pipeline_active: boolean;
  enrichment_pipeline_active: boolean;
  last_academic_run: string | null;
  last_news_run: string | null;
  last_serper_run: string | null;
  last_enrichment_run: string | null;
  total_processed_today: number;
  errors_today: number;
  metrics?: ETLMetrics;
  pipeline_metrics?: {
    academic_pipeline?: ETLMetrics;
    news_pipeline?: ETLMetrics;
    discovery_pipeline?: ETLMetrics;
    enrichment_pipeline?: ETLMetrics;
  };
}

export interface ETLHealth {
  status: "healthy" | "degraded" | "down";
  last_check: string;
  response_time: number;
}

export interface APIResponse {
  success: boolean;
  message?: string;
  data?: any;
}

export function useDashboard(): DashboardData {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    total_publications: 0,
    total_innovations: 0,
    total_organizations: 0,
    verified_individuals: 0,
    african_countries_covered: 0,
    unique_keywords: 0,
    avg_african_relevance: 0,
    avg_ai_relevance: 0,
    last_updated: "",
    loading: true,
    error: null,
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setDashboardData((prev) => ({ ...prev, loading: true, error: null }));

      // Try to get from backend API first
      try {
        const apiData = await apiCall<any>(API_ENDPOINTS.stats);
        
        setDashboardData({
          total_publications: apiData.total_publications || 0,
          total_innovations: apiData.total_innovations || 0,
          total_organizations: apiData.total_organizations || 0,
          verified_individuals: apiData.verified_individuals || 0,
          african_countries_covered: apiData.african_countries_covered || 0,
          unique_keywords: apiData.unique_keywords || 0,
          avg_african_relevance: apiData.avg_african_relevance || 0,
          avg_ai_relevance: apiData.avg_ai_relevance || 0,
          last_updated: apiData.last_updated || new Date().toISOString(),
          loading: false,
          error: null,
        });
        return;
      } catch (apiError) {
        console.log('Backend API not available, trying Supadatabase...');
      }

      // Try to get from materialized view as fallback
      const { data: viewData, error: viewError } = await supabase
        .from("dashboard_stats")
        .select("*")
        .single();

      if (viewData && !viewError) {
        setDashboardData({
          ...viewData,
          loading: false,
          error: null,
        });
        return;
      }

      // If materialized view fails, calculate manually
      console.log(
        "Materialized view not available, calculating stats manually...",
      );

      const [
        publicationsResult,
        innovationsResult,
        organizationsResult,
        individualsResult,
      ] = await Promise.all([
        supabase
          .from("publications")
          .select("*", { count: "exact", head: true }),
        supabase
          .from("innovations")
          .select("*", { count: "exact", head: true }),
        supabase
          .from("organizations")
          .select("*", { count: "exact", head: true }),
        supabase
          .from("individuals")
          .select("*", { count: "exact" })
          .eq("verification_status", "verified"),
      ]);

      // Get detailed data for calculations
      const { data: publications } = await supabase
        .from("publications")
        .select(
          "african_entities, keywords, african_relevance_score, ai_relevance_score",
        );

      // Calculate derived stats
      const africanCountries = new Set<string>();
      const keywords = new Set<string>();
      let africanScoreSum = 0;
      let aiScoreSum = 0;
      let scoresCount = 0;

      publications?.forEach((pub) => {
        // African entities
        if (pub.african_entities) {
          pub.african_entities.forEach((entity: string) =>
            africanCountries.add(entity),
          );
        }

        // Keywords
        if (pub.keywords) {
          pub.keywords.forEach((keyword: string) => keywords.add(keyword));
        }

        // Scores
        if (pub.african_relevance_score > 0 && pub.ai_relevance_score > 0) {
          africanScoreSum += pub.african_relevance_score;
          aiScoreSum += pub.ai_relevance_score;
          scoresCount++;
        }
      });

      setDashboardData({
        total_publications: publicationsResult.count || 0,
        total_innovations: innovationsResult.count || 0,
        total_organizations: organizationsResult.count || 0,
        verified_individuals: individualsResult.count || 0,
        african_countries_covered: africanCountries.size,
        unique_keywords: keywords.size,
        avg_african_relevance:
          scoresCount > 0 ? africanScoreSum / scoresCount : 0,
        avg_ai_relevance: scoresCount > 0 ? aiScoreSum / scoresCount : 0,
        last_updated: new Date().toISOString(),
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error("Error fetching dashboard stats:", err);
      setDashboardData((prev) => ({
        ...prev,
        loading: false,
        error:
          err instanceof Error
            ? err.message
            : "Failed to fetch dashboard statistics",
      }));
    }
  };

  return dashboardData;
}

// Hook for getting recent activity
export function useRecentActivity() {
  const [activity, setActivity] = useState({
    recentPublications: [] as any[],
    recentInnovations: [] as any[],
    loading: true,
    error: null as string | null,
  });

  useEffect(() => {
    fetchRecentActivity();
  }, []);

  const fetchRecentActivity = async () => {
    try {
      const [publicationsResult, innovationsResult] = await Promise.all([
        supabase
          .from("publications")
          .select(
            "id, title, publication_date, source, african_relevance_score, ai_relevance_score",
          )
          .order("created_at", { ascending: false })
          .limit(5),
        supabase
          .from("innovations")
          .select("id, title, domain, development_stage, verification_status")
          .eq("visibility", "public")
          .order("created_at", { ascending: false })
          .limit(5),
      ]);

      setActivity({
        recentPublications: publicationsResult.data || [],
        recentInnovations: innovationsResult.data || [],
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error("Error fetching recent activity:", err);
      setActivity((prev) => ({
        ...prev,
        loading: false,
        error:
          err instanceof Error
            ? err.message
            : "Failed to fetch recent activity",
      }));
    }
  };

  return activity;
}

// Hook for ETL monitoring and control
export function useETLMonitoring() {
  const [etlData, setETLData] = useState<{
    status: ETLStatus | null;
    health: ETLHealth | null;
    loading: boolean;
    error: string | null;
  }>({
    status: null,
    health: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    fetchETLStatus();
    // Set up polling every 30 seconds
    const interval = setInterval(fetchETLStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchETLStatus = async () => {
    try {
      setETLData(prev => ({ ...prev, loading: true, error: null }));

      // Try to get ETL status from the backend API first
      try {
        const etlStatusResponse = await apiCall<any>(API_ENDPOINTS.etl.status);
        
        if (etlStatusResponse && etlStatusResponse.unified_status) {
          // Use the unified_status directly from backend
          const unifiedStatus = etlStatusResponse.unified_status;
          
          // Convert backend response to frontend ETLStatus format
          const status: ETLStatus = {
            academic_pipeline_active: unifiedStatus.academic_pipeline_active || false,
            news_pipeline_active: unifiedStatus.news_pipeline_active || false,
            serper_pipeline_active: unifiedStatus.serper_pipeline_active || false,
            enrichment_pipeline_active: unifiedStatus.enrichment_pipeline_active || false,
            last_academic_run: unifiedStatus.last_academic_run,
            last_news_run: unifiedStatus.last_news_run,
            last_serper_run: unifiedStatus.last_serper_run,
            last_enrichment_run: unifiedStatus.last_enrichment_run,
            total_processed_today: unifiedStatus.total_processed_today || 0,
            errors_today: unifiedStatus.errors_today || 0,
          };

          const health: ETLHealth = {
            status: unifiedStatus.system_health === 'healthy' ? 'healthy' : 'degraded',
            last_check: unifiedStatus.last_updated || new Date().toISOString(),
            response_time: 150,
          };

          setETLData({
            status,
            health,
            loading: false,
            error: null,
          });
          return;
        }
      } catch (apiError) {
        console.log('ETL API not available, trying Supabase fallback...', apiError);
      }

      // Fallback to Supabase table if API fails
      const { data: statusData, error: statusError } = await supabase
        .from("etl_status")
        .select("*")
        .single();

      if (statusError) {
        console.log("ETL status table not available, using default inactive state");
        // Default to inactive state when no data source is available
        setETLData({
          status: {
            academic_pipeline_active: false,
            news_pipeline_active: false,
            serper_pipeline_active: false,
            enrichment_pipeline_active: false,
            last_academic_run: null,
            last_news_run: null,
            last_serper_run: null,
            last_enrichment_run: null,
            total_processed_today: 0,
            errors_today: 0,
          },
          health: {
            status: "down",
            last_check: new Date().toISOString(),
            response_time: 0,
          },
          loading: false,
          error: "ETL monitoring unavailable",
        });
      } else {
        setETLData({
          status: statusData,
          health: {
            status: "healthy",
            last_check: new Date().toISOString(),
            response_time: 150,
          },
          loading: false,
          error: null,
        });
      }
    } catch (err) {
      console.error("Error fetching ETL status:", err);
      setETLData((prev) => ({
        ...prev,
        loading: false,
        error:
          err instanceof Error ? err.message : "Failed to fetch ETL status",
      }));
    }
  };

  const triggerAcademicPipeline = async () => {
    try {
      const result = await apiCall<APIResponse>(API_ENDPOINTS.etl.triggerAcademic, {
        method: 'POST',
      });

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return {
          success: true,
          message: result.message || "Academic pipeline triggered successfully",
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger academic pipeline",
        };
      }
    } catch (err) {
      console.error("Error triggering academic pipeline:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger academic pipeline",
      };
    }
  };

  const triggerNewsPipeline = async () => {
    try {
      const result = await apiCall<APIResponse>(API_ENDPOINTS.etl.triggerNews, {
        method: 'POST',
      });

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return { 
          success: true, 
          message: result.message || "News pipeline triggered successfully" 
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger news pipeline",
        };
      }
    } catch (err) {
      console.error("Error triggering news pipeline:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger news pipeline",
      };
    }
  };

  const triggerSerperSearch = async (query?: string) => {
    try {
      const result = await apiCall<APIResponse>(API_ENDPOINTS.etl.triggerDiscovery, {
        method: 'POST',
        ...(query && {
          body: JSON.stringify({ query }),
        }),
      });

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return {
          success: true,
          message: result.message || "Discovery search triggered successfully",
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger discovery search",
        };
      }
    } catch (err) {
      console.error("Error triggering Serper search:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger Serper search",
      };
    }
  };

  const triggerEnrichment = async (
    innovation_ids?: string[],
    max_jobs: number = 10
  ) => {
    try {
      const result = await apiCall<APIResponse>(API_ENDPOINTS.etl.triggerEnrichment, {
        method: 'POST',
        body: JSON.stringify({ 
          innovation_ids,
          max_jobs
        }),
      });

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return {
          success: true,
          message: result.message || "AI enrichment triggered successfully",
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger AI enrichment",
        };
      }
    } catch (err) {
      console.error("Error triggering AI enrichment:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger AI enrichment",
      };
    }
  };

  return {
    status: etlData.status,
    health: etlData.health,
    loading: etlData.loading,
    error: etlData.error,
    triggerAcademicPipeline,
    triggerNewsPipeline,
    triggerSerperSearch,
    triggerEnrichment,
    refresh: fetchETLStatus,
  };
}
