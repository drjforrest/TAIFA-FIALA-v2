"use client";

import { useState } from "react";
import { Button, Card } from "@/components/ui";
import {
  Search,
  Filter,
  Star,
  Clock,
  Users,
  CheckCircle,
  AlertTriangle,
  Eye,
  ExternalLink,
  MessageCircle,
} from "lucide-react";
import { Section1Text, Section2Text } from "@/components/ui/adaptive-text";

interface PendingInnovation {
  id: string;
  title: string;
  description: string;
  innovationType: string;
  country: string;
  organization: string;
  submittedDate: string;
  submitterName: string;
  evidence: string[];
  communityVotes: {
    positive: number;
    negative: number;
    neutral: number;
  };
  expertReviews: number;
  status: "pending" | "under_review" | "verified" | "needs_more_info";
}

const mockPendingInnovations: PendingInnovation[] = [
  {
    id: "1",
    title: "Solar-Powered IoT Sensors for Smart Agriculture",
    description:
      "Low-cost sensor network for monitoring soil moisture, temperature, and crop health in remote farming areas.",
    innovationType: "AgriTech",
    country: "Kenya",
    organization: "AgriSense Solutions",
    submittedDate: "2024-01-15",
    submitterName: "Dr. Amina Hassan",
    evidence: [
      "deployment_photos.pdf",
      "impact_metrics.xlsx",
      "farmer_testimonials.mp4",
    ],
    communityVotes: { positive: 23, negative: 2, neutral: 5 },
    expertReviews: 2,
    status: "under_review",
  },
  {
    id: "2",
    title: "AI-Powered Mental Health Chatbot in Swahili",
    description:
      "Conversational AI providing mental health support and resources in local languages for underserved communities.",
    innovationType: "HealthTech",
    country: "Tanzania",
    organization: "Afya Digital",
    submittedDate: "2024-01-20",
    submitterName: "James Mwangi",
    evidence: ["app_screenshots.pdf", "user_feedback.docx", "demo_video.mp4"],
    communityVotes: { positive: 18, negative: 1, neutral: 3 },
    expertReviews: 1,
    status: "pending",
  },
  {
    id: "3",
    title: "Blockchain Supply Chain for Coffee Farmers",
    description:
      "Transparent supply chain tracking system helping small-scale coffee farmers get fair prices and direct market access.",
    innovationType: "FinTech",
    country: "Ethiopia",
    organization: "CoffeeCare Technologies",
    submittedDate: "2024-01-25",
    submitterName: "Sara Tekle",
    evidence: ["blockchain_architecture.pdf", "farmer_onboarding.xlsx"],
    communityVotes: { positive: 15, negative: 4, neutral: 8 },
    expertReviews: 0,
    status: "needs_more_info",
  },
];

export default function VerifyPage() {
  const [innovations] = useState<PendingInnovation[]>(mockPendingInnovations);
  const [selectedInnovation, setSelectedInnovation] =
    useState<PendingInnovation | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "var(--color-green-600)";
      case "under_review":
        return "var(--color-blue-600)";
      case "pending":
        return "var(--color-yellow-600)";
      case "needs_more_info":
        return "var(--color-orange-600)";
      default:
        return "var(--color-gray-500)";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <CheckCircle className="h-4 w-4" />;
      case "under_review":
        return <Eye className="h-4 w-4" />;
      case "pending":
        return <Clock className="h-4 w-4" />;
      case "needs_more_info":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const filteredInnovations = innovations.filter((innovation) => {
    const matchesSearch =
      innovation.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      innovation.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !filterStatus || innovation.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const inputStyles = {
    width: "100%",
    padding: "var(--spacing-md)",
    borderRadius: "var(--radius-md)",
    border: "1px solid var(--color-border)",
    backgroundColor: "var(--color-input)",
    color: "var(--color-foreground)",
    fontSize: "1rem",
  };

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-muted)" }}
    >
      {/* Header */}
      <div
        style={{
          backgroundColor: "var(--color-card)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-between items-center">
            <div>
              <h1
                className="text-3xl font-bold"
                style={{ color: "var(--color-foreground)" }}
              >
                Verification & Showcase
              </h1>
              <p style={{ color: "var(--color-muted-foreground)" }}>
                Help verify African AI innovations through community review
              </p>
            </div>
            <div className="flex space-x-4">
              <Button variant="outline">
                <Users className="h-4 w-4 mr-2" />
                Become Expert Reviewer
              </Button>
              <Button>
                <Star className="h-4 w-4 mr-2" />
                Review Innovations
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Verification Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="text-center">
            <div
              className="text-2xl font-bold"
              style={{ color: "var(--color-blue-600)" }}
            >
              {innovations.filter((i) => i.status === "pending").length}
            </div>
            <div style={{ color: "var(--color-muted-foreground)" }}>
              Pending Review
            </div>
          </Card>
          <Card className="text-center">
            <div
              className="text-2xl font-bold"
              style={{ color: "var(--color-yellow-600)" }}
            >
              {innovations.filter((i) => i.status === "under_review").length}
            </div>
            <div style={{ color: "var(--color-muted-foreground)" }}>
              Under Review
            </div>
          </Card>
          <Card className="text-center">
            <div
              className="text-2xl font-bold"
              style={{ color: "var(--color-green-600)" }}
            >
              {innovations.filter((i) => i.status === "verified").length}
            </div>
            <div style={{ color: "var(--color-muted-foreground)" }}>
              Verified
            </div>
          </Card>
          <Card className="text-center">
            <div
              className="text-2xl font-bold"
              style={{ color: "var(--color-purple-600)" }}
            >
              {innovations.reduce(
                (sum, i) =>
                  sum +
                  i.communityVotes.positive +
                  i.communityVotes.negative +
                  i.communityVotes.neutral,
                0,
              )}
            </div>
            <div style={{ color: "var(--color-muted-foreground)" }}>
              Community Votes
            </div>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5"
                  style={{ color: "var(--color-muted-foreground)" }}
                />
                <input
                  type="text"
                  placeholder="Search innovations to review..."
                  style={{ ...inputStyles, paddingLeft: "2.5rem" }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <select
              style={inputStyles}
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="under_review">Under Review</option>
              <option value="verified">Verified</option>
              <option value="needs_more_info">Needs More Info</option>
            </select>
          </div>
        </Card>

        {/* Innovations List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredInnovations.map((innovation) => (
            <Card
              key={innovation.id}
              variant="outlined"
              className="hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-2">
                  <div
                    className="flex items-center px-2 py-1 rounded text-xs font-semibold"
                    style={{
                      backgroundColor: `${getStatusColor(innovation.status)}20`,
                      color: getStatusColor(innovation.status),
                    }}
                  >
                    {getStatusIcon(innovation.status)}
                    <span className="ml-1 capitalize">
                      {innovation.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <span
                  className="text-xs"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  {new Date(innovation.submittedDate).toLocaleDateString()}
                </span>
              </div>

              <h3
                className="text-lg font-semibold mb-2"
                style={{ color: "var(--color-foreground)" }}
              >
                {innovation.title}
              </h3>

              <p
                className="text-sm mb-3 line-clamp-2"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                {innovation.description}
              </p>

              <div
                className="flex items-center justify-between mb-3 text-xs"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                <span>{innovation.country}</span>
                <span>{innovation.innovationType}</span>
              </div>

              <div className="flex items-center justify-between mb-4 text-sm">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center">
                    <span
                      className="text-xs"
                      style={{ color: "var(--color-green-600)" }}
                    >
                      👍 {innovation.communityVotes.positive}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span
                      className="text-xs"
                      style={{ color: "var(--color-red-600)" }}
                    >
                      👎 {innovation.communityVotes.negative}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span
                      className="text-xs"
                      style={{ color: "var(--color-yellow-600)" }}
                    >
                      ⭐ {innovation.expertReviews}
                    </span>
                  </div>
                </div>
                <div
                  className="text-xs"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  {innovation.evidence.length} files
                </div>
              </div>

              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  onClick={() => setSelectedInnovation(innovation)}
                >
                  <Eye className="h-3 w-3 mr-1" />
                  Review
                </Button>
                <Button size="sm" variant="ghost">
                  <MessageCircle className="h-3 w-3" />
                </Button>
                <Button size="sm" variant="ghost">
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {/* Detailed Review Modal/Panel */}
        {selectedInnovation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <Card>
                <div className="flex justify-between items-start mb-4">
                  <h2
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    {selectedInnovation.title}
                  </h2>
                  <Button
                    variant="ghost"
                    onClick={() => setSelectedInnovation(null)}
                  >
                    ×
                  </Button>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3
                      className="font-semibold mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Innovation Details
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <strong>Organization:</strong>{" "}
                        {selectedInnovation.organization}
                      </div>
                      <div>
                        <strong>Country:</strong> {selectedInnovation.country}
                      </div>
                      <div>
                        <strong>Type:</strong>{" "}
                        {selectedInnovation.innovationType}
                      </div>
                      <div>
                        <strong>Submitted by:</strong>{" "}
                        {selectedInnovation.submitterName}
                      </div>
                      <div>
                        <strong>Date:</strong>{" "}
                        {new Date(
                          selectedInnovation.submittedDate,
                        ).toLocaleDateString()}
                      </div>
                    </div>

                    <h4
                      className="font-semibold mt-4 mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Description
                    </h4>
                    <p
                      className="text-sm"
                      style={{ color: "var(--color-muted-foreground)" }}
                    >
                      {selectedInnovation.description}
                    </p>
                  </div>

                  <div>
                    <h3
                      className="font-semibold mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Community Feedback
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Positive votes</span>
                        <span
                          className="text-sm font-semibold"
                          style={{ color: "var(--color-green-600)" }}
                        >
                          {selectedInnovation.communityVotes.positive}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Negative votes</span>
                        <span
                          className="text-sm font-semibold"
                          style={{ color: "var(--color-red-600)" }}
                        >
                          {selectedInnovation.communityVotes.negative}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Expert reviews</span>
                        <span
                          className="text-sm font-semibold"
                          style={{ color: "var(--color-blue-600)" }}
                        >
                          {selectedInnovation.expertReviews}
                        </span>
                      </div>
                    </div>

                    <h4
                      className="font-semibold mt-4 mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Evidence Files
                    </h4>
                    <div className="space-y-2">
                      {selectedInnovation.evidence.map((file, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 rounded"
                          style={{ backgroundColor: "var(--color-muted)" }}
                        >
                          <span className="text-sm">{file}</span>
                          <Button size="sm" variant="ghost">
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div
                  className="mt-6 pt-4"
                  style={{ borderTop: "1px solid var(--color-border)" }}
                >
                  <h3
                    className="font-semibold mb-3"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Your Review
                  </h3>
                  <div className="flex space-x-3">
                    <Button
                      size="sm"
                      style={{
                        backgroundColor: "var(--color-green-600)",
                        color: "white",
                      }}
                    >
                      👍 Verify
                    </Button>
                    <Button
                      size="sm"
                      style={{
                        backgroundColor: "var(--color-yellow-600)",
                        color: "white",
                      }}
                    >
                      ℹ️ Needs Info
                    </Button>
                    <Button
                      size="sm"
                      style={{
                        backgroundColor: "var(--color-red-600)",
                        color: "white",
                      }}
                    >
                      👎 Reject
                    </Button>
                    <Button size="sm" variant="outline">
                      💬 Comment
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}

        {filteredInnovations.length === 0 && (
          <Card className="text-center py-12">
            <div style={{ color: "var(--color-muted-foreground)" }}>
              No innovations found matching your criteria.
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
