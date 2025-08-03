import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { GraduationCap, Users, BookOpen, Globe, Award, Heart, LucideIcon } from 'lucide-react';

// Color constants
const COLORS = {
  gray: {
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  emerald: {
    300: '#6ee7b7',
    400: '#34d399',
    500: '#10b981',
    600: '#059669',
    900: '#064e3b',
  },
  blue: {
    400: '#60a5fa',
    500: '#3b82f6',
  },
  purple: {
    400: '#a855f7',
    500: '#8b5cf6',
  },
  orange: {
    400: '#fb923c',
    500: '#f97316',
  },
};

const CHART_COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f97316', '#ef4444'];

// TypeScript interfaces
interface ResearchInvestment {
  organization: string;
  amount: number;
  focus: string;
  location: string;
  type: string;
  timeline: string;
  status: string;
  description: string;
  impact: string;
  beneficiaries: string;
}

interface FocusArea {
  name: string;
  value: number;
  color: string;
}

interface ImpactMetric {
  icon: LucideIcon;
  title: string;
  value: string;
  subtitle: string;
  description: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

// Mock data for Research & Capacity Building investments
const researchInvestments: ResearchInvestment[] = [
  {
    organization: 'Google',
    amount: 37,
    focus: 'AI Research & Training',
    location: 'Accra, Ghana',
    type: 'Community Center & University Partnerships',
    timeline: '2024-2027',
    status: 'active',
    description: 'AI Community Center, language tools, university research partnerships',
    impact: 'Direct capacity building with no profit extraction',
    beneficiaries: '1000+ researchers and students',
  },
  {
    organization: 'DeepMind',
    amount: 15,
    focus: 'Mathematical Research',
    location: 'Multiple African Universities',
    type: 'Research Grants & Fellowships',
    timeline: '2023-2026',
    status: 'active',
    description: 'Supporting mathematical research and AI safety studies',
    impact: 'Building foundational research capacity',
    beneficiaries: '200+ graduate students',
  },
  {
    organization: 'Mozilla Foundation',
    amount: 8,
    focus: 'Open Source AI Tools',
    location: 'Pan-African',
    type: 'Community Development',
    timeline: '2024-2025',
    status: 'active',
    description: 'Developing open-source AI tools for African languages',
    impact: 'Community-owned technology development',
    beneficiaries: '50+ language communities',
  },
];

const focusAreas: FocusArea[] = [
  { name: 'University Research', value: 45, color: COLORS.emerald[500] },
  { name: 'Community Training', value: 30, color: COLORS.blue[500] },
  { name: 'Open Source Tools', value: 15, color: COLORS.purple[500] },
  { name: 'Language Preservation', value: 10, color: COLORS.orange[500] },
];

const impactMetrics: ImpactMetric[] = [
  {
    icon: GraduationCap,
    title: 'Research Capacity',
    value: '1,200+',
    subtitle: 'Researchers & Students',
    description: 'Direct beneficiaries of capacity building programs',
  },
  {
    icon: BookOpen,
    title: 'Knowledge Creation',
    value: '150+',
    subtitle: 'Research Publications',
    description: 'Academic papers and open research outputs',
  },
  {
    icon: Globe,
    title: 'Community Impact',
    value: '50+',
    subtitle: 'Language Communities',
    description: 'African languages supported by AI tools',
  },
  {
    icon: Award,
    title: 'Institutional Partnerships',
    value: '25+',
    subtitle: 'Universities',
    description: 'African institutions with research partnerships',
  },
];

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div
        style={{
          backgroundColor: COLORS.gray[900],
          padding: "12px",
          borderRadius: "8px",
          border: `1px solid ${COLORS.gray[700]}`,
          color: COLORS.gray[100],
          fontSize: "14px",
        }}
      >
        <p style={{ margin: 0, fontWeight: "bold" }}>{data.organization}</p>
        <p style={{ margin: "4px 0 0 0", color: COLORS.emerald[400] }}>
          ${data.amount}M investment
        </p>
        <p style={{ margin: "4px 0 0 0", color: COLORS.gray[400], fontSize: "12px" }}>
          {data.focus} • {data.location}
        </p>
      </div>
    );
  }
  return null;
};

const ResearchCapacityTab: React.FC = () => {
  const totalInvestment = researchInvestments.reduce((sum, inv) => sum + inv.amount, 0);

  return (
    <div style={{ backgroundColor: COLORS.gray[800], padding: "24px", borderRadius: "12px" }}>

      <h3 style={{ color: COLORS.gray[200], marginTop: 0, marginBottom: "24px", fontSize: "20px", fontWeight: "600" }}>
        Research & Capacity
      </h3>

      {/* Investment Overview Chart */}
      <div style={{ marginBottom: "32px" }}>
        <h4 style={{ color: COLORS.gray[200], marginBottom: "16px", fontSize: "16px" }}>
          Investment Distribution by Organization
        </h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={researchInvestments} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.gray[700]} />
            <XAxis 
              dataKey="organization" 
              stroke={COLORS.gray[400]} 
              fontSize={12}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke={COLORS.gray[400]} fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="amount" name="Investment ($M)" fill={COLORS.emerald[500]} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Focus Areas Pie Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', marginBottom: '32px' }}>
        <div>
          <h4 style={{ color: COLORS.gray[200], marginBottom: "16px", fontSize: "16px" }}>
            Focus Areas Distribution
          </h4>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={focusAreas}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }: any) => `${name}: ${value}%`}
                labelLine={false}
              >
                {focusAreas.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div>
          <h4 style={{ color: COLORS.gray[200], marginBottom: "16px", fontSize: "16px" }}>
            Impact Metrics
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {impactMetrics.map((metric, index) => (
              <div key={index} style={{
                backgroundColor: COLORS.gray[900],
                padding: "16px",
                borderRadius: "8px",
                textAlign: "center"
              }}>
                <metric.icon className="h-8 w-8 mx-auto mb-2" style={{ color: COLORS.emerald[400] }} />
                <div style={{ color: COLORS.emerald[400], fontWeight: "bold", fontSize: "20px" }}>
                  {metric.value}
                </div>
                <div style={{ color: COLORS.gray[300], fontSize: "12px", marginBottom: "4px" }}>
                  {metric.subtitle}
                </div>
                <div style={{ color: COLORS.gray[500], fontSize: "10px" }}>
                  {metric.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Investment Cards */}
      <div>
        <h4 style={{ color: COLORS.gray[200], marginBottom: "16px", fontSize: "16px" }}>
          Verified Research & Capacity Investments
        </h4>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "16px" }}>
          {researchInvestments.map((investment, index) => (
            <div key={investment.organization} style={{
              backgroundColor: COLORS.gray[900],
              padding: "20px",
              borderRadius: "12px",
              border: `2px solid ${COLORS.emerald[600]}`
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <h5 style={{ color: COLORS.gray[200], margin: 0, fontSize: "16px" }}>{investment.organization}</h5>
                <span style={{ color: COLORS.emerald[400], fontWeight: "bold", fontSize: "18px" }}>
                  ${investment.amount}M
                </span>
              </div>
              
              <div style={{ marginBottom: "8px" }}>
                <span style={{ color: COLORS.emerald[400], fontSize: "14px", fontWeight: "500" }}>
                  {investment.focus}
                </span>
                <span style={{ color: COLORS.gray[400], fontSize: "12px", marginLeft: "8px" }}>
                  • {investment.location}
                </span>
              </div>
              
              <div style={{ color: COLORS.gray[400], fontSize: "12px", marginBottom: "8px" }}>
                <strong>Type:</strong> {investment.type}
              </div>
              
              <div style={{ color: COLORS.gray[400], fontSize: "12px", marginBottom: "8px" }}>
                <strong>Timeline:</strong> {investment.timeline}
              </div>
              
              <div style={{ color: COLORS.gray[300], fontSize: "13px", marginBottom: "8px" }}>
                {investment.description}
              </div>
              
              <div style={{ 
                backgroundColor: COLORS.emerald[900], 
                padding: "8px", 
                borderRadius: "6px",
                marginBottom: "8px"
              }}>
                <div style={{ color: COLORS.emerald[300], fontSize: "11px", fontWeight: "500" }}>
                  Impact: {investment.impact}
                </div>
                <div style={{ color: COLORS.emerald[400], fontSize: "11px" }}>
                  Beneficiaries: {investment.beneficiaries}
                </div>
              </div>
              
              <div style={{
                color: COLORS.emerald[400],
                fontSize: "12px",
                fontWeight: "500"
              }}>
                Status: {investment.status.charAt(0).toUpperCase() + investment.status.slice(1)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Distinction Callout */}
      <div style={{
        marginTop: "24px",
        padding: "16px",
        backgroundColor: COLORS.gray[700],
        borderRadius: "8px",
        borderLeft: `4px solid ${COLORS.emerald[400]}`
      }}>
        <h4 style={{ color: COLORS.emerald[400], margin: "0 0 8px 0", fontSize: "14px" }}>
          Why This Category Matters
        </h4>
        <p style={{ color: COLORS.gray[300], fontSize: "12px", margin: 0 }}>
          Unlike startup investments or infrastructure projects, Research & Capacity Building investments focus on 
          <strong> knowledge creation and community empowerment</strong> with minimal profit extraction. 
          These investments build the foundational human capital that makes sustainable AI development possible, 
          creating lasting value that benefits entire communities rather than individual investors.
        </p>
      </div>
    </div>
  );
};

export default ResearchCapacityTab;
