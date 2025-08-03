import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

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
  yellow: {
    400: '#facc15',
    600: '#ca8a04',
  },
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

interface SectorItem {
  name: string;
  percentage: number;
  companies: number;
  rationale?: string;
}

interface SectorAnalysisTabProps {
  sectorData: SectorItem[];
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
        <p style={{ margin: "4px 0 0 0", color: COLORS.yellow[400] }}>
          {data.percentage}% of ecosystem
        </p>
        <p style={{ margin: "4px 0 0 0", color: COLORS.gray[400], fontSize: "12px" }}>
          {data.companies} companies
        </p>
        {data.rationale && (
          <p style={{ margin: "4px 0 0 0", color: COLORS.gray[500], fontSize: "11px" }}>
            {data.rationale}
          </p>
        )}
      </div>
    );
  }
  return null;
};

const SectorAnalysisTab: React.FC<SectorAnalysisTabProps> = ({ sectorData }) => {
  return (
    <div style={{ backgroundColor: COLORS.gray[800], padding: "24px", borderRadius: "12px" }}>

      <h3 style={{ color: COLORS.gray[200], marginTop: 0, marginBottom: "16px", fontSize: "20px", fontWeight: "600" }}>
        Sector Analysis
      </h3>

      <p style={{ color: COLORS.gray[400], marginBottom: "24px", fontSize: "14px" }}>
        FinTech, TalentTech, and EdTech represent 55.6% of all companies - driven by immediate commercial opportunities
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={sectorData}
            cx="50%"
            cy="50%"
            outerRadius={100}
            dataKey="percentage"
            label={({ name, percentage }: any) => `${name}: ${percentage}%`}
          >
            {sectorData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div style={{ marginTop: "24px" }}>
        <h4 style={{ color: COLORS.yellow[400], marginBottom: "16px", fontSize: "16px" }}>
          Underserved Critical Sectors
        </h4>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "12px" }}>
          {sectorData.filter(s => ['HealthTech', 'AgriTech', 'ClimateTech'].includes(s.name)).map((sector) => (
            <div key={sector.name} style={{
              backgroundColor: COLORS.gray[900],
              padding: "16px",
              borderRadius: "8px",
              border: `1px solid ${COLORS.yellow[600]}`
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ color: COLORS.yellow[400], fontWeight: "bold" }}>{sector.name}</span>
                <span style={{ color: COLORS.gray[400] }}>{sector.percentage}%</span>
              </div>
              <div style={{ color: COLORS.gray[400], fontSize: "12px" }}>
                {sector.companies} companies
              </div>
              <div style={{ color: COLORS.gray[500], fontSize: "11px", marginTop: "8px" }}>
                {sector.rationale}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SectorAnalysisTab;
