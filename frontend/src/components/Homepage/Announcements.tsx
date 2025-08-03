import React from "react";
import { Building2, TrendingUp, Globe, AlertTriangle } from "lucide-react";
import { Section2Text, Section3Text } from "@/components/ui/adaptive-text";

// Major funding announcements data
const majorAnnouncements = [
  {
    id: 1,
    title: "AWS $1.7B Africa Infrastructure",
    amount: "$1.7B",
    period: "2024-2029",
    description: "Amazon Web Services commits to massive cloud and AI infrastructure development across Africa, targeting data centers and computing capacity.",
    status: "Confirmed",
    icon: Building2,
    category: "Infrastructure",
    highlight: "Largest single commitment",
    theme: "primary" // Light blue theme
  },
  {
    id: 2,
    title: "Microsoft AI Infrastructure",
    amount: "$1.4B",
    period: "2025-2027",
    description: "$297M for South Africa AI infrastructure plus $1.1B in previous data center investments, focusing on AI development and cloud services.",
    status: "Confirmed",
    icon: TrendingUp,
    category: "Infrastructure",
    highlight: "Multi-phase deployment",
    theme: "accent" // Purple theme
  },
  {
    id: 3,
    title: "Cassava-Nvidia AI Factories",
    amount: "$720M",
    period: "Multi-year",
    description: "AI factories and data centers across South Africa, Egypt, Nigeria, Kenya, and Morocco, creating continent-wide AI infrastructure.",
    status: "Pipeline",
    icon: Globe,
    category: "Infrastructure",
    highlight: "Multi-country deployment",
    theme: "info" // Teal theme
  },
  {
    id: 4,
    title: "Africa AI Fund Proposal",
    amount: "$60B",
    period: "Proposed",
    description: "Ambitious proposal from Global AI Summit in Kigali covering 52 African nations, requiring verification and implementation tracking.",
    status: "Aspirational",
    icon: AlertTriangle,
    category: "Development",
    highlight: "Verification pending",
    theme: "success" // Light green theme
  }
];

// Announcement Card Component
const AnnouncementCard: React.FC<{ announcement: typeof majorAnnouncements[0] }> = ({ announcement }) => {
  const Icon = announcement.icon;
  
  // Get theme colors based on the card's theme
  const getThemeColors = (theme: string) => {
    switch (theme) {
      case 'primary':
        return {
          main: 'var(--color-primary)',
          background: 'var(--color-primary-background)'
        };
      case 'accent':
        return {
          main: 'var(--color-accent)',
          background: 'var(--color-accent-background)'
        };
      case 'info':
        return {
          main: 'var(--color-info)',
          background: 'var(--color-info-background)'
        };
      case 'success':
        return {
          main: 'var(--color-success)',
          background: 'var(--color-success-background)'
        };
      default:
        return {
          main: 'var(--color-primary)',
          background: 'var(--color-primary-background)'
        };
    }
  };
  
  const themeColors = getThemeColors(announcement.theme);
  
  return (
    <div 
      className="p-6 rounded-xl border transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-105 hover:-translate-y-1"
      style={{
        backgroundColor: "var(--color-card)",
        borderColor: "var(--color-border)"
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <div 
            className="p-2 rounded-lg mr-3"
            style={{
              backgroundColor: themeColors.background
            }}
          >
            <Icon 
              className="h-5 w-5" 
              style={{
                color: themeColors.main
              }} 
            />
          </div>
          <div>
            <h3 className="font-semibold text-lg" style={{ color: "var(--color-card-foreground)" }}>
              {announcement.title}
            </h3>
            <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
              {announcement.period}
            </p>
          </div>
        </div>
        
        <div 
          className="px-3 py-1 rounded-full text-xs font-medium"
          style={{
            backgroundColor: themeColors.background,
            color: themeColors.main
          }}
        >
          {announcement.status}
        </div>
      </div>

      {/* Amount */}
      <div className="mb-4">
        <div className="text-3xl font-bold" style={{ color: themeColors.main }}>
          {announcement.amount}
        </div>
        <div className="text-sm font-medium" style={{ color: themeColors.main }}>
          {announcement.highlight}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm mb-4" style={{ color: "var(--color-muted-foreground)" }}>
        {announcement.description}
      </p>

      {/* Category */}
      <div 
        className="inline-block px-2 py-1 rounded text-xs font-medium"
        style={{
          backgroundColor: themeColors.main,
          color: "white"
        }}
      >
        {announcement.category}
      </div>
    </div>
  );
};

// Main Announcements Component
const Announcements: React.FC = () => {
  const totalConfirmed = majorAnnouncements
    .filter(a => a.status === 'Confirmed')
    .reduce((sum, a) => sum + parseFloat(a.amount.replace('$', '').replace('B', '000').replace('M', '')), 0);

  return (
    <div className="space-y-8">
      {/* Announcement Cards Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {majorAnnouncements.map((announcement) => (
          <AnnouncementCard key={announcement.id} announcement={announcement} />
        ))}
      </div>

      {/* Summary Stats */}
      <div 
        className="p-6 rounded-xl border"
        style={{
          backgroundColor: "var(--color-muted)",
          borderColor: "var(--color-border)"
        }}
      >
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-2xl font-bold mb-1" style={{ color: "var(--color-primary)" }}>
              ${(totalConfirmed/1000).toFixed(1)}B
            </div>
            <div className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
              Confirmed Commitments
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold mb-1" style={{ color: "var(--color-info)" }}>
              4
            </div>
            <div className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
              Major Announcements
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold mb-1" style={{ color: "var(--color-success)" }}>
              75%
            </div>
            <div className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
              Infrastructure Focus
            </div>
          </div>
        </div>
      </div>

      {/* Research Note */}
      <div 
        className="p-4 rounded-lg border-l-4"
        style={{
          backgroundColor: "var(--color-muted)",
          borderLeftColor: "var(--color-info)"
        }}
      >
        <Section3Text as="h4" className="font-medium mb-2" style={{ color: "var(--color-info)" }}>
          Research Methodology
        </Section3Text>
        <Section3Text as="p" className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
          All announcements verified through official press releases, government statements, and corporate filings. 
          TAIFA-FIALA tracks implementation progress and actual disbursements separately from initial commitments.
        </Section3Text>
      </div>
    </div>
  );
};

export default Announcements;