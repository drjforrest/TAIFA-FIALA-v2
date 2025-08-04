"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  MapPin,
  Calendar,
  Users,
  ExternalLink,
  Star,
  TrendingUp,
  Building2,
  Tag,
  CheckCircle,
  Clock,
  AlertCircle,
  Zap,
  Globe,
  ArrowUpRight,
} from "lucide-react";
import { Section1Text } from "@/components/ui/adaptive-text";

// Production API URL - update this to your actual production backend URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://your-backend-domain.com' // Replace with actual production URL
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

interface SearchParams {
  query: string;
  innovation_type?: string;
  country?: string;
  verification_status?: string;
  funding_min?: number;
  funding_max?: number;
  limit: number;
  offset: number;
}

export default function ExploreDataPage() {
  const [innovations, setInnovations] = useState<Innovation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [searchMetadata, setSearchMetadata] = useState<any>(null);

  // Search and filter state
  const [searchParams, setSearchParams] = useState<SearchParams>({
    query: "",
    limit: 12,
    offset: 0,
  });

  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    innovation_types: [] as string[],
    countries: [] as string[],
    organizations: [] as string[],
  });

  // Debounced search
  const [debouncedQuery, setDebouncedQuery] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchParams.query);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchParams.query]);

  // Fetch innovations with retry logic
  const fetchInnovations = useCallback(async (params: SearchParams, retryCount = 0) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching innovations with params:', params);

      // Check if API URL is configured
      if (!API_BASE_URL || API_BASE_URL.includes("localhost")) {
        console.warn("API not available, using mock data");
        // Provide mock data when API is not available
        setTimeout(() => {
          setInnovations([]);
          setTotalCount(0);
          setFilterOptions({
            innovation_types: ["AI/ML Platform", "Healthcare AI", "FinTech", "AgTech"],
            countries: ["Nigeria", "South Africa", "Kenya", "Ghana", "Egypt"],
            organizations: [],
          });
          setLoading(false);
        }, 500);
        return;
      }

      const queryParams = new URLSearchParams();

      if (params.query) queryParams.append("query", params.query);
      if (params.innovation_type)
        queryParams.append("innovation_type", params.innovation_type);
      if (params.country) queryParams.append("country", params.country);
      if (params.verification_status)
        queryParams.append("verification_status", params.verification_status);
      if (params.funding_min)
        queryParams.append("funding_min", params.funding_min.toString());
      if (params.funding_max)
        queryParams.append("funding_max", params.funding_max.toString());
      queryParams.append("limit", params.limit.toString());
      queryParams.append("offset", params.offset.toString());

      console.log('Fetching innovations with URL:', `${API_BASE_URL}/api/innovations?${queryParams}`);
      
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      // Try direct API call first, fallback to proxy if CORS fails
      let response;
      try {
        response = await fetch(
          `${API_BASE_URL}/api/innovations?${queryParams}`,
          {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            },
            mode: 'cors',
            credentials: 'omit',
            signal: controller.signal,
          }
        );
      } catch (corsError) {
        console.log('CORS error, trying proxy route...', corsError instanceof Error ? corsError.message : corsError);
        // Fallback to Next.js API route as proxy
        response = await fetch(
          `/api/innovations?${queryParams}`,
          {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            },
            signal: controller.signal,
          }
        );
      }
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        // If it's a 500 error, provide a more user-friendly message
        if (response.status === 500) {
          throw new Error(
            "The innovation database is currently unavailable. Please try again later."
          );
        }
        throw new Error(
          `Search failed: ${response.status} ${response.statusText}`,
        );
      }

      const data = await response.json();

      setInnovations(data.innovations || []);
      setTotalCount(data.total || 0);
      
      // Store search metadata for UI indicators
      if (data.search_metadata) {
        setSearchMetadata(data.search_metadata);
      } else {
        setSearchMetadata(null);
      }

      // Update filter options from metadata
      if (data.metadata) {
        setFilterOptions({
          innovation_types: data.metadata.innovation_types || [],
          countries: data.metadata.countries || [],
          organizations: data.metadata.organizations || [],
        });
      }
    } catch (err) {
      console.error("Error fetching innovations:", err);
      
      // Retry logic for network errors
      if (retryCount < 2 && (err instanceof TypeError || (err instanceof DOMException && err.name === 'AbortError'))) {
        console.log(`Retrying request (attempt ${retryCount + 1}/2)...`);
        setTimeout(() => {
          fetchInnovations(params, retryCount + 1);
        }, 1000 * (retryCount + 1)); // Exponential backoff
        return;
      }
      
      // Handle different types of errors with more specific messages
      if (err instanceof DOMException && err.name === 'AbortError') {
        setError(
          "Request timeout: The server is taking too long to respond. Please try again."
        );
      } else if (err instanceof TypeError) {
        if (err.message.includes('fetch')) {
          setError(
            "Network error: Unable to connect to the server. Please check your internet connection and try again."
          );
        } else if (err.message.includes('NetworkError') || err.message.includes('CORS')) {
          setError(
            "CORS error: The server is not properly configured to accept requests from this domain."
          );
        } else {
          setError(`Network error: ${err.message}`);
        }
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load and search updates
  useEffect(() => {
    const params = {
      ...searchParams,
      query: debouncedQuery,
    };
    fetchInnovations(params);
  }, [
    debouncedQuery,
    searchParams.innovation_type,
    searchParams.country,
    searchParams.verification_status,
    searchParams.offset,
    searchParams.funding_min,
    searchParams.funding_max,
    searchParams.limit,
    fetchInnovations,
  ]);

  // Search handlers
  const handleSearchChange = (query: string) => {
    setSearchParams((prev) => ({ ...prev, query, offset: 0 }));
  };

  const handleFilterChange = (
    key: keyof SearchParams,
    value: string | number | undefined,
  ) => {
    setSearchParams((prev) => ({ ...prev, [key]: value, offset: 0 }));
  };

  const handleLoadMore = () => {
    setSearchParams((prev) => ({ ...prev, offset: prev.offset + prev.limit }));
  };

  // Utility functions
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

  const formatFunding = (fundings?: Innovation["fundings"]) => {
    if (!fundings || fundings.length === 0) return null;
    const total = fundings.reduce((sum, f) => sum + (f.amount || 0), 0);
    const currency = fundings[0]?.currency || "USD";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(total);
  };

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
              <Search className="h-4 w-4 mr-2" />
              Innovation Discovery
            </div>

            <Section1Text
              as="h1"
              className="text-4xl md:text-6xl font-bold mb-6 leading-tight"
            >
              Explore AI Innovations
            </Section1Text>

            <Section1Text
              as="p"
              variant="paragraph"
              className="text-xl max-w-3xl mx-auto mb-8"
            >
              Discover documented AI breakthroughs across Africa's innovation
              ecosystem—from verified startups to groundbreaking research
            </Section1Text>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/submit"
                className="px-6 py-3 rounded-lg transition-all duration-200 hover:opacity-90 hover:scale-105 flex items-center justify-center space-x-2"
                style={{
                  backgroundColor: "var(--color-primary)",
                  color: "var(--color-primary-foreground)",
                }}
              >
                <span>Submit Innovation</span>
                <ArrowUpRight className="h-4 w-4" />
              </Link>
              <Link
                href="/methodology"
                className="px-6 py-3 rounded-lg border-2 transition-all duration-200 hover:opacity-90 hover:scale-105 flex items-center justify-center space-x-2"
                style={{
                  borderColor: "var(--color-border)",
                  backgroundColor: "var(--color-card)",
                  color: "var(--color-card-foreground)",
                }}
              >
                <span>Our Methodology</span>
                <TrendingUp className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Search and Filters */}
      <div
        className="py-6"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-6">
            {/* Search Bar with Label */}
            <div>
              <label
                htmlFor="search-input"
                className="block text-sm font-medium mb-2"
                style={{ color: "var(--color-foreground)" }}
              >
                <Search className="inline h-4 w-4 mr-2" />
                Search Innovations
              </label>
              <div className="relative">
                <Search 
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5" 
                  style={{ color: "var(--color-muted-foreground)" }}
                />
                <input
                  id="search-input"
                  type="text"
                  className="w-full pl-10 pr-4 py-3 rounded-lg border-2 focus:ring-2 focus:ring-opacity-50 transition-all duration-200 hover:border-opacity-80"
                  style={{
                    borderColor: "var(--color-border)",
                    backgroundColor: "var(--color-card)",
                    color: "var(--color-card-foreground)",
                  }}
                  placeholder="Search innovations, organizations, technologies..."
                  value={searchParams.query}
                  onChange={(e) => handleSearchChange(e.target.value)}
                />
              </div>
            </div>

            {/* Filters with Labels */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Innovation Type Filter */}
              <div>
                <label
                  htmlFor="innovation-type-select"
                  className="block text-sm font-medium mb-2"
                  style={{ color: "var(--color-foreground)" }}
                >
                  <Tag className="inline h-4 w-4 mr-2" />
                  Innovation Type
                </label>
                <div className="relative">
                  <Tag 
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" 
                    style={{ color: "var(--color-muted-foreground)" }}
                  />
                  <select
                    id="innovation-type-select"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border-2 focus:ring-2 focus:ring-opacity-50 transition-all duration-200 hover:border-opacity-80 appearance-none cursor-pointer"
                    style={{
                      borderColor: "var(--color-border)",
                      backgroundColor: "var(--color-card)",
                      color: "var(--color-card-foreground)",
                    }}
                    value={searchParams.innovation_type || ""}
                    onChange={(e) =>
                      handleFilterChange(
                        "innovation_type",
                        e.target.value || undefined,
                      )
                    }
                  >
                    <option value="">All Innovation Types</option>
                    {filterOptions.innovation_types.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Country Filter */}
              <div>
                <label
                  htmlFor="country-select"
                  className="block text-sm font-medium mb-2"
                  style={{ color: "var(--color-foreground)" }}
                >
                  <Globe className="inline h-4 w-4 mr-2" />
                  Country
                </label>
                <div className="relative">
                  <Globe 
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" 
                    style={{ color: "var(--color-muted-foreground)" }}
                  />
                  <select
                    id="country-select"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border-2 focus:ring-2 focus:ring-opacity-50 transition-all duration-200 hover:border-opacity-80 appearance-none cursor-pointer"
                    style={{
                      borderColor: "var(--color-border)",
                      backgroundColor: "var(--color-card)",
                      color: "var(--color-card-foreground)",
                    }}
                    value={searchParams.country || ""}
                    onChange={(e) =>
                      handleFilterChange("country", e.target.value || undefined)
                    }
                  >
                    <option value="">All Countries</option>
                    {filterOptions.countries.map((country) => (
                      <option key={country} value={country}>
                        {country}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Verification Status Filter */}
              <div>
                <label
                  htmlFor="verification-select"
                  className="block text-sm font-medium mb-2"
                  style={{ color: "var(--color-foreground)" }}
                >
                  <CheckCircle className="inline h-4 w-4 mr-2" />
                  Verification Status
                </label>
                <div className="relative">
                  <CheckCircle 
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" 
                    style={{ color: "var(--color-muted-foreground)" }}
                  />
                  <select
                    id="verification-select"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border-2 focus:ring-2 focus:ring-opacity-50 transition-all duration-200 hover:border-opacity-80 appearance-none cursor-pointer"
                    style={{
                      borderColor: "var(--color-border)",
                      backgroundColor: "var(--color-card)",
                      color: "var(--color-card-foreground)",
                    }}
                    value={searchParams.verification_status || ""}
                    onChange={(e) =>
                      handleFilterChange(
                        "verification_status",
                        e.target.value || undefined,
                      )
                    }
                  >
                    <option value="">All Verification Status</option>
                    <option value="verified">Verified</option>
                    <option value="pending">Under Review</option>
                    <option value="community">Community Validated</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Search Quality Indicator */}
          {searchMetadata && searchParams.query && (
            <div 
              className="flex items-center justify-between text-sm mt-4 p-3 rounded-lg"
              style={{ 
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
                border: "1px solid var(--color-border)"
              }}
            >
              <div className="flex items-center space-x-4">
                {searchMetadata.used_vector_search && (
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span style={{ color: "var(--color-card-foreground)" }}>
                      AI-Powered Search
                    </span>
                  </div>
                )}
                
                {searchMetadata.search_quality && searchMetadata.search_quality !== "n/a" && (
                  <div className="flex items-center space-x-1">
                    <span style={{ color: "var(--color-muted-foreground)" }}>Quality:</span>
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <span
                          key={i}
                          className={`text-xs ${
                            i < Math.round((searchMetadata.avg_relevance_score || 0) * 5)
                              ? "text-yellow-500"
                              : "text-gray-300"
                          }`}
                        >
                          ⭐
                        </span>
                      ))}
                    </div>
                    <span 
                      className="text-xs capitalize ml-1"
                      style={{ color: "var(--color-muted-foreground)" }}
                    >
                      ({searchMetadata.search_quality})
                    </span>
                  </div>
                )}
              </div>
              
              <div className="text-xs" style={{ color: "var(--color-muted-foreground)" }}>
                {searchMetadata.vector_results_count > 0 && (
                  <span>{searchMetadata.vector_results_count} semantic matches</span>
                )}
                {searchMetadata.traditional_results_count > 0 && searchMetadata.vector_results_count > 0 && (
                  <span> + {searchMetadata.traditional_results_count} keyword matches</span>
                )}
                {searchMetadata.traditional_results_count > 0 && searchMetadata.vector_results_count === 0 && (
                  <span>{searchMetadata.traditional_results_count} keyword matches</span>
                )}
              </div>
            </div>
          )}

          {/* Results Summary */}
          <div 
            className="flex items-center justify-between text-sm mt-6 pt-4 border-t"
            style={{ 
              color: "var(--color-muted-foreground)",
              borderColor: "var(--color-border)"
            }}
          >
            <span>
              {loading
                ? "Searching..."
                : `${totalCount.toLocaleString()} innovations found`}
            </span>
            {searchParams.query && (
              <span>
                Results for: <strong style={{ color: "var(--color-card-foreground)" }}>"{searchParams.query}"</strong>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Loading State */}
        {loading && innovations.length === 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="animate-pulse">
                <div
                  className="rounded-lg h-80"
                  style={{ backgroundColor: "var(--color-muted)" }}
                />
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400 mr-3" />
                <div>
                  <h3 className="text-lg font-medium text-red-800 dark:text-red-200">
                    Search Error
                  </h3>
                  <p className="text-red-600 dark:text-red-400 mt-1">{error}</p>
                </div>
              </div>
              <button
                onClick={() => {
                  const params = { ...searchParams, query: debouncedQuery };
                  fetchInnovations(params);
                }}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Innovation Cards */}
        {!loading &&
          !error &&
          innovations.length === 0 &&
          searchParams.query && (
            <div className="text-center py-12">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No innovations found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Try adjusting your search terms or filters to find relevant
                innovations.
              </p>
            </div>
          )}

        {innovations.length > 0 && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
              {innovations.map((innovation) => (
                <div
                  key={innovation.id}
                  className="rounded-lg border shadow-sm hover:shadow-lg hover:scale-105 hover:-translate-y-1 transition-all duration-300 ease-in-out group"
                  style={{ 
                    backgroundColor: "var(--color-card)",
                    borderColor: "var(--color-border)"
                  }}
                >
                  <div className="p-6">
                    {/* Header with verification status */}
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 
                            className="text-xl font-bold transition-colors"
                            style={{ 
                              color: "var(--color-card-foreground)",
                            }}
                          >
                            {innovation.title}
                          </h3>
                          {/* Relevance score indicator for search results */}
                          {searchParams.query && (innovation as any)._relevance_score && (
                            <div className="flex items-center space-x-1">
                              <div className="flex">
                                {[...Array(5)].map((_, i) => (
                                  <span
                                    key={i}
                                    className={`text-xs ${
                                      i < Math.round(((innovation as any)._relevance_score || 0) * 5)
                                        ? "text-yellow-500"
                                        : "text-gray-300"
                                    }`}
                                  >
                                    ⭐
                                  </span>
                                ))}
                              </div>
                              {(innovation as any)._search_source === 'vector' && (
                                <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 px-1 py-0.5 rounded">
                                  AI
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        <div 
                          className="flex items-center space-x-4 text-sm mb-3"
                          style={{ color: "var(--color-muted-foreground)" }}
                        >
                          {innovation.country && (
                            <span className="flex items-center">
                              <MapPin className="h-4 w-4 mr-1" />
                              {innovation.country}
                            </span>
                          )}
                          <span className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {new Date(
                              innovation.creation_date,
                            ).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div
                        className={`flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getVerificationColor(innovation.verification_status)}`}
                      >
                        {getVerificationIcon(innovation.verification_status)}
                        <span className="ml-1 capitalize">
                          {innovation.verification_status}
                        </span>
                      </div>
                    </div>

                    {/* Description */}
                    <p 
                      className="mb-4 line-clamp-3"
                      style={{ color: "var(--color-muted-foreground)" }}
                    >
                      {innovation.description}
                    </p>

                    {/* Innovation Type */}
                    <div className="flex items-center mb-4">
                      <Tag 
                        className="h-4 w-4 mr-2" 
                        style={{ color: "var(--color-primary)" }}
                      />
                      <span 
                        className="text-sm font-medium"
                        style={{ color: "var(--color-primary)" }}
                      >
                        {innovation.innovation_type}
                      </span>
                    </div>

                    {/* Organizations */}
                    {innovation.organizations &&
                      innovation.organizations.length > 0 && (
                        <div className="flex items-center mb-4">
                          <Building2 className="h-4 w-4 text-gray-500 mr-2" />
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {innovation.organizations[0].name}
                            {innovation.organizations.length > 1 && (
                              <span className="text-gray-400">
                                {" "}
                                +{innovation.organizations.length - 1} more
                              </span>
                            )}
                          </span>
                        </div>
                      )}

                    {/* Funding Info */}
                    {innovation.fundings && innovation.fundings.length > 0 && (
                      <div className="flex items-center mb-4">
                        <Zap className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-sm font-medium text-green-600 dark:text-green-400">
                          {formatFunding(innovation.fundings)} funding
                        </span>
                      </div>
                    )}

                    {/* Impact Metrics */}
                    {innovation.impact_metrics && (
                      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        {innovation.impact_metrics.users_reached && (
                          <div className="text-center">
                            <div className="font-semibold text-gray-900 dark:text-white">
                              {innovation.impact_metrics.users_reached.toLocaleString()}
                            </div>
                            <div className="text-gray-500 dark:text-gray-400">
                              Users
                            </div>
                          </div>
                        )}
                        {innovation.impact_metrics.jobs_created && (
                          <div className="text-center">
                            <div className="font-semibold text-gray-900 dark:text-white">
                              {innovation.impact_metrics.jobs_created.toLocaleString()}
                            </div>
                            <div className="text-gray-500 dark:text-gray-400">
                              Jobs
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Footer with CTA */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center space-x-2">
                        {innovation.publications &&
                          innovation.publications.length > 0 && (
                            <span className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                              <ExternalLink className="h-3 w-3 mr-1" />
                              {innovation.publications.length} publication
                              {innovation.publications.length !== 1 ? "s" : ""}
                            </span>
                          )}
                      </div>
                      <Link
                        href={`/innovations/${innovation.id}`}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium transition-colors"
                      >
                        Learn More →
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Load More Button */}
            {innovations.length < totalCount && (
              <div className="text-center">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="px-6 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                >
                  {loading
                    ? "Loading..."
                    : `Load More (${totalCount - innovations.length} remaining)`}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
