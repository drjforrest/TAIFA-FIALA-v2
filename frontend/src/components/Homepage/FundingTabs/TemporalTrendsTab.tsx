import React from 'react';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Color constants
const COLORS = {
  gray: {
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  cyan: {
    500: '#06b6d4',
  },
  purple: {
    400: '#a855f7',
  },
};

interface TemporalItem {
  year: number;
  amount: number;
  companies: number;
}

interface TemporalTrendsTabProps {
  temporalData: TemporalItem[];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
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
        <p style={{ margin: 0, fontWeight: "bold" }}>{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ margin: "4px 0 0 0", color: entry.color }}>
            {entry.name}: {entry.name === 'Funding ($M)' ? `$${entry.value}M` : `${entry.value} companies`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const TemporalTrendsTab: React.FC<TemporalTrendsTabProps> = ({ temporalData }) => {
  return (
    <div style={{ backgroundColor: COLORS.gray[800], padding: "24px", borderRadius: "12px" }}>

      <h3 style={{ color: COLORS.gray[200], marginTop: 0, marginBottom: "16px", fontSize: "20px", fontWeight: "600" }}>
        Temporal Trends
      </h3>

      <p style={{ color: COLORS.gray[400], marginBottom: "24px", fontSize: "14px" }}>
        Peak in 2022 ($167.7M), correction in 2023 ($17.9M), strong recovery in 2024 ($277.7M)
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={temporalData}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.gray[700]} />
          <XAxis dataKey="year" stroke={COLORS.gray[400]} />
          <YAxis stroke={COLORS.gray[400]} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="amount" name="Funding ($M)" fill={COLORS.cyan[500]} radius={[4, 4, 0, 0]} />
          <Line
            type="monotone"
            dataKey="companies"
            name="Companies"
            stroke={COLORS.purple[400]}
            strokeWidth={3}
            dot={{ fill: COLORS.purple[400], strokeWidth: 2, r: 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div style={{ marginTop: "24px", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px" }}>
        {temporalData.map((year) => (
          <div key={year.year} style={{
            backgroundColor: COLORS.gray[900],
            padding: "12px",
            borderRadius: "8px",
            textAlign: "center"
          }}>
            <div style={{ color: COLORS.cyan[500], fontWeight: "bold", fontSize: "18px" }}>{year.year}</div>
            <div style={{ color: COLORS.gray[300], fontSize: "14px" }}>${year.amount}M</div>
            <div style={{ color: COLORS.gray[400], fontSize: "12px" }}>{year.companies} companies</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemporalTrendsTab;
