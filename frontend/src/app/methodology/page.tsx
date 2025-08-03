"use client";

import {
  Globe,
  Search,
  Zap,
  CheckCircle,
  ArrowRight,
  Database,
  Code,
  Server,
  Monitor,
  Shield,
  Users,
  TrendingUp,
  Target,
} from "lucide-react";
import React from "react";
import {
  Section1Text,
  Section2Text,
  Section3Text,
  Section4Text,
} from "@/components/ui/adaptive-text";

export default function MethodologyPage() {
  const stages = [
    {
      number: "01",
      title: "Community Data Collection",
      subtitle: "Comprehensive",
      description:
        "Data collection begins with published academic evaluations, grant reports, news archives, and digital project documentation—capturing innovations whether celebrated or overlooked.",
      metrics: [
        "85-90% coverage rate",
        "500-800 daily opportunities",
        "Real-time updates",
      ],
      icon: <Globe />,
    },
    {
      number: "02",
      title: "Source Verification",
      subtitle: "Accuracy",
      description:
        "Multi-source validation and traceability for every data point—ensuring accuracy through cross-referencing, source weighting, and structured documentation.",
      metrics: ["Multi-source validation", "Format standardization", "95% uptime"],
      icon: <Search />,
    },
    {
      number: "03",
      title: "Knowledge Enhancement",
      subtitle: "Context",
      description:
        "Strategic enrichment of project records with sectoral, geographic, and institutional context—ensuring the dataset reflects not just what exists, but what it means.",
      metrics: [
        "≥70% relevance scoring",
        "90% field completion",
        "Contextual enrichment",
      ],
      icon: <Zap />,
    },
  ];

  const techStack = [
    {
      category: "Backend",
      icon: <Server />,
      technologies: [
        "PostgreSQL with spatial extensions",
        "FastAPI async processing",
        "Python ML pipeline",
        "Crawl4AI automation",
      ],
    },
    {
      category: "Frontend",
      icon: <Monitor />,
      technologies: [
        "Next.js 14 with TypeScript",
        "Recharts visualization",
        "Tailwind CSS design system",
        "React Server Components",
      ],
    },
    {
      category: "Infrastructure",
      icon: <Shield />,
      technologies: [
        "Docker containerization",
        "OAuth 2.0 security",
        "Real-time monitoring",
        "Horizontal scaling",
      ],
    },
  ];

  const qualityMetrics = [
    {
      label: "Field Completion",
      target: "90%+",
      current: "87%",
    },
    {
      label: "Accuracy Rate",
      target: "95%+",
      current: "96%",
    },
    {
      label: "Max Latency",
      target: "24h",
      current: "18h",
    },
    {
      label: "Country Coverage",
      target: "54",
      current: "54",
    },
  ];

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      {/* Hero Section */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-1)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Technical Documentation Badge */}
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
            >
              <Code className="h-4 w-4 mr-2" />
              Technical Methodology
            </div>

            <Section1Text
              as="h1"
              className="text-4xl md:text-6xl font-bold mb-6"
            >
              Methodology
            </Section1Text>

            <Section1Text
              as="p"
              variant="paragraph"
              className="text-xl max-w-4xl mx-auto leading-relaxed"
            >
              A continent-scale system for capturing AI innovation—combining 
              automation, verification, and contextual research to support inclusive, 
              evidence-based decision-making.
            </Section1Text>
          </div>
        </div>
      </section>

      {/* Three-Stage Pipeline */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Three-Stage Data Collection Pipeline
            </h2>
            <p className="text-lg text-white">Volume → Depth → Precision</p>
          </div>

          <div className="grid md:grid-cols-3 gap-10 mb-16">
            {stages.map((stage, index) => (
              <div key={index} className="relative group">
                <div
                  className="p-8 rounded-xl shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 border-l-4"
                  style={{
                    backgroundColor: "var(--color-card)",
                    borderLeftColor:
                      index === 0
                        ? "var(--color-primary)"
                        : index === 1
                          ? "var(--color-info)"
                          : "var(--color-accent)",
                  }}
                >
                  <div className="flex items-center mb-6">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center mr-5 border-2"
                      style={{
                        backgroundColor:
                          index === 0
                            ? "var(--color-primary)"
                            : index === 1
                              ? "var(--color-info)"
                              : "var(--color-accent)",
                        borderColor:
                          index === 0
                            ? "var(--color-primary)"
                            : index === 1
                              ? "var(--color-info)"
                              : "var(--color-accent)",
                        color: "white",
                      }}
                    >
                      {React.cloneElement(stage.icon, { className: "h-8 w-8" })}
                    </div>
                    <div>
                      <div
                        className="text-sm font-bold"
                        style={{
                          color:
                            index === 0
                              ? "var(--color-primary)"
                              : index === 1
                                ? "var(--color-info)"
                                : "var(--color-accent)",
                        }}
                      >
                        STAGE {stage.number}
                      </div>
                      <div className="text-xl font-semibold text-gray-800">
                        {stage.title}
                      </div>
                      <div
                        className="text-md font-medium"
                        style={{
                          color:
                            index === 0
                              ? "var(--color-primary)"
                              : index === 1
                                ? "var(--color-info)"
                                : "var(--color-accent)",
                        }}
                      >
                        {stage.subtitle}
                      </div>
                    </div>
                  </div>

                  <p className="mb-6 h-24 text-gray-600">{stage.description}</p>

                  <div className="space-y-3">
                    {stage.metrics.map((metric, idx) => (
                      <div key={idx} className="flex items-center text-sm">
                        <CheckCircle
                          className="h-5 w-5 mr-3"
                          style={{
                            color:
                              index === 0
                                ? "var(--color-primary)"
                                : index === 1
                                  ? "var(--color-info)"
                                  : "var(--color-accent)",
                          }}
                        />
                        <span className="text-gray-600">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {index < stages.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-5 transform -translate-y-1/2 group-hover:scale-125 transition-transform">
                    <ArrowRight
                      className="h-10 w-10"
                      style={{ color: "var(--color-muted-foreground)" }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pipeline Flow Diagram */}
          <div
            className="p-8 rounded-2xl shadow-xl border"
            style={{
              backgroundColor: "var(--color-card)",
              borderColor: "var(--color-border)",
            }}
          >
            <h3 className="text-2xl font-semibold mb-12 text-center text-gray-800">
              Complete Pipeline Flow
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-between space-y-6 md:space-y-0 md:space-x-6">
              {[
                {
                  icon: <Database className="h-8 w-8" />,
                  title: "Primary Data Source Aggregation",
                  subtitle: "Peer-reviewed, public, and grey literature",
                  color: "var(--color-primary)", // Input
                },
                {
                  icon: <Code className="h-8 w-8" />,
                  title: "Targeted Search",
                  subtitle: "Gap-filling with programmatic queries and filters",
                  color: "var(--color-info)", // Processing
                },
                {
                  icon: <Search className="h-8 w-8" />,
                  title: "Intelligent Scraping",
                  subtitle: "Automation for structure, not discovery",
                  color: "var(--color-accent)", // Validation
                },
                {
                  icon: <CheckCircle className="h-8 w-8" />,
                  title: "Structured Record Generation",
                  subtitle: "Validated, contextualized, query-ready data",
                  color: "var(--color-success)", // Output
                },
              ].map((item, index, arr) => (
                <React.Fragment key={index}>
                  <div className="text-center group cursor-pointer">
                    <div
                      className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-3 border-2 group-hover:scale-110 transition-transform"
                      style={{
                        backgroundColor: item.color,
                        borderColor: item.color,
                        color: "white",
                      }}
                    >
                      {item.icon}
                    </div>
                    <div className="text-md font-medium text-gray-800">
                      {item.title}
                    </div>
                    <div className="text-sm text-gray-600">{item.subtitle}</div>
                  </div>
                  {index < arr.length - 1 && (
                    <ArrowRight
                      className="hidden md:block h-10 w-10 stroke-2"
                      style={{ color: "var(--color-muted-foreground)" }}
                    />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-3)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Technology Stack
            </h2>
            <p className="text-lg text-white">
              Modern, scalable architecture built for African AI intelligence
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-10">
            {techStack.map((stack, index) => (
              <div
                key={index}
                className="p-8 rounded-2xl border-2 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                style={{
                  backgroundColor: "var(--color-card)",
                  borderColor:
                    index === 0
                      ? "var(--color-primary)"
                      : index === 1
                        ? "var(--color-info)"
                        : "var(--color-accent)",
                }}
              >
                <div className="flex items-center mb-5">
                  <div
                    style={{
                      color:
                        index === 0
                          ? "var(--color-primary)"
                          : index === 1
                            ? "var(--color-info)"
                            : "var(--color-accent)",
                    }}
                  >
                    {React.cloneElement(stack.icon, { className: "h-8 w-8" })}
                  </div>
                  <h3
                    className="text-2xl font-semibold ml-4"
                    style={{
                      color:
                        index === 0
                          ? "var(--color-primary)"
                          : index === 1
                            ? "var(--color-info)"
                            : "var(--color-accent)",
                    }}
                  >
                    {stack.category}
                  </h3>
                </div>
                <ul className="space-y-3">
                  {stack.technologies.map((tech, idx) => (
                    <li
                      key={idx}
                      className="text-md flex items-center"
                      style={{ color: "var(--color-muted-foreground)" }}
                    >
                      <div
                        className="w-2.5 h-2.5 rounded-full mr-3 border"
                        style={{
                          backgroundColor: "var(--color-card)",
                          borderColor:
                            index === 0
                              ? "var(--color-primary)"
                              : index === 1
                                ? "var(--color-info)"
                                : "var(--color-accent)",
                        }}
                      ></div>
                      {tech}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quality Metrics */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-4)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Data Quality & Performance
            </h2>
            <p className="text-lg text-white">
              Rigorous validation ensuring reliable intelligence
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {qualityMetrics.map((metric, index) => (
              <div
                key={index}
                className="p-6 rounded-2xl shadow-lg text-center hover:scale-105 transition-transform duration-300 border"
                style={{
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)",
                }}
              >
                <div
                  className="text-5xl font-bold mb-2"
                  style={{
                    color:
                      index === 0
                        ? "var(--color-primary)"
                        : index === 1
                          ? "var(--color-info)"
                          : index === 2
                            ? "var(--color-accent)"
                            : "#22c55e",
                  }}
                >
                  {metric.current}
                </div>
                <div className="text-md font-medium mb-1 text-gray-800">
                  {metric.label}
                </div>
                <div className="text-sm text-gray-600">
                  Target: {metric.target}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Roadmap Section */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-4)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
            >
              <Target className="h-4 w-4 mr-2" />
              Strategic Evolution
            </div>
            <Section4Text
              as="h2"
              className="text-4xl md:text-5xl font-bold mb-6"
            >
              From Funding Tracker to Innovation Archive
            </Section4Text>
            <Section4Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-4xl mx-auto leading-relaxed"
            >
              Having completed our technical infrastructure, TAIFA-FIALA is now in the critical data gathering phase—combining 
              automated pipeline intelligence with trusted partner collaboration to build the definitive archive of African AI innovation.
            </Section4Text>
          </div>

          <div className="grid md:grid-cols-2 gap-12 mb-16">
            {/* Phase 1 */}
            <div
              className="p-8 rounded-2xl border"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div className="flex items-center mb-6">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center mr-4"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                >
                  <span className="text-lg font-bold">1</span>
                </div>
                <div>
                  <h3
                    className="text-xl font-semibold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    Data Gathering & Pipeline Integration
                  </h3>
                  <p
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Current Phase (Q3-Q4 2025)
                  </p>
                </div>
              </div>
              <ul
                className="space-y-3 text-sm"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 mr-2 mt-0.5 text-green-500 flex-shrink-0" />
                  Technical scraping infrastructure and relational database architecture
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 mr-2 mt-0.5 text-green-500 flex-shrink-0" />
                  Integration of StartupList Africa's $803M verified startup dataset
                </li>
                <li className="flex items-start">
                  <ArrowRight className="h-4 w-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                  Passive partner input systems for direct project data sharing
                </li>
                <li className="flex items-start">
                  <ArrowRight className="h-4 w-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                  Building trust relationships with African AI innovators and funders
                </li>
              </ul>
            </div>

            {/* Phase 2 */}
            <div
              className="p-8 rounded-2xl border"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div className="flex items-center mb-6">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center mr-4"
                  style={{
                    backgroundColor: "var(--color-accent)",
                    color: "var(--color-accent-foreground)",
                  }}
                >
                  <span className="text-lg font-bold">2</span>
                </div>
                <div>
                  <h3
                    className="text-xl font-semibold"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    Trusted Partner Showcase Platform
                  </h3>
                  <p
                    className="text-sm"
                    style={{ color: "var(--color-muted-foreground)" }}
                  >
                    Target: January 2026
                  </p>
                </div>
              </div>
              <ul
                className="space-y-3 text-sm"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                <li className="flex items-start">
                  <ArrowRight className="h-4 w-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                  Projects trust TAIFA-FIALA enough to directly share achievement data
                </li>
                <li className="flex items-start">
                  <ArrowRight className="h-4 w-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                  Active innovation showcase highlighting verified African AI excellence
                </li>
                <li className="flex items-start">
                  <ArrowRight className="h-4 w-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                  Partner-driven content creation and achievement documentation
                </li>
                <li className="flex items-start">
                  <ArrowRight className="h-4 w-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                  Established reputation as credible research infrastructure for African AI
                </li>
              </ul>
            </div>
          </div>

          {/* Success Metrics */}
          <div
            className="p-8 rounded-2xl border"
            style={{
              backgroundColor: "var(--color-card)",
              borderColor: "var(--color-border)",
            }}
          >
            <h3
              className="text-2xl font-semibold mb-6 text-center"
              style={{ color: "var(--color-card-foreground)" }}
            >
              Success Metrics: Mathematical Integrity & Verified Innovation Showcase
            </h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4
                  className="text-lg font-semibold mb-4"
                  style={{ color: "var(--color-primary)" }}
                >
                  Mathematical Integrity Indicators
                </h4>
                <ul
                  className="space-y-2 text-sm"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  <li>• Interactive platform breakdowns that sum correctly to headline figures</li>
                  <li>• Every funding claim backed by verifiable documentation with clear source citations</li>
                  <li>• User confidence metrics showing trust in platform data accuracy</li>
                  <li>• Academic citations referencing platform's verification methodology</li>
                </ul>
              </div>
              <div>
                <h4
                  className="text-lg font-semibold mb-4"
                  style={{ color: "var(--color-accent)" }}
                >
                  Verified Innovation Showcase Success
                </h4>
                <ul
                  className="space-y-2 text-sm"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  <li>• Connection rate between documented innovations and verified funding sources (target: &gt;80%)</li>
                  <li>• Recognition gained by showcased innovators through verified platform data</li>
                  <li>• Replication of documented successful approaches across different contexts</li>
                  <li>• Adoption of verification methodology by other research institutions globally</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Vision Statement */}
      <section
        className="py-20"
        style={{ backgroundColor: "var(--color-background-section-1)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
            >
              <Target className="h-4 w-4 mr-2" />
              Our Vision
            </div>
            <Section1Text as="h2" className="text-4xl md:text-6xl font-bold mb-6">
              Trusted Data Centre for African AI Innovation
            </Section1Text>
            <Section1Text
              as="p"
              variant="paragraph"
              className="text-xl max-w-4xl mx-auto leading-relaxed"
            >
              Our vision is to become Africa's most trusted research infrastructure 
              for AI innovation intelligence—a humble yet rigorous scientific network 
              that transforms how we understand and support technological progress 
              across the continent.
            </Section1Text>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {[
              {
                icon: <Users />,
                title: "For Entrepreneurs & Researchers",
                description: "Recognition platform and network connections for innovation showcasing",
                color: "var(--color-primary)",
                bgColor: "var(--color-primary-background)",
              },
              {
                icon: <TrendingUp />,
                title: "For Funders & Investors", 
                description: "Evidence showcase and credible third-party validation of impact",
                color: "var(--color-info)",
                bgColor: "var(--color-info-background)",
              },
              {
                icon: <Shield />,
                title: "For Policymakers & Governments",
                description: "Evidence-based insights and data-driven strategic recommendations",
                color: "var(--color-accent)",
                bgColor: "var(--color-accent-background)",
              },
            ].map((item, index) => (
              <div
                key={index}
                className="p-8 rounded-2xl border transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-105 hover:-translate-y-1"
                style={{
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)",
                }}
              >
                <div
                  className="p-3 rounded-lg mb-6 inline-block"
                  style={{
                    backgroundColor: item.bgColor,
                  }}
                >
                  {React.cloneElement(item.icon, { 
                    className: "h-6 w-6",
                    style: { color: item.color }
                  })}
                </div>
                <h3
                  className="text-xl font-bold mb-4"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  {item.title}
                </h3>
                <p
                  className="text-base"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  {item.description}
                </p>
              </div>
            ))}
          </div>

          {/* Vision Details */}
          <div
            className="p-8 rounded-2xl border"
            style={{
              backgroundColor: "var(--color-card)",
              borderColor: "var(--color-border)",
            }}
          >
            <Section1Text
              as="p"
              variant="paragraph"
              className="text-lg leading-relaxed text-center"
              style={{ color: "var(--color-muted-foreground)" }}
            >
              A future in which the full breadth of African AI innovation is visible, valued, and directed toward human wellbeing.
              By making patterns of research, development, and investment transparent, we seek to inform decisions that move beyond hype—toward 
              equitable progress in health, education, livelihoods, and public good.
            </Section1Text>
          </div>
        </div>
      </section>
    </div>
  );
}
