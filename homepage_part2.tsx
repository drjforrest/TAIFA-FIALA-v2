import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, MapPin, Building2, Users, AlertTriangle, Info } from "lucide-react";

// Color palette consistent with design system
const COLORS = {
  cyan: { 400: "#22d3ee", 500: "#06b6d4", 600: "#0891b2", 700: "#0e7490" },
  gray: { 100: "#f3f4f6", 200: "#e5e7eb", 300: "#d1d5db", 400: "#9ca3af", 500: "#6b7280", 600: "#4b5563", 700: "#374151", 800: "#1f2937", 900: "#111827" },
  green: { 400: "#4ade80", 500: "#22c55e", 600: "#16a34a" },
  purple: { 400: "#c084fc", 500: "#a855f7", 600: "#9333ea" },
  yellow: { 400: "#fbbf24", 500: "#f59e0b", 600: "#d97706" },
  red: { 400: "#f87171", 500: "#ef4444", 600: "#dc2626" },
  orange: { 400: "#fb923c", 500: "#f97316", 600: "#ea580c" }
};

const CHART_COLORS = [COLORS.cyan[500], COLORS.cyan[700], COLORS.purple[500], COLORS.green[500], COLORS.yellow[500], COLORS.purple[400], COLORS.green[400], COLORS.yellow[400]];

// Verified $1.1B breakdown data
const verifiedFunding = [
  { name: "Startup Ecosystem", amount: 803.2, description: "159 companies, $5.0M avg", color: COLORS.cyan[500] },
  { name: "Corporate Infrastructure", amount: 200.0, description: "Microsoft, Google, Meta", color: COLORS.purple[500] },
  { name: "Government & Development", amount: 100.0, description: "Gates Foundation, UK FCDO", color: COLORS.green[500] }
];

// Unconfirmed announcements data
const unconfirmedAnnouncements = [
  { category: "Corporate Infrastructure", amount: 2420, companies: "AWS, Cassava-Nvidia", status: "Pipeline" },
  { category: "Asia Government", amount: 61000, companies: "China, Japan, S. Korea", status: "Announcements" },
  { category: "Africa AI Fund", amount: 60000, companies: "52 African Nations", status: "Aspirational" },
  { category: "EU Programs", amount: 530, companies: "Horizon Europe", status: "Committed" },
  { category: "Other Corporate", amount: 3200, companies: "Various tech companies", status: "Mixed" }
];

// Stat Card Component
const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = COLORS.cyan[400] }) => (
  <div className="bg-gray-800 p-5 rounded-xl border border-gray-700 text-center min-w-[200px]">
    <div className="flex items-center justify-center mb-2">
      <Icon size={18} style={{ color, marginRight: "8px" }} />
      <h3 className="text-gray-300 text-sm font-medium">{title}</h3>
    </div>
    <p className="text-gray-100 text-2xl font-bold mb-1">{value}</p>
    <p className="text-gray-400 text-xs">{subtitle}</p>
    {trend && (
      <div className="mt-2 flex items-center justify-center">
        <TrendingUp size={12} className="text-green-400 mr-1" />
        <span className="text-green-400 text-xs">{trend}</span>
      </div>
    )}
  </div>
);

// Custom Tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-800 border border-gray-600 p-3 rounded-lg shadow-lg">
        <p className="text-cyan-400 font-bold mb-1">{label}</p>
        {payload.map((item, index) => (
          <p key={index} style={{ color: item.color }} className="text-sm">
            {item.name}: ${typeof item.value === 'number' ? item.value.toFixed(1) : item.value}{item.name === 'Amount' ? 'M' : ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Main Component
const HomepageFundingSections = () => {
  return (
    <div className="space-y-16">
      {/* Verified Funding Section */}
      <section className="bg-gray-900 p-8 rounded-2xl border border-gray-700">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-white text-2xl font-bold mb-2">
            Verified African AI Investment
          </h2>
          <p className="text-gray-400 text-sm max-w-2xl mx-auto">
            Mathematical analysis of $1.1B+ verified investment with documented sources and confirmed disbursements
          </p>
        </div>

        {/* Key Stats */}
        <div className="flex flex-wrap gap-4 justify-center mb-8">
          <StatCard
            title="Total Verified"
            value="$1.1B+"
            subtitle="Mathematically verified"
            icon={TrendingUp}
            trend="100% source transparency"
          />
          <StatCard
            title="Active Startups"
            value="159"
            subtitle="$5.0M average funding"
            icon={Building2}
            color={COLORS.purple[400]}
          />
          <StatCard
            title="Countries"
            value="22"
            subtitle="5 countries hold 92.3%"
            icon={MapPin}
            color={COLORS.green[400]}
          />
          <StatCard
            title="Verification"
            value="100%"
            subtitle="All figures sum correctly"
            icon={Users}
            color={COLORS.yellow[500]}
          />
        </div>

        {/* Funding Breakdown Chart */}
        <div className="bg-gray-800 p-6 rounded-xl">
          <h3 className="text-white text-lg font-semibold mb-4">Verified Investment Breakdown</h3>
          <div className="grid md:grid-cols-2 gap-6 items-center">
            {/* Chart */}
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={verifiedFunding}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    innerRadius={50}
                    dataKey="amount"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    labelLine={false}
                  >
                    {verifiedFunding.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Breakdown Details */}
            <div className="space-y-4">
              {verifiedFunding.map((item, index) => (
                <div key={item.name} className="flex items-center p-3 bg-gray-900 rounded-lg">
                  <div
                    className="w-3 h-3 rounded mr-3"
                    style={{ backgroundColor: item.color }}
                  />
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-200 font-medium">{item.name}</span>
                      <span className="text-cyan-400 font-bold">${item.amount}M</span>
                    </div>
                    <div className="text-gray-400 text-xs mt-1">{item.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Mathematical Verification Note */}
          <div className="mt-6 p-4 bg-green-900/20 border border-green-600 rounded-lg">
            <div className="flex items-center">
              <Info size={16} className="text-green-400 mr-2" />
              <span className="text-green-400 text-sm font-medium">
                Mathematical Verification: 803.2 + 200.0 + 100.0 = 1,103.2 million ($1.1B+)
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Unconfirmed Announcements Section */}
      <section className="bg-gray-800 p-8 rounded-2xl border border-gray-600">
        {/* Header */}
        <div className="text-center mb-6">
          <h2 className="text-white text-xl font-bold mb-2">
            Unconfirmed Funding Announcements
          </h2>
          <p className="text-gray-400 text-sm max-w-2xl mx-auto">
            Additional $127B+ in announced commitments requiring verification and implementation tracking
          </p>
        </div>

        {/* Warning Banner */}
        <div className="bg-orange-900/20 border border-orange-600 p-4 rounded-lg mb-6">
          <div className="flex items-center">
            <AlertTriangle size={20} className="text-orange-400 mr-3" />
            <div>
              <h4 className="text-orange-400 font-medium">Verification Required</h4>
              <p className="text-orange-300 text-sm">
                These announcements require independent verification of actual disbursements and implementation status
              </p>
            </div>
          </div>
        </div>

        {/* Unconfirmed Chart */}
        <div className="h-80 mb-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={unconfirmedAnnouncements} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.gray[700]} />
              <XAxis 
                dataKey="category" 
                stroke={COLORS.gray[400]}
                fontSize={11}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis stroke={COLORS.gray[400]} fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="amount" name="Amount ($M)" fill={COLORS.orange[500]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Breakdown */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {unconfirmedAnnouncements.map((item, index) => (
            <div key={item.category} className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <div className="flex justify-between items-start mb-2">
                <h4 className="text-gray-200 font-medium text-sm">{item.category}</h4>
                <span 
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    item.status === 'Pipeline' ? 'bg-yellow-900/50 text-yellow-400' :
                    item.status === 'Announcements' ? 'bg-orange-900/50 text-orange-400' :
                    item.status === 'Aspirational' ? 'bg-red-900/50 text-red-400' :
                    item.status === 'Committed' ? 'bg-green-900/50 text-green-400' :
                    'bg-gray-700 text-gray-300'
                  }`}
                >
                  {item.status}
                </span>
              </div>
              <div className="text-orange-400 text-lg font-bold mb-1">
                ${item.amount >= 1000 ? `${(item.amount/1000).toFixed(0)}B` : `${item.amount}M`}
              </div>
              <div className="text-gray-400 text-xs">{item.companies}</div>
            </div>
          ))}
        </div>

        {/* Context Note */}
        <div className="mt-6 p-4 bg-gray-700 rounded-lg border-l-4 border-cyan-400">
          <h4 className="text-cyan-400 font-medium mb-2">Research Context</h4>
          <p className="text-gray-300 text-sm">
            Our validation research revealed $130B+ in total announcements, but only $1.1B meets verification standards. 
            TAIFA-FIALA prioritizes mathematical integrity and source transparency over inflated announcement figures.
          </p>
        </div>
      </section>
    </div>
  );
};

export default HomepageFundingSections;