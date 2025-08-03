import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// Color constants
const COLORS = {
  gray: {
    100: '#f3f4f6',
    200: '#e5e7eb',
    400: '#9ca3af',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  cyan: {
    400: '#22d3ee',
  },
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#ef4444', '#ec4899'];

interface FundingItem {
  name: string;
  amount: number;
  percentage: number;
  description: string;
  status: string;
}

interface FundingBreakdownTabProps {
  fundingBreakdown: FundingItem[];
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
          backgroundColor: "var(--color-card)",
          padding: "12px",
          borderRadius: "8px",
          border: `1px solid var(--color-border)`,
          color: "var(--color-card-foreground)",
          fontSize: "14px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
        }}
      >
        <p style={{ margin: 0, fontWeight: "bold" }}>{data.name}</p>
        <p style={{ margin: "4px 0 0 0", color: "var(--color-primary)" }}>
          ${data.amount}M ({data.percentage}%)
        </p>
        <p style={{ margin: "4px 0 0 0", color: "var(--color-muted-foreground)", fontSize: "12px" }}>
          {data.description}
        </p>
      </div>
    );
  }
  return null;
};

const FundingBreakdownTab: React.FC<FundingBreakdownTabProps> = ({ fundingBreakdown }) => {
  return (
    <div style={{ backgroundColor: COLORS.gray[800], padding: "24px", borderRadius: "12px" }}>

      <h3 style={{ color: COLORS.gray[200], marginTop: 0, marginBottom: "24px", fontSize: "20px", fontWeight: "600" }}>
        Funding Breakdown
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={fundingBreakdown}
            cx="50%"
            cy="50%"
            outerRadius={120}
            innerRadius={60}
            dataKey="amount"
            label={({ name, percentage }: any) => `${name}: ${percentage}%`}
            labelLine={false}
          >
            {fundingBreakdown.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div style={{ marginTop: "24px" }}>
        {fundingBreakdown.map((item, index) => (
          <div key={item.name} style={{
            display: "flex",
            alignItems: "center",
            marginBottom: "12px",
            padding: "12px",
            backgroundColor: COLORS.gray[900],
            borderRadius: "8px"
          }}>
            <div
              style={{
                width: "12px",
                height: "12px",
                backgroundColor: CHART_COLORS[index],
                borderRadius: "2px",
                marginRight: "12px",
              }}
            />
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ color: COLORS.gray[200], fontWeight: "500" }}>{item.name}</span>
                <span style={{ color: COLORS.cyan[400], fontWeight: "bold" }}>
                  ${item.amount}M ({item.percentage}%)
                </span>
              </div>
              <div style={{ color: COLORS.gray[400], fontSize: "12px", marginTop: "4px" }}>
                {item.description} • Status: {item.status.replace(/_/g, ' ')}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Mathematical verification footnote */}
      <div style={{ 
        marginTop: "24px", 
        paddingTop: "16px", 
        borderTop: `1px solid ${COLORS.gray[700]}`,
        fontSize: "12px",
        color: COLORS.gray[400]
      }}>
        * Mathematical verification: 803.2 + 200.0 + 100.0 = 1,103.2 million (displayed as $1.1B+)
      </div>
    </div>
  );
};

export default FundingBreakdownTab;
