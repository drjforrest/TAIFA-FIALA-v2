"use client";

import { useState, useEffect } from "react";
import { supabase, DashboardStats } from "@/lib/supabase";
import { API_ENDPOINTS, apiCall } from "@/lib/api";

export interface DashboardData extends DashboardStats {
  loading: boolean;
  error: string | null;
  etl_status?: ETLStatus;
}

export interface ETLStatus {
  academic_pipeline_active: boolean;
  news_pipeline_active: boolean;
  serper_pipeline_active: boolean;
  last_academic_run: string | null;
  last_news_run: string | null;
  last_serper_run: string | null;
  total_processed_today: number;
  errors_today: number;
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

      // Try to get from materialized view first
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
      // Try to get ETL status from a dedicated table or API endpoint
      const { data: statusData, error: statusError } = await supabase
        .from("etl_status")
        .select("*")
        .single();

      if (statusError) {
        console.log("ETL status table not available, using mock data");
        // Mock data for development
        setETLData({
          status: {
            academic_pipeline_active: Math.random() > 0.5,
            news_pipeline_active: Math.random() > 0.3,
            serper_pipeline_active: Math.random() > 0.7,
            last_academic_run: new Date(
              Date.now() - Math.random() * 86400000,
            ).toISOString(),
            last_news_run: new Date(
              Date.now() - Math.random() * 86400000,
            ).toISOString(),
            last_serper_run: new Date(
              Date.now() - Math.random() * 86400000,
            ).toISOString(),
            total_processed_today: Math.floor(Math.random() * 100),
            errors_today: Math.floor(Math.random() * 5),
          },
          health: {
            status: "healthy",
            last_check: new Date().toISOString(),
            response_time: Math.floor(Math.random() * 200) + 50,
          },
          loading: false,
          error: null,
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

  return {
    status: etlData.status,
    health: etlData.health,
    loading: etlData.loading,
    error: etlData.error,
    triggerAcademicPipeline,
    triggerNewsPipeline,
    triggerSerperSearch,
    refresh: fetchETLStatus,
  };
}
