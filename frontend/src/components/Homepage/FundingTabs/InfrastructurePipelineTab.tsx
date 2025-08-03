import React from 'react';

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
    400: '#22d3ee',
  },
  green: {
    400: '#4ade80',
  },
  yellow: {
    400: '#facc15',
  },
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

interface InfrastructureProject {
  name: string;
  amount: number;
  timeline: string;
  status: string;
}

interface InfrastructurePipelineTabProps {
  infrastructurePipeline: InfrastructureProject[];
}

const InfrastructurePipelineTab: React.FC<InfrastructurePipelineTabProps> = ({ infrastructurePipeline }) => {
  return (
    <div style={{ backgroundColor: COLORS.gray[800], padding: "24px", borderRadius: "12px" }}>

      <h3 style={{ color: COLORS.gray[200], marginTop: 0, marginBottom: "16px", fontSize: "20px", fontWeight: "600" }}>
        Infrastructure Pipeline
      </h3>

      <p style={{ color: COLORS.gray[400], marginBottom: "24px", fontSize: "14px" }}>
        Major infrastructure commitments separate from current verified funding to avoid double-counting
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))", gap: "20px" }}>
        {infrastructurePipeline.map((project, index) => (
          <div key={project.name} style={{
            backgroundColor: COLORS.gray[900],
            padding: "20px",
            borderRadius: "12px",
            border: `2px solid ${CHART_COLORS[index]}`
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <h4 style={{ color: COLORS.gray[200], margin: 0, fontSize: "16px" }}>{project.name}</h4>
              <span style={{ color: CHART_COLORS[index], fontWeight: "bold", fontSize: "18px" }}>
                ${project.amount}M
              </span>
            </div>
            <div style={{ color: COLORS.gray[400], fontSize: "14px", marginBottom: "8px" }}>
              Timeline: {project.timeline}
            </div>
            <div style={{
              color: project.status === 'deployment_beginning' ? COLORS.green[400] : COLORS.yellow[400],
              fontSize: "12px",
              fontWeight: "500"
            }}>
              Status: {project.status.replace(/_/g, ' ')}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: "24px",
        padding: "16px",
        backgroundColor: COLORS.gray[700],
        borderRadius: "8px",
        borderLeft: `4px solid ${COLORS.cyan[400]}`
      }}>
        <h4 style={{ color: COLORS.cyan[400], margin: "0 0 8px 0", fontSize: "14px" }}>
          Why Separate from Main Total?
        </h4>
        <p style={{ color: COLORS.gray[300], fontSize: "12px", margin: 0 }}>
          These infrastructure commitments represent future deployment capacity rather than current funding to startups and innovations.
          Including them in the $1.1B total would create double-counting as they will eventually fund the next generation of African AI companies.
        </p>
      </div>
    </div>
  );
};

export default InfrastructurePipelineTab;
