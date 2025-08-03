import React, { useState } from "react";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import "react-tabs/style/react-tabs.css";
import { TrendingUp, MapPin, Building2 } from "lucide-react";
import {
  FundingBreakdownTab,
  GeographicDistributionTab,
  SectorAnalysisTab,
  TemporalTrendsTab,
  InfrastructurePipelineTab,
  ResearchCapacityTab,
} from "./FundingTabs";

// Updated data based on your revised analytics data
const fundingData = {
  totalVerifiedInvestment: {
    amount: 1103200000, // $1.103 billion
    currency: "USD",
    period: "2020-2025",
    lastUpdated: "2025-08-01",
    verificationStatus: "verified_committed_and_disbursed",
  },
  startupEcosystem: {
    totalFunding: 803200000, // $803.2M
    companiesCount: 159,
    averageFunding: 5047000, // $5.047M average
  },
};

// Color palette consistent with your design system
const COLORS = {
  cyan: {
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
  },
  green: {
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
  },
  purple: {
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
  },
  yellow: {
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
  },
  red: {
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
  },
};

const CHART_COLORS = [
  "var(--color-primary)", // Site's primary color
  "var(--color-info)", // Site's info color (light cyan)
  "#8b5cf6", // Light purple (for Government & Development)
  COLORS.green[500], // Keep green for positive KPIs
  "var(--color-accent)", // Site's accent color
  "#ec4899", // Light pink
  "#06b6d4", // Light cyan
  "#10b981", // Light emerald
];

// Data transformations for charts
const fundingBreakdown = [
  {
    name: "Startup Ecosystem",
    amount: 803.2,
    percentage: 72.8,
    status: "verified_funding",
    description: "159 companies, $5.0M avg",
  },
  {
    name: "Corporate Infrastructure",
    amount: 200.0,
    percentage: 18.1,
    status: "verified_committed",
    description: "Microsoft, Google, Meta commitments",
  },
  {
    name: "Government & Development",
    amount: 100.0,
    percentage: 9.1,
    status: "verified_disbursed",
    description: "Gates Foundation, UK FCDO, IDRC",
  },
];

const geographicData = [
  {
    name: "Kenya",
    amount: 242.3,
    companies: 19,
    avgPerCompany: 12.8,
    efficiency: "exceptional",
  },
  {
    name: "Tunisia",
    amount: 244.4,
    companies: 9,
    avgPerCompany: 27.2,
    strategy: "deep_tech_focused",
  },
  {
    name: "South Africa",
    amount: 150.4,
    companies: 31,
    avgPerCompany: 4.9,
    advantage: "established_infrastructure",
  },
  {
    name: "Egypt",
    amount: 83.4,
    companies: 44,
    avgPerCompany: 1.9,
    focus: "ecosystem_building",
  },
  {
    name: "Nigeria",
    amount: 47.3,
    companies: 34,
    avgPerCompany: 1.4,
    potential: "large_market_underserved",
  },
  {
    name: "Other Countries",
    amount: 35.4,
    companies: 22,
    avgPerCompany: 1.6,
    note: "17 countries",
  },
];

const sectorData = [
  {
    name: "FinTech",
    percentage: 20.9,
    companies: 33,
    rationale: "Unbanked population opportunity",
  },
  {
    name: "TalentTech",
    percentage: 19.9,
    companies: 32,
    rationale: "Demographic dividend",
  },
  {
    name: "EdTech",
    percentage: 14.8,
    companies: 24,
    rationale: "Skills development needs",
  },
  {
    name: "HealthTech",
    percentage: 5.8,
    companies: 9,
    rationale: "Massive underserved potential",
  },
  {
    name: "ContentTech",
    percentage: 5.8,
    companies: 9,
    rationale: "Creative economy growth",
  },
  {
    name: "LogisTech",
    percentage: 4.8,
    companies: 8,
    rationale: "Supply chain optimization",
  },
  {
    name: "AgriTech",
    percentage: 3.9,
    companies: 6,
    rationale: "60% workforce disconnect",
  },
  {
    name: "ClimateTech",
    percentage: 1.3,
    companies: 2,
    rationale: "Critical underinvestment",
  },
];

const temporalData = [
  { year: 2020, amount: 34.9, companies: 8 },
  { year: 2021, amount: 166.9, companies: 24 },
  { year: 2022, amount: 167.7, companies: 28 }, // Peak year
  { year: 2023, amount: 17.9, companies: 12 }, // Market correction
  { year: 2024, amount: 277.7, companies: 45 }, // Recovery
  { year: 2025, amount: 138.1, companies: 42 }, // Through June
];

const infrastructurePipeline = [
  {
    name: "AWS Infrastructure",
    amount: 1700,
    timeline: "2024-2029",
    status: "committed_not_disbursed",
  },
  {
    name: "Cassava-Nvidia AI Factories",
    amount: 720,
    timeline: "2025-2027",
    status: "deployment_beginning",
  },
];

// Custom Tooltip component
interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({
  active,
  payload,
  label,
}) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          backgroundColor: "var(--color-card)",
          border: `1px solid var(--color-border)`,
          padding: "12px",
          borderRadius: "8px",
          boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.1)",
          color: "var(--color-card-foreground)",
        }}
      >
        <p
          style={{
            marginTop: 0,
            marginBottom: 0,
            marginLeft: 0,
            marginRight: 0,
            fontWeight: "bold",
            color: "var(--color-primary)",
          }}
        >
          {label}
        </p>
        {payload.map((item: any, index: number) => (
          <p
            key={index}
            style={{
              marginTop: "4px",
              marginBottom: "4px",
              marginLeft: 0,
              marginRight: 0,
              color: item.color,
            }}
          >
            {item.name}: $
            {typeof item.value === "number"
              ? item.value.toFixed(1)
              : item.value}
            M
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Stat Card component
interface StatCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ComponentType<{ size?: number; style?: React.CSSProperties }>;
  trend?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
}) => (
  <div
    style={{
      backgroundColor: "var(--color-background)",
      padding: "20px",
      borderRadius: "12px",
      border: `1px solid var(--color-border)`,
      textAlign: "center",
      minWidth: "200px",
    }}
  >
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        marginBottom: "8px",
      }}
    >
      <Icon
        size={20}
        style={{ color: "var(--color-primary)", marginRight: "8px" }}
      />
      <h3
        style={{
          color: "#9ca3af",
          fontSize: "14px",
          marginTop: 0,
          marginBottom: 0,
          marginLeft: 0,
          marginRight: 0,
          fontWeight: "500",
        }}
      >
        {title}
      </h3>
    </div>
    <p
      style={{
        color: "var(--color-foreground)",
        fontSize: "28px",
        fontWeight: "bold",
        marginTop: "8px",
        marginBottom: "8px",
        marginLeft: 0,
        marginRight: 0,
      }}
    >
      {value}
    </p>
    <p
      style={{
        color: "#9ca3af",
        fontSize: "13px",
        marginTop: 0,
        marginBottom: 0,
        marginLeft: 0,
        marginRight: 0,
      }}
    >
      {subtitle}
    </p>
    {trend && (
      <div
        style={{
          marginTop: "12px",
          paddingTop: "8px",
          borderTop: "1px solid var(--color-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <TrendingUp
          size={12}
          style={{ color: COLORS.green[500], marginRight: "4px" }}
        />
        <span
          style={{
            color: COLORS.green[500],
            fontSize: "12px",
            fontWeight: "500",
          }}
        >
          {trend}
        </span>
      </div>
    )}
  </div>
);

// Main Interactive Analytics Panel
const InteractiveAnalyticsPanel = () => {
  const [selectedTab, setSelectedTab] = useState(0);

  // Add custom styles for tab interactions
  React.useEffect(() => {
    const style = document.createElement("style");
    style.textContent = `
      .custom-tab:hover {
        background-color: var(--color-primary) !important;
        color: var(--color-primary-foreground) !important;
        border-color: var(--color-primary) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
      }

      .custom-tab[aria-selected="true"] {
        background-color: var(--color-primary) !important;
        color: var(--color-primary-foreground) !important;
        border-color: var(--color-primary) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
      }

      .custom-tab:active {
        transform: translateY(0px);
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <div
      style={{
        backgroundColor: "var(--color-card)",
        padding: "24px",
        borderRadius: "16px",
        border: `1px solid var(--color-border)`,
        color: "var(--color-card-foreground)",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Subtitle only - main title is handled by page header */}
      <div style={{ textAlign: "center", marginBottom: "32px" }}>
        <p
          style={{
            color: "var(--color-muted-foreground)",
            fontSize: "14px",
            marginTop: 0,
            marginBottom: 0,
            marginLeft: "auto",
            marginRight: "auto",
            maxWidth: "600px",
          }}
        >
          Verified investment analysis across 159 companies • Last updated:
          August 2025
        </p>
      </div>

      {/* Key Stats Row */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          marginBottom: "32px",
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        <StatCard
          title="Total Verified Investment"
          value="$1.1B+"
          subtitle="Across three verified categories"
          icon={TrendingUp}
          trend="+127% since 2023"
        />
        <StatCard
          title="Active Startups"
          value="159"
          subtitle="$5.0M average funding"
          icon={Building2}
          trend="22 countries represented"
        />
        <StatCard
          title="Geographic Concentration"
          value="5"
          subtitle="Countries hold 92.3% of funding"
          icon={MapPin}
          trend="High concentration risk"
        />
      </div>

      {/* Tabs */}
      <Tabs
        selectedIndex={selectedTab}
        onSelect={(index) => setSelectedTab(index || 0)}
      >
        <TabList
          style={{
            display: "flex",
            gap: "8px",
            marginTop: 0,
            marginBottom: "32px",
            marginLeft: 0,
            marginRight: 0,
            backgroundColor: "transparent",
            flexWrap: "wrap",
            listStyle: "none",
            padding: 0,
            justifyContent: "center",
          }}
        >
          <Tab
            className="custom-tab"
            style={{
              padding: "12px 20px",
              color: "#9ca3af",
              cursor: "pointer",
              transition: "all 0.3s ease",
              backgroundColor: "var(--color-background)",
              border: `1px solid var(--color-border)`,
              borderRadius: "8px",
              outline: "none",
              fontSize: "14px",
              fontWeight: "500",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            Funding Breakdown
          </Tab>
          <Tab
            className="custom-tab"
            style={{
              padding: "12px 20px",
              color: "#9ca3af",
              cursor: "pointer",
              transition: "all 0.3s ease",
              backgroundColor: "var(--color-background)",
              border: `1px solid var(--color-border)`,
              borderRadius: "8px",
              outline: "none",
              fontSize: "14px",
              fontWeight: "500",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            Geographic Distribution
          </Tab>
          <Tab
            className="custom-tab"
            style={{
              padding: "12px 20px",
              color: "#9ca3af",
              cursor: "pointer",
              transition: "all 0.3s ease",
              backgroundColor: "var(--color-background)",
              border: `1px solid var(--color-border)`,
              borderRadius: "8px",
              outline: "none",
              fontSize: "14px",
              fontWeight: "500",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            Sector Analysis
          </Tab>
          <Tab
            className="custom-tab"
            style={{
              padding: "12px 20px",
              color: "#9ca3af",
              cursor: "pointer",
              transition: "all 0.3s ease",
              backgroundColor: "var(--color-background)",
              border: `1px solid var(--color-border)`,
              borderRadius: "8px",
              outline: "none",
              fontSize: "14px",
              fontWeight: "500",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            Temporal Trends
          </Tab>
          <Tab
            className="custom-tab"
            style={{
              padding: "12px 20px",
              color: "#9ca3af",
              cursor: "pointer",
              transition: "all 0.3s ease",
              backgroundColor: "var(--color-background)",
              border: `1px solid var(--color-border)`,
              borderRadius: "8px",
              outline: "none",
              fontSize: "14px",
              fontWeight: "500",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            Infrastructure Pipeline
          </Tab>
          <Tab
            className="custom-tab"
            style={{
              padding: "12px 20px",
              color: "#9ca3af",
              cursor: "pointer",
              transition: "all 0.3s ease",
              backgroundColor: "var(--color-background)",
              border: `1px solid var(--color-border)`,
              borderRadius: "8px",
              outline: "none",
              fontSize: "14px",
              fontWeight: "500",
              boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
            }}
          >
            Research & Capacity
          </Tab>
        </TabList>

        {/* Tab 1: Funding Breakdown */}
        <TabPanel>
          <FundingBreakdownTab fundingBreakdown={fundingBreakdown} />
        </TabPanel>

        {/* Tab 2: Geographic Distribution */}
        <TabPanel>
          <GeographicDistributionTab geographicData={geographicData} />
        </TabPanel>

        {/* Tab 3: Sector Analysis */}
        <TabPanel>
          <SectorAnalysisTab sectorData={sectorData} />
        </TabPanel>

        {/* Tab 4: Temporal Trends */}
        <TabPanel>
          <TemporalTrendsTab temporalData={temporalData} />
        </TabPanel>

        {/* Tab 5: Infrastructure Pipeline */}
        <TabPanel>
          <InfrastructurePipelineTab
            infrastructurePipeline={infrastructurePipeline}
          />
        </TabPanel>

        {/* Tab 6: Research & Capacity Building */}
        <TabPanel>
          <ResearchCapacityTab />
        </TabPanel>
      </Tabs>

      {/* Data Quality Footer */}
      <div
        style={{
          marginTop: "32px",
          padding: "20px",
          backgroundColor: "var(--color-background)",
          borderRadius: "12px",
          border: `1px solid var(--color-border)`,
        }}
      >
        <h4
          style={{
            color: "var(--color-foreground)",
            marginBottom: "12px",
            fontSize: "16px",
          }}
        >
          Data Quality & Verification
        </h4>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "16px",
          }}
        >
          <div>
            <div
              style={{
                color: COLORS.green[500],
                fontSize: "12px",
                fontWeight: "500",
                marginBottom: "4px",
              }}
            >
              VERIFICATION LEVEL
            </div>
            <div
              style={{
                color: "#9ca3af",
                fontSize: "14px",
              }}
            >
              Documented sources only
            </div>
          </div>
          <div>
            <div
              style={{
                color: COLORS.green[500],
                fontSize: "12px",
                fontWeight: "500",
                marginBottom: "4px",
              }}
            >
              CONFIDENCE LEVEL
            </div>
            <div
              style={{
                color: "#9ca3af",
                fontSize: "14px",
              }}
            >
              High (mathematical integrity verified)
            </div>
          </div>
          <div>
            <div
              style={{
                color: COLORS.green[500],
                fontSize: "12px",
                fontWeight: "500",
                marginBottom: "4px",
              }}
            >
              LAST VERIFIED
            </div>
            <div
              style={{
                color: "#9ca3af",
                fontSize: "14px",
              }}
            >
              August 1, 2025
            </div>
          </div>
          <div>
            <div
              style={{
                color: COLORS.green[500],
                fontSize: "12px",
                fontWeight: "500",
                marginBottom: "4px",
              }}
            >
              PRIMARY SOURCE
            </div>
            <div
              style={{
                color: "#9ca3af",
                fontSize: "14px",
              }}
            >
              StartupList Africa database
            </div>
          </div>
        </div>

        <div
          style={{
            marginTop: "16px",
            padding: "12px",
            backgroundColor: "#111827",
            borderRadius: "8px",
          }}
        >
          <div
            style={{
              color: "#22d3ee",
              fontSize: "12px",
              fontWeight: "500",
              marginBottom: "8px",
            }}
          >
            EXCLUDED FROM TOTALS
          </div>
          <ul
            style={{
              color: "#9ca3af",
              fontSize: "12px",
              marginTop: 0,
              marginBottom: 0,
              marginLeft: 0,
              marginRight: 0,
              paddingLeft: "16px",
            }}
          >
            <li>
              Chinese government announcements ($52B+) - verification challenges
            </li>
            <li>
              Africa AI Fund proposal ($60B) - aspirational without confirmed
              commitments
            </li>
            <li>
              Infrastructure pipeline commitments - separate category for future
              deployment
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default InteractiveAnalyticsPanel;
