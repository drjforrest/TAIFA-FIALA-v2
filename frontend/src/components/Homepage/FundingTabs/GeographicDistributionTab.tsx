import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle } from 'lucide-react';

// Color constants
const COLORS = {
  gray: {
    100: '#f3f4f6',
    200: '#e5e7eb',
    400: '#9ca3af',
    500: '#6b7280',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  cyan: {
    400: '#22d3ee',
    500: '#06b6d4',
  },
  red: {
    600: '#dc2626',
  },
};

interface GeographicItem {
  name: string;
  amount: number;
  companies: number;
  avgPerCompany: number;
  efficiency?: string;
  strategy?: string;
  advantage?: string;
  focus?: string;
  potential?: string;
  note?: string;
}

interface GeographicDistributionTabProps {
  geographicData: GeographicItem[];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

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
        <p style={{ margin: 0, fontWeight: "bold" }}>{data.name}</p>
        <p style={{ margin: "4px 0 0 0", color: COLORS.cyan[400] }}>
          ${data.amount}M total funding
        </p>
        <p style={{ margin: "4px 0 0 0", color: COLORS.gray[400], fontSize: "12px" }}>
          {data.companies} companies • ${data.avgPerCompany}M average
        </p>
      </div>
    );
  }
  return null;
};

const GeographicDistributionTab: React.FC<GeographicDistributionTabProps> = ({ geographicData }) => {
  return (
    <div style={{ backgroundColor: COLORS.gray[800], padding: "24px", borderRadius: "12px" }}>

      <h3 style={{ color: COLORS.gray[200], marginTop: 0, marginBottom: "24px", fontSize: "20px", fontWeight: "600" }}>
        Geographic Distribution
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={geographicData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.gray[700]} />
          <XAxis
            dataKey="name"
            stroke={COLORS.gray[400]}
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke={COLORS.gray[400]} fontSize={12} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="amount" name="Total Funding ($M)" fill={COLORS.cyan[500]} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      <div style={{
        backgroundColor: "#ef4444",
        color: COLORS.gray[100],
        padding: "12px",
        borderRadius: "8px",
        marginTop: "16px",
        marginBottom: "24px",
        display: "flex",
        alignItems: "center"
      }}>
        <AlertTriangle size={16} style={{ marginRight: "8px" }} />
        <span style={{ fontSize: "13px" }}>
          High Risk: Top 5 countries control 92.3% of all funding
        </span>
      </div>

      <div style={{ marginTop: "24px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "16px" }}>
        {geographicData.map((country, index) => (
          <div key={country.name} style={{
            backgroundColor: COLORS.gray[900],
            padding: "16px",
            borderRadius: "8px",
            border: `1px solid ${COLORS.gray[700]}`
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
              <h4 style={{ color: COLORS.gray[200], margin: 0, fontSize: "16px" }}>{country.name}</h4>
              <span style={{ color: COLORS.cyan[400], fontWeight: "bold" }}>${country.amount}M</span>
            </div>
            <div style={{ color: COLORS.gray[400], fontSize: "12px" }}>
              {country.companies} companies • ${country.avgPerCompany}M average
            </div>
            <div style={{ color: COLORS.gray[500], fontSize: "11px", marginTop: "4px" }}>
              {country.efficiency && `Efficiency: ${country.efficiency}`}
              {country.strategy && `Strategy: ${country.strategy}`}
              {country.advantage && `Advantage: ${country.advantage}`}
              {country.focus && `Focus: ${country.focus}`}
              {country.potential && `Potential: ${country.potential}`}
              {country.note && country.note}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GeographicDistributionTab;
