"use client";

import React, { useState } from "react";
import { useDashboard, useETLMonitoring } from "@/hooks/useDashboard";
import {
  BarChart3,
  Users,
  FileText,
  Building2,
  Globe,
  Hash,
  TrendingUp,
  Activity,
  CheckCircle,
  XCircle,
  Play,
  RefreshCw,
  Database,
  Zap,
  AlertTriangle,
} from "lucide-react";
import {
  Section1Text,
  Section2Text,
  Section3Text,
  Section4Text,
} from "@/components/ui/adaptive-text";

export default function DashboardStats() {
  const [feedbackMessage, setFeedbackMessage] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const {
    total_publications,
    total_innovations,
    total_organizations,
    verified_individuals,
    african_countries_covered,
    unique_keywords,
    avg_african_relevance,
    avg_ai_relevance,
    etl_status,
    loading,
    error,
  } = useDashboard();

  const {
    status: etlStatus,
    health: etlHealth,
    triggerAcademicPipeline,
    triggerNewsPipeline,
    triggerSerperSearch,
    loading: etlLoading,
  } = useETLMonitoring();

  // Enhanced trigger functions with user feedback
  const handleTriggerAcademic = async () => {
    setFeedbackMessage({ type: null, message: '' });
    const result = await triggerAcademicPipeline();
    setFeedbackMessage({
      type: result.success ? 'success' : 'error',
      message: result.message
    });
    // Clear message after 5 seconds
    setTimeout(() => setFeedbackMessage({ type: null, message: '' }), 5000);
  };

  const handleTriggerNews = async () => {
    setFeedbackMessage({ type: null, message: '' });
    const result = await triggerNewsPipeline();
    setFeedbackMessage({
      type: result.success ? 'success' : 'error',
      message: result.message
    });
    setTimeout(() => setFeedbackMessage({ type: null, message: '' }), 5000);
  };

  const handleTriggerDiscovery = async () => {
    setFeedbackMessage({ type: null, message: '' });
    const result = await triggerSerperSearch();
    setFeedbackMessage({
      type: result.success ? 'success' : 'error',
      message: result.message
    });
    setTimeout(() => setFeedbackMessage({ type: null, message: '' }), 5000);
  };

  if (loading) {
    return (
      <div
        className="min-h-screen"
        style={{ backgroundColor: "var(--color-background)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div
                    className="rounded-lg h-32"
                    style={{ backgroundColor: "var(--color-muted)" }}
                  ></div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div
                    className="rounded-lg h-48"
                    style={{ backgroundColor: "var(--color-muted)" }}
                  ></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="min-h-screen"
        style={{ backgroundColor: "var(--color-background)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div
            className="border rounded-lg p-6"
            style={{
              backgroundColor: "var(--color-destructive)",
              borderColor: "var(--color-destructive)",
              color: "var(--color-destructive-foreground)",
            }}
          >
            <div className="flex items-center">
              <XCircle className="h-6 w-6 mr-3" />
              <div>
                <h3 className="text-lg font-medium">Dashboard Error</h3>
                <p className="mt-1">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const coreStats = [
    {
      label: "AI Innovations",
      value: total_innovations,
      icon: BarChart3,
      description: "Documented AI projects and solutions",
      color: "var(--color-primary)", // Light Blue
    },
    {
      label: "Research Publications",
      value: total_publications,
      icon: FileText,
      description: "Academic papers and research outputs",
      color: "var(--color-info)", // Teal
    },
    {
      label: "Organizations",
      value: total_organizations,
      icon: Building2,
      description: "Universities, companies, and institutions",
      color: "var(--color-accent)", // Purple
    },
    {
      label: "Verified Contributors",
      value: verified_individuals,
      icon: Users,
      description: "Researchers and innovators",
      color: "var(--color-primary)", // Light Blue
    },
    {
      label: "African Countries",
      value: african_countries_covered,
      icon: Globe,
      description: "Geographic coverage across Africa",
      color: "var(--color-info)", // Teal
    },
    {
      label: "Research Domains",
      value: unique_keywords,
      icon: Hash,
      description: "Unique research topics and applications",
      color: "var(--color-accent)", // Purple
    },
    {
      label: "African Relevance",
      value: `${(avg_african_relevance * 100).toFixed(1)}%`,
      icon: TrendingUp,
      description: "Average African context relevance",
      color: "var(--color-primary)", // Light Blue
    },
    {
      label: "AI Technology Focus",
      value: `${(avg_ai_relevance * 100).toFixed(1)}%`,
      icon: TrendingUp,
      description: "Average AI/ML technology relevance",
      color: "var(--color-info)", // Teal
    },
  ];

  const getStatusColor = (active: boolean) =>
    active ? "var(--color-success)" : "var(--color-muted-foreground)";

  const getStatusIcon = (active: boolean) => (active ? CheckCircle : XCircle);

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      {/* Hero Section */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-1)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
            >
              <Activity className="h-4 w-4 mr-2" />
              Live Dashboard
            </div>

            <Section1Text
              as="h1"
              className="text-4xl md:text-5xl font-bold mb-6"
            >
              Innovation Discovery Dashboard
            </Section1Text>

            <Section1Text
              as="p"
              variant="paragraph"
              className="text-xl max-w-3xl mx-auto mb-8"
            >
              Monitoring systematic documentation of African AI excellence
            </Section1Text>

            <div className="flex items-center justify-center space-x-2 text-sm">
              <Activity
                className="h-4 w-4"
                style={{ color: "var(--color-success)" }}
              />
              <Section1Text as="span" variant="paragraph">
                Last updated: {new Date().toLocaleTimeString()}
              </Section1Text>
            </div>
          </div>
        </div>
      </section>

      {/* Core Statistics */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Section2Text as="h2" className="text-3xl font-bold mb-4">
              Platform Statistics
            </Section2Text>
            <Section2Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-2xl mx-auto"
            >
              Real-time metrics tracking African AI innovation documentation
            </Section2Text>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {coreStats.map((stat, index) => {
              const IconComponent = stat.icon;
              return (
                <div
                  key={index}
                  className="rounded-lg border p-6 hover:shadow-lg hover:scale-105 hover:-translate-y-1 transition-all duration-300 ease-in-out"
                  style={{
                    backgroundColor: "var(--color-card)",
                    borderColor: "var(--color-border)",
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p
                        className="text-sm font-medium mb-1"
                        style={{ color: "var(--color-muted-foreground)" }}
                      >
                        {stat.label}
                      </p>
                      <p
                        className="text-3xl font-bold mb-2"
                        style={{ color: "var(--color-card-foreground)" }}
                      >
                        {typeof stat.value === "number"
                          ? stat.value.toLocaleString()
                          : stat.value}
                      </p>
                      <p
                        className="text-xs"
                        style={{ color: "var(--color-muted-foreground)" }}
                      >
                        {stat.description}
                      </p>
                    </div>
                    <div
                      className="p-3 rounded-lg"
                      style={{
                        backgroundColor: `${stat.color}20`,
                      }}
                    >
                      <IconComponent
                        className="w-6 h-6"
                        style={{ color: stat.color }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ETL Pipeline Status */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-3)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Section3Text as="h2" className="text-3xl font-bold mb-4">
              Data Processing Pipelines
            </Section3Text>
            <Section3Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-2xl mx-auto"
            >
              Monitor and control automated data collection systems
            </Section3Text>
            
            {/* Feedback Message */}
            {feedbackMessage.type && (
              <div
                className="mt-4 p-3 rounded-lg text-sm font-medium max-w-md mx-auto"
                style={{
                  backgroundColor: feedbackMessage.type === 'success' 
                    ? 'var(--color-success)' 
                    : 'var(--color-destructive)',
                  color: feedbackMessage.type === 'success'
                    ? 'var(--color-success-foreground)'
                    : 'var(--color-destructive-foreground)',
                }}
              >
                <div className="flex items-center justify-center">
                  {feedbackMessage.type === 'success' ? (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  ) : (
                    <XCircle className="h-4 w-4 mr-2" />
                  )}
                  {feedbackMessage.message}
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Academic Pipeline */}
            <div
              className="rounded-lg border p-6"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3
                  className="text-lg font-semibold flex items-center"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  <Database
                    className="h-5 w-5 mr-2"
                    style={{ color: "var(--color-primary)" }}
                  />
                  Academic Pipeline
                </h3>
                <button
                  onClick={handleTriggerAcademic}
                  disabled={etlLoading}
                  className="p-2 rounded-lg hover:shadow-md transition-all"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                  title="Trigger Academic Pipeline"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etl_status?.academic_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etl_status?.academic_pipeline_active || false,
                            ),
                          }}
                        />
                      );
                    })()}
                    <span
                      className="ml-1 text-sm"
                      style={{
                        color: getStatusColor(
                          etl_status?.academic_pipeline_active || false,
                        ),
                      }}
                    >
                      {etl_status?.academic_pipeline_active
                        ? "Active"
                        : "Inactive"}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etl_status?.last_academic_run
                      ? new Date(etl_status.last_academic_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Discovers AI research from academic papers, arxiv, and
                    institutional repositories
                  </div>
                </div>
              </div>
            </div>

            {/* News Pipeline */}
            <div
              className="rounded-lg border p-6"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3
                  className="text-lg font-semibold flex items-center"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  <Zap
                    className="h-5 w-5 mr-2"
                    style={{ color: "var(--color-success)" }}
                  />
                  News Pipeline
                </h3>
                <button
                  onClick={handleTriggerNews}
                  disabled={etlLoading}
                  className="p-2 rounded-lg hover:shadow-md transition-all"
                  style={{
                    backgroundColor: "var(--color-success)",
                    color: "var(--color-success-foreground)",
                  }}
                  title="Trigger News Pipeline"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etl_status?.news_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etl_status?.news_pipeline_active || false,
                            ),
                          }}
                        />
                      );
                    })()}
                    <Section3Text
                      as="span"
                      variant="paragraph"
                      className="ml-1 text-sm"
                      style={{
                        color: getStatusColor(
                          etl_status?.news_pipeline_active || false,
                        ),
                      }}
                    >
                      {etl_status?.news_pipeline_active ? "Active" : "Inactive"}
                    </Section3Text>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etl_status?.last_news_run
                      ? new Date(etl_status.last_news_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Monitors RSS feeds and news sources for innovation
                    announcements and project launches
                  </div>
                </div>
              </div>
            </div>

            {/* Discovery Pipeline */}
            <div
              className="rounded-lg border p-6"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3
                  className="text-lg font-semibold flex items-center"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  <RefreshCw
                    className="h-5 w-5 mr-2"
                    style={{ color: "var(--color-accent)" }}
                  />
                  Discovery Pipeline
                </h3>
                <button
                  onClick={handleTriggerDiscovery}
                  disabled={etlLoading}
                  className="p-2 rounded-lg hover:shadow-md transition-all"
                  style={{
                    backgroundColor: "var(--color-accent)",
                    color: "var(--color-accent-foreground)",
                  }}
                  title="Trigger Discovery Search"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etl_status?.serper_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etl_status?.serper_pipeline_active || false,
                            ),
                          }}
                        />
                      );
                    })()}
                    <Section3Text
                      as="span"
                      variant="paragraph"
                      className="ml-1 text-sm"
                      style={{
                        color: getStatusColor(
                          etl_status?.serper_pipeline_active || false,
                        ),
                      }}
                    >
                      {etl_status?.serper_pipeline_active
                        ? "Active"
                        : "Inactive"}
                    </Section3Text>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etl_status?.last_serper_run
                      ? new Date(etl_status.last_serper_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Uses Serper.dev for precision searches and Crawl4AI for
                    project site extraction
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Activity Summary */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-4)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Today's Processing Activity */}
            <div
              className="rounded-lg border p-6"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-accent)",
                borderWidth: "2px",
              }}
            >
              <h3
                className="text-lg font-semibold mb-4 flex items-center"
                style={{ color: "var(--color-card-foreground)" }}
              >
                <Activity
                  className="h-5 w-5 mr-2"
                  style={{ color: "var(--color-accent)" }}
                />
                Today's Activity
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span style={{ color: "var(--color-muted-foreground)" }}>
                    Projects Processed
                  </span>
                  <span
                    className="text-lg font-semibold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etl_status?.total_processed_today || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span style={{ color: "var(--color-muted-foreground)" }}>
                    Processing Errors
                  </span>
                  <div className="flex items-center">
                    {(etl_status?.errors_today || 0) > 0 && (
                      <AlertTriangle
                        className="h-4 w-4 mr-1"
                        style={{ color: "var(--color-destructive)" }}
                      />
                    )}
                    <span
                      className="text-lg font-semibold"
                      style={{
                        color:
                          (etl_status?.errors_today || 0) > 0
                            ? "var(--color-destructive)"
                            : "var(--color-card-foreground)",
                      }}
                    >
                      {etl_status?.errors_today || 0}
                    </span>
                  </div>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Real-time processing statistics reset daily at midnight UTC
                  </div>
                </div>
              </div>
            </div>

            {/* Innovation Archive Summary */}
            <div
              className="rounded-lg border p-6"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-primary)",
                borderWidth: "2px",
              }}
            >
              <h3
                className="text-xl font-bold mb-2 flex items-center"
                style={{ color: "var(--color-card-foreground)" }}
              >
                <Database
                  className="h-5 w-5 mr-2"
                  style={{ color: "var(--color-primary)" }}
                />
                African AI Innovation Archive
              </h3>
              <p
                className="mb-4 text-sm"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                Systematic documentation transforming{" "}
                {african_countries_covered} countries' AI landscape from
                promises to proven innovations
              </p>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {total_innovations}
                  </div>
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Innovations
                  </div>
                </div>
                <div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {total_publications}
                  </div>
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Publications
                  </div>
                </div>
                <div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {african_countries_covered}
                  </div>
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Countries
                  </div>
                </div>
              </div>
              <div
                className="mt-4 pt-4 border-t"
                style={{ borderColor: "var(--color-border)" }}
              >
                <div
                  className="flex justify-between text-xs"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  <span>
                    African Relevance:{" "}
                    {(avg_african_relevance * 100).toFixed(1)}%
                  </span>
                  <span>AI Focus: {(avg_ai_relevance * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
