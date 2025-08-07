"use client";

import RealTimeAnalytics from "@/components/Dashboard/RealTimeAnalytics";
import PublicationsTable from "@/components/Dashboard/PublicationsTable";
import {
  ResearchToInnovationPipeline,
  CollaborationHeatMap,
  TechnologyAdoptionCurves
} from "@/components/Dashboard/DataInsights";
import {
  Section1Text,
  Section2Text,
  Section3Text
} from "@/components/ui/adaptive-text";
import { useDashboard, useETLMonitoring } from "@/hooks/useDashboard";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Building2,
  CheckCircle,
  Clock,
  Database,
  FileText,
  Globe,
  Hash,
  Play,
  RefreshCw,
  Rss,
  TrendingUp,
  Users,
  XCircle,
  Zap,
  Network,
  Brain,
  Target
} from "lucide-react";
import { useState } from "react";

export default function DashboardStats() {
  const [activeTab, setActiveTab] = useState<'monitoring' | 'analytics' | 'pipeline' | 'collaboration' | 'technology' | 'rss'>('monitoring');
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
    loading,
    error,
  } = useDashboard();

  const {
    status: etlStatus,
    health: etlHealth,
    triggerAcademicPipeline,
    triggerNewsPipeline,
    triggerSerperSearch,
    triggerEnrichment,
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

  const handleTriggerEnrichment = async () => {
    setFeedbackMessage({ type: null, message: '' });
    const result = await triggerEnrichment();
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

            <p 
              className="text-xl max-w-3xl mx-auto mb-8"
              style={{ color: "var(--color-text-section-subheading)" }}
            >
              Monitoring systematic documentation of African AI excellence
            </p>

            <div className="flex items-center justify-center space-x-2 text-sm">
              <Activity
                className="h-4 w-4"
                style={{ color: "var(--color-success)" }}
              />
              <span style={{ color: "var(--color-text-section-subheading)" }}>
                Last updated: {new Date().toLocaleTimeString()}
              </span>
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
            <p 
              className="text-lg max-w-2xl mx-auto"
              style={{ color: "var(--color-text-section-subheading)" }}
            >
              Real-time metrics tracking African AI innovation documentation
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {coreStats.map((stat, index) => {
              const IconComponent = stat.icon;
              return (
                <div
                  key={index}
                  className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out"
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
                        style={{ color: "var(--color-text-card-paragraph)" }}
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

      {/* Tab Navigation */}
      <section
        className="py-4"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="border-b" style={{ borderColor: "var(--color-border)" }}>
            <nav className="flex space-x-4">
              <button
                onClick={() => setActiveTab('monitoring')}
                className="flex items-center transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
                style={{
                  padding: "12px 20px",
                  backgroundColor: activeTab === 'monitoring' ? 'var(--color-primary)' : 'var(--color-background)',
                  color: activeTab === 'monitoring' ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  border: `1px solid ${activeTab === 'monitoring' ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  boxShadow: activeTab === 'monitoring' ? "0 2px 6px rgba(0, 0, 0, 0.12)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'monitoring') {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'monitoring') {
                    e.currentTarget.style.backgroundColor = 'var(--color-background)';
                    e.currentTarget.style.color = 'var(--color-muted-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
              >
                <Activity className="h-4 w-4 mr-2" />
                ETL Monitoring
              </button>
              <button
                onClick={() => setActiveTab('pipeline')}
                className="flex items-center transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
                style={{
                  padding: "12px 20px",
                  backgroundColor: activeTab === 'pipeline' ? 'var(--color-primary)' : 'var(--color-background)',
                  color: activeTab === 'pipeline' ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  border: `1px solid ${activeTab === 'pipeline' ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  boxShadow: activeTab === 'pipeline' ? "0 2px 6px rgba(0, 0, 0, 0.12)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'pipeline') {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'pipeline') {
                    e.currentTarget.style.backgroundColor = 'var(--color-background)';
                    e.currentTarget.style.color = 'var(--color-muted-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Research Pipeline
              </button>
              <button
                onClick={() => setActiveTab('collaboration')}
                className="flex items-center transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
                style={{
                  padding: "12px 20px",
                  backgroundColor: activeTab === 'collaboration' ? 'var(--color-primary)' : 'var(--color-background)',
                  color: activeTab === 'collaboration' ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  border: `1px solid ${activeTab === 'collaboration' ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  boxShadow: activeTab === 'collaboration' ? "0 2px 6px rgba(0, 0, 0, 0.12)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'collaboration') {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'collaboration') {
                    e.currentTarget.style.backgroundColor = 'var(--color-background)';
                    e.currentTarget.style.color = 'var(--color-muted-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
              >
                <Network className="h-4 w-4 mr-2" />
                Collaboration
              </button>
              <button
                onClick={() => setActiveTab('technology')}
                className="flex items-center transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
                style={{
                  padding: "12px 20px",
                  backgroundColor: activeTab === 'technology' ? 'var(--color-primary)' : 'var(--color-background)',
                  color: activeTab === 'technology' ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  border: `1px solid ${activeTab === 'technology' ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  boxShadow: activeTab === 'technology' ? "0 2px 6px rgba(0, 0, 0, 0.12)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'technology') {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'technology') {
                    e.currentTarget.style.backgroundColor = 'var(--color-background)';
                    e.currentTarget.style.color = 'var(--color-muted-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
              >
                <Target className="h-4 w-4 mr-2" />
                Technology Trends
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className="flex items-center transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
                style={{
                  padding: "12px 20px",
                  backgroundColor: activeTab === 'analytics' ? 'var(--color-primary)' : 'var(--color-background)',
                  color: activeTab === 'analytics' ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  border: `1px solid ${activeTab === 'analytics' ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  boxShadow: activeTab === 'analytics' ? "0 2px 6px rgba(0, 0, 0, 0.12)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'analytics') {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'analytics') {
                    e.currentTarget.style.backgroundColor = 'var(--color-background)';
                    e.currentTarget.style.color = 'var(--color-muted-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Real-time Analytics
              </button>
              <button
                onClick={() => setActiveTab('rss')}
                className="flex items-center transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
                style={{
                  padding: "12px 20px",
                  backgroundColor: activeTab === 'rss' ? 'var(--color-primary)' : 'var(--color-background)',
                  color: activeTab === 'rss' ? 'var(--color-primary-foreground)' : 'var(--color-muted-foreground)',
                  border: `1px solid ${activeTab === 'rss' ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "500",
                  boxShadow: activeTab === 'rss' ? "0 2px 6px rgba(0, 0, 0, 0.12)" : "0 1px 3px rgba(0, 0, 0, 0.1)",
                  cursor: "pointer",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'rss') {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary)';
                    e.currentTarget.style.color = 'var(--color-primary-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'rss') {
                    e.currentTarget.style.backgroundColor = 'var(--color-background)';
                    e.currentTarget.style.color = 'var(--color-muted-foreground)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }
                }}
              >
                <Rss className="h-4 w-4 mr-2" />
                RSS Feed
              </button>
            </nav>
          </div>
        </div>
      </section>

      {/* Tab Content - ETL Monitoring */}
      {activeTab === 'monitoring' && (
        <>
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
            <p 
              className="text-lg max-w-2xl mx-auto"
              style={{ color: "var(--color-text-section-subheading)" }}
            >
              Monitor and control automated data collection systems
            </p>
            
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

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
            {/* Academic Pipeline */}
            <div
              className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out"
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
                  className="p-4 rounded-lg hover:shadow-lg hover:scale-110 transition-all duration-200 ease-in-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                  title="Trigger Academic Pipeline"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-6 w-6 animate-spin" />
                  ) : (
                    <Play className="h-6 w-6" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etlStatus?.academic_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etlStatus?.academic_pipeline_active || false,
                            ),
                          }}
                        />
                      );
                    })()}
                    <span
                      className="ml-1 text-sm"
                      style={{
                        color: getStatusColor(
                          etlStatus?.academic_pipeline_active || false,
                        ),
                      }}
                    >
                      {etlStatus?.academic_pipeline_active
                        ? "Active"
                        : "Inactive"}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etlStatus?.last_academic_run
                      ? new Date(etlStatus.last_academic_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                {/* Metrics Display */}
                {etlStatus?.academic_pipeline_active && (
                  <div className="space-y-2 pt-2 border-t" style={{ borderColor: "var(--color-border)" }}>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Batch Size</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus?.metrics?.batch_size || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Duplicates Removed</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus?.metrics?.duplicates_removed || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Processing Time</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus?.metrics?.processing_time_ms ? `${etlStatus.metrics.processing_time_ms}ms` : '0ms'}
                      </span>
                    </div>
                  </div>
                )}
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Discovers AI research from academic papers, arxiv, and
                    institutional repositories
                  </div>
                </div>
              </div>
            </div>

            {/* News Pipeline */}
            <div
              className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out"
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
                  className="p-4 rounded-lg hover:shadow-lg hover:scale-110 transition-all duration-200 ease-in-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: "var(--color-success)",
                    color: "var(--color-success-foreground)",
                  }}
                  title="Trigger News Pipeline"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-6 w-6 animate-spin" />
                  ) : (
                    <Play className="h-6 w-6" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etlStatus?.news_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etlStatus?.news_pipeline_active || false,
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
                          etlStatus?.news_pipeline_active || false,
                        ),
                      }}
                    >
                      {etlStatus?.news_pipeline_active ? "Active" : "Inactive"}
                    </Section3Text>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etlStatus?.last_news_run
                      ? new Date(etlStatus.last_news_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Monitors RSS feeds and news sources for innovation
                    announcements and project launches
                  </div>
                </div>
              </div>
            </div>

            {/* Discovery Pipeline */}
            <div
              className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out"
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
                  className="p-4 rounded-lg hover:shadow-lg hover:scale-110 transition-all duration-200 ease-in-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: "var(--color-accent)",
                    color: "var(--color-accent-foreground)",
                  }}
                  title="Trigger Discovery Search"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-6 w-6 animate-spin" />
                  ) : (
                    <Play className="h-6 w-6" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etlStatus?.serper_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etlStatus?.serper_pipeline_active || false,
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
                          etlStatus?.serper_pipeline_active || false,
                        ),
                      }}
                    >
                      {etlStatus?.serper_pipeline_active
                        ? "Active"
                        : "Inactive"}
                    </Section3Text>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etlStatus?.last_serper_run
                      ? new Date(etlStatus.last_serper_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Uses Serper.dev for precision searches and Crawl4AI for
                    project site extraction
                  </div>
                </div>
              </div>
            </div>

            {/* AI Enrichment Pipeline */}
            <div
              className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out relative"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              {/* "Please Wait" HUD Overlay - Only show when enrichment is active and processing */}
              {etlStatus?.enrichment_pipeline_active && etlLoading && (
                <div
                  className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-yellow-500/10 rounded-lg flex items-center justify-center backdrop-blur-sm"
                  style={{
                    backgroundColor: "rgba(251, 146, 60, 0.05)",
                    backdropFilter: "blur(2px)",
                  }}
                >
                  <div
                    className="text-center p-4 rounded-lg border-2 border-dashed"
                    style={{
                      borderColor: "var(--color-orange-500)",
                      backgroundColor: "rgba(251, 146, 60, 0.1)",
                    }}
                  >
                    <Clock className="h-8 w-8 mx-auto mb-2" style={{ color: "var(--color-orange-500)" }} />
                    <p className="text-sm font-medium" style={{ color: "var(--color-orange-500)" }}>
                      Please Wait Patiently
                    </p>
                    <p className="text-xs mt-1" style={{ color: "var(--color-muted-foreground)" }}>
                      Processing enrichment...
                    </p>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between mb-4">
                <h3
                  className="text-lg font-semibold flex items-center"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  <Zap
                    className="h-5 w-5 mr-2"
                    style={{ color: "var(--color-orange-500)" }}
                  />
                  AI Enrichment
                </h3>
                <button
                  onClick={handleTriggerEnrichment}
                  disabled={etlLoading}
                  className="p-4 rounded-lg hover:shadow-lg hover:scale-110 transition-all duration-200 ease-in-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: "var(--color-orange-500)",
                    color: "var(--color-white)",
                  }}
                  title="Trigger AI Intelligence Enrichment"
                >
                  {etlLoading ? (
                    <RefreshCw className="h-6 w-6 animate-spin" />
                  ) : (
                    <Play className="h-6 w-6" />
                  )}
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Status
                  </span>
                  <div className="flex items-center">
                    {(() => {
                      const StatusIcon = getStatusIcon(
                        etlStatus?.enrichment_pipeline_active || false,
                      );
                      return (
                        <StatusIcon
                          className="h-4 w-4"
                          style={{
                            color: getStatusColor(
                              etlStatus?.enrichment_pipeline_active || false,
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
                          etlStatus?.enrichment_pipeline_active || false,
                        ),
                      }}
                    >
                      {etlStatus?.enrichment_pipeline_active ? "Active" : "Inactive"}
                    </Section3Text>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Last Run
                  </span>
                  <span
                    className="text-sm"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etlStatus?.last_enrichment_run
                      ? new Date(etlStatus.last_enrichment_run).toLocaleString()
                      : "Never"}
                  </span>
                </div>
                {/* Metrics Display */}
                {etlStatus?.pipeline_metrics?.enrichment_pipeline && (
                  <div className="space-y-2 pt-2 border-t" style={{ borderColor: "var(--color-border)" }}>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Batch Size</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus.pipeline_metrics.enrichment_pipeline.batch_size}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Duplicates Removed</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus.pipeline_metrics.enrichment_pipeline.duplicates_removed}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Processing Time</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus.pipeline_metrics.enrichment_pipeline.processing_time_ms}ms
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span style={{ color: "var(--color-text-card-paragraph)" }}>Success Rate</span>
                      <span style={{ color: "var(--color-card-foreground)" }}>
                        {etlStatus.pipeline_metrics.enrichment_pipeline.success_rate.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                )}
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Uses AI (Perplexity, OpenAI, etc.) for intelligent analysis and
                    comprehensive insights on African AI ecosystem
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
              className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out"
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
                  <span style={{ color: "var(--color-text-card-paragraph)" }}>
                    Projects Processed
                  </span>
                  <span
                    className="text-lg font-semibold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    {etlStatus?.total_processed_today || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span style={{ color: "var(--color-text-card-paragraph)" }}>
                    Processing Errors
                  </span>
                  <div className="flex items-center">
                    {(etlStatus?.errors_today || 0) > 0 && (
                      <AlertTriangle
                        className="h-4 w-4 mr-1"
                        style={{ color: "var(--color-destructive)" }}
                      />
                    )}
                    <span
                      className="text-lg font-semibold"
                      style={{
                        color:
                          (etlStatus?.errors_today || 0) > 0
                            ? "var(--color-destructive)"
                            : "var(--color-card-foreground)",
                      }}
                    >
                      {etlStatus?.errors_today || 0}
                    </span>
                  </div>
                </div>
                <div
                  className="pt-2 border-t"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div
                    className="text-xs"
                    style={{ color: "var(--color-text-card-paragraph)" }}
                  >
                    Real-time processing statistics reset daily at midnight UTC
                  </div>
                </div>
              </div>
            </div>

            {/* Innovation Archive Summary */}
            <div
              className="rounded-lg border p-6 hover:shadow-lg transition-all duration-300 ease-in-out"
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
                style={{ color: "var(--color-text-card-paragraph)" }}
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
                    style={{ color: "var(--color-text-card-paragraph)" }}
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
                    style={{ color: "var(--color-text-card-paragraph)" }}
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
                    style={{ color: "var(--color-text-card-paragraph)" }}
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
                  style={{ color: "var(--color-text-card-paragraph)" }}
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
        </>
      )}

      {/* Tab Content - Real-time Analytics */}
      {activeTab === 'analytics' && (
        <section
          className="py-16"
          style={{ backgroundColor: "var(--color-background-section-3)" }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <RealTimeAnalytics />
          </div>
        </section>
      )}

      {/* Tab Content - Research Pipeline */}
      {activeTab === 'pipeline' && (
        <section
          className="py-16"
          style={{ backgroundColor: "var(--color-background-section-3)" }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <Section3Text as="h2" className="text-3xl font-bold mb-4">
                Research to Innovation Pipeline
              </Section3Text>
              <p 
                className="text-lg max-w-2xl mx-auto opacity-70"
                style={{ color: "var(--color-text-section-subheading)" }}
              >
                Tracking knowledge flows from academic research to commercial innovations across Africa
              </p>
            </div>
            <ResearchToInnovationPipeline />
          </div>
        </section>
      )}

      {/* Tab Content - Collaboration HeatMap */}
      {activeTab === 'collaboration' && (
        <section
          className="py-16"
          style={{ backgroundColor: "var(--color-background-section-3)" }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <Section3Text as="h2" className="text-3xl font-bold mb-4">
                African AI Collaboration Network
              </Section3Text>
              <p 
                className="text-lg max-w-2xl mx-auto opacity-70"
                style={{ color: "var(--color-text-section-subheading)" }}
              >
                Institutional connections and collaboration patterns across African research institutes
              </p>
            </div>
            <CollaborationHeatMap />
          </div>
        </section>
      )}

      {/* Tab Content - Technology Trends */}
      {activeTab === 'technology' && (
        <section
          className="py-16"
          style={{ backgroundColor: "var(--color-background-section-3)" }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <Section3Text as="h2" className="text-3xl font-bold mb-4">
                AI Technology Adoption Trends
              </Section3Text>
              <p 
                className="text-lg max-w-2xl mx-auto opacity-70"
                style={{ color: "var(--color-text-section-subheading)" }}
              >
                Technology lifecycle analysis and adoption patterns across African AI ecosystem
              </p>
            </div>
            <TechnologyAdoptionCurves />
          </div>
        </section>
      )}

      {/* Tab Content - RSS Feed */}
      {activeTab === 'rss' && (
        <section
          className="py-16"
          style={{ backgroundColor: "var(--color-background-section-3)" }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <Section3Text as="h2" className="text-3xl font-bold mb-4">
                Research Publications Feed
              </Section3Text>
              <p 
                className="text-lg max-w-2xl mx-auto opacity-70"
                style={{ color: "var(--color-text-section-subheading)" }}
              >
                Live feed of African AI research publications and academic papers
              </p>
            </div>
            <PublicationsTable />
          </div>
        </section>
      )}
    </div>
  );
}
