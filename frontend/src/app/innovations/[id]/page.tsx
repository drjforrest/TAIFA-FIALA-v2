"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  MapPin,
  Calendar,
  Users,
  ExternalLink,
  CheckCircle,
  Clock,
  AlertCircle,
  Building2,
  Tag,
  Zap,
  TrendingUp,
  Globe,
  DollarSign,
} from "lucide-react";
import { Section1Text } from "@/components/ui/adaptive-text";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://your-backend-domain.com' 
    : "http://localhost:8000"
  );

interface Innovation {
  id: string;
  title: string;
  description: string;
  innovation_type: string;
  creation_date: string;
  verification_status: "verified" | "pending" | "community";
  visibility: "public" | "private";
  country?: string;
  website_url?: string;
  github_url?: string;
  demo_url?: string;
  source_url?: string;
  organizations?: Array<{
    id: string;
    name: string;
    organization_type: string;
  }>;
  individuals?: Array<{
    id: string;
    name: string;
    role: string;
  }>;
  fundings?: Array<{
    amount: number;
    currency: string;
    funding_type: string;
    funder_name: string;
  }>;
  publications?: Array<{
    title: string;
    url?: string;
    publication_type: string;
  }>;
  tags?: string[];
  impact_metrics?: {
    users_reached?: number;
    revenue_generated?: number;
    jobs_created?: number;
  };
}

export default function InnovationDetailPage() {
  const params = useParams();
  const id = params.id as string;
  
  const [innovation, setInnovation] = useState<Innovation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchInnovation = async () => {
      try {
        setLoading(true);
        setError(null);

        // Since the backend doesn't support individual innovation endpoints,
        // we'll fetch all innovations and filter by ID
        let response;
        try {
          response = await fetch(
            `${API_BASE_URL}/api/innovations?limit=100`,
            {
              method: 'GET',
              headers: {
                'Accept': 'application/json',
              },
              mode: 'cors',
              credentials: 'omit',
            }
          );
        } catch (corsError) {
          console.log('CORS error, trying proxy route...', corsError instanceof Error ? corsError.message : corsError);
          // Fallback to Next.js API route as proxy
          response = await fetch(`/api/innovations?limit=100`);
        }

        if (!response.ok) {
          throw new Error(`Failed to fetch innovations: ${response.status}`);
        }

        const data = await response.json();
        const foundInnovation = data.innovations?.find((inn: Innovation) => inn.id === id);
        
        if (!foundInnovation) {
          throw new Error("Innovation not found");
        }
        
        setInnovation(foundInnovation);
      } catch (err) {
        console.error("Error fetching innovation:", err);
        setError(err instanceof Error ? err.message : "Failed to load innovation");
      } finally {
        setLoading(false);
      }
    };

    fetchInnovation();
  }, [id]);

  const getVerificationColor = (status: string) => {
    switch (status) {
      case "verified":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      case "community":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  const getVerificationIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <CheckCircle className="h-4 w-4" />;
      case "pending":
        return <Clock className="h-4 w-4" />;
      case "community":
        return <Users className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };


  if (loading) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: "var(--color-background)" }}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded mb-4"></div>
            <div className="h-64 bg-gray-300 rounded mb-6"></div>
            <div className="space-y-4">
              <div className="h-4 bg-gray-300 rounded"></div>
              <div className="h-4 bg-gray-300 rounded"></div>
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: "var(--color-background)" }}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="flex items-center">
              <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400 mr-3" />
              <div>
                <h3 className="text-lg font-medium text-red-800 dark:text-red-200">
                  Error Loading Innovation
                </h3>
                <p className="text-red-600 dark:text-red-400 mt-1">{error}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                href="/innovations"
                className="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Innovations
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!innovation) {
    return null;
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: "var(--color-background)" }}>
      {/* Header */}
      <div 
        className="py-8"
        style={{ backgroundColor: "var(--color-background-section-1)" }}
      >
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link
            href="/innovations"
            className="inline-flex items-center text-sm mb-6 hover:opacity-70 transition-opacity"
            style={{ color: "var(--color-muted-foreground)" }}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Innovations
          </Link>

          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <Section1Text
                as="h1"
                className="text-3xl md:text-4xl font-bold mb-4"
              >
                {innovation.title}
              </Section1Text>
              
              <div className="flex items-center space-x-4 text-sm mb-4" style={{ color: "var(--color-muted-foreground)" }}>
                {innovation.country && (
                  <span className="flex items-center">
                    <MapPin className="h-4 w-4 mr-1" />
                    {innovation.country}
                  </span>
                )}
                <span className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {new Date(innovation.creation_date).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div
              className={`flex items-center px-3 py-1 rounded-full text-sm font-semibold ${getVerificationColor(innovation.verification_status)}`}
            >
              {getVerificationIcon(innovation.verification_status)}
              <span className="ml-1 capitalize">
                {innovation.verification_status}
              </span>
            </div>
          </div>

          <div className="flex items-center mb-4">
            <Tag className="h-5 w-5 mr-2" style={{ color: "var(--color-primary)" }} />
            <span className="text-lg font-medium" style={{ color: "var(--color-primary)" }}>
              {innovation.innovation_type}
            </span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <div 
              className="rounded-lg border p-6"
              style={{ 
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)"
              }}
            >
              <h2 className="text-xl font-semibold mb-4" style={{ color: "var(--color-card-foreground)" }}>
                Description
              </h2>
              <div 
                className="prose prose-gray dark:prose-invert max-w-none"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                {innovation.description.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-4">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>

            {/* Links & Resources */}
            {(innovation.website_url || innovation.github_url || innovation.demo_url || innovation.source_url) && (
              <div 
                className="rounded-lg border p-6"
                style={{ 
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)"
                }}
              >
                <h2 className="text-xl font-semibold mb-4" style={{ color: "var(--color-card-foreground)" }}>
                  Links & Resources
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {innovation.website_url && (
                    <a 
                      href={innovation.website_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center p-3 rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/10 hover:bg-blue-100 dark:hover:bg-blue-900/20 transition-colors"
                    >
                      <Globe className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-3" />
                      <div>
                        <div className="font-medium text-blue-800 dark:text-blue-300">Website</div>
                        <div className="text-sm text-blue-600 dark:text-blue-400">Visit project website</div>
                      </div>
                    </a>
                  )}
                  {innovation.github_url && (
                    <a 
                      href={innovation.github_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/10 hover:bg-gray-100 dark:hover:bg-gray-900/20 transition-colors"
                    >
                      <ExternalLink className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-3" />
                      <div>
                        <div className="font-medium text-gray-800 dark:text-gray-300">GitHub</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">View source code</div>
                      </div>
                    </a>
                  )}
                  {innovation.demo_url && (
                    <a 
                      href={innovation.demo_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center p-3 rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/10 hover:bg-green-100 dark:hover:bg-green-900/20 transition-colors"
                    >
                      <ExternalLink className="h-5 w-5 text-green-600 dark:text-green-400 mr-3" />
                      <div>
                        <div className="font-medium text-green-800 dark:text-green-300">Live Demo</div>
                        <div className="text-sm text-green-600 dark:text-green-400">Try the application</div>
                      </div>
                    </a>
                  )}
                  {innovation.source_url && (
                    <a 
                      href={innovation.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center p-3 rounded-lg border border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/10 hover:bg-purple-100 dark:hover:bg-purple-900/20 transition-colors"
                    >
                      <ExternalLink className="h-5 w-5 text-purple-600 dark:text-purple-400 mr-3" />
                      <div>
                        <div className="font-medium text-purple-800 dark:text-purple-300">Original Source</div>
                        <div className="text-sm text-purple-600 dark:text-purple-400">View original article</div>
                      </div>
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Publications */}
            {innovation.publications && innovation.publications.length > 0 && (
              <div 
                className="rounded-lg border p-6"
                style={{ 
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)"
                }}
              >
                <h2 className="text-xl font-semibold mb-4" style={{ color: "var(--color-card-foreground)" }}>
                  Publications
                </h2>
                <div className="space-y-3">
                  {innovation.publications.map((publication, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <ExternalLink className="h-4 w-4 mt-1 text-blue-600" />
                      <div className="flex-1">
                        {publication.url ? (
                          <a
                            href={publication.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block hover:opacity-80 transition-opacity"
                          >
                            <h3 className="font-medium text-blue-600 dark:text-blue-400 hover:underline" style={{ color: "var(--color-primary)" }}>
                              {publication.title}
                            </h3>
                            <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                              {publication.publication_type}
                            </p>
                          </a>
                        ) : (
                          <div>
                            <h3 className="font-medium" style={{ color: "var(--color-card-foreground)" }}>
                              {publication.title}
                            </h3>
                            <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                              {publication.publication_type}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Organizations */}
            {innovation.organizations && innovation.organizations.length > 0 && (
              <div 
                className="rounded-lg border p-6"
                style={{ 
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)"
                }}
              >
                <h3 className="text-lg font-semibold mb-4 flex items-center" style={{ color: "var(--color-card-foreground)" }}>
                  <Building2 className="h-5 w-5 mr-2" />
                  Organizations
                </h3>
                <div className="space-y-3">
                  {innovation.organizations.map((org) => (
                    <div key={org.id}>
                      <h4 className="font-medium" style={{ color: "var(--color-card-foreground)" }}>
                        {org.name}
                      </h4>
                      <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                        {org.organization_type}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Funding */}
            {innovation.fundings && innovation.fundings.length > 0 && (
              <div 
                className="rounded-lg border p-6"
                style={{ 
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)"
                }}
              >
                <h3 className="text-lg font-semibold mb-4 flex items-center" style={{ color: "var(--color-card-foreground)" }}>
                  <DollarSign className="h-5 w-5 mr-2" />
                  Funding
                </h3>
                <div className="space-y-3">
                  {innovation.fundings.map((funding, index) => (
                    <div key={index}>
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-green-600">
                          {new Intl.NumberFormat("en-US", {
                            style: "currency",
                            currency: funding.currency || "USD",
                          }).format(funding.amount)}
                        </span>
                        <span className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                          {funding.funding_type}
                        </span>
                      </div>
                      <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                        {funding.funder_name}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Impact Metrics */}
            {innovation.impact_metrics && Object.keys(innovation.impact_metrics).length > 0 && (
              <div 
                className="rounded-lg border p-6"
                style={{ 
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)"
                }}
              >
                <h3 className="text-lg font-semibold mb-4 flex items-center" style={{ color: "var(--color-card-foreground)" }}>
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Impact Metrics
                </h3>
                <div className="space-y-4">
                  {innovation.impact_metrics.users_reached && (
                    <div className="text-center">
                      <div className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                        {innovation.impact_metrics.users_reached.toLocaleString()}
                      </div>
                      <div className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                        Users Reached
                      </div>
                    </div>
                  )}
                  {innovation.impact_metrics.jobs_created && (
                    <div className="text-center">
                      <div className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                        {innovation.impact_metrics.jobs_created.toLocaleString()}
                      </div>
                      <div className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                        Jobs Created
                      </div>
                    </div>
                  )}
                  {innovation.impact_metrics.revenue_generated && (
                    <div className="text-center">
                      <div className="text-2xl font-bold" style={{ color: "var(--color-card-foreground)" }}>
                        {new Intl.NumberFormat("en-US", {
                          style: "currency",
                          currency: "USD",
                          notation: "compact",
                        }).format(innovation.impact_metrics.revenue_generated)}
                      </div>
                      <div className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
                        Revenue Generated
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}