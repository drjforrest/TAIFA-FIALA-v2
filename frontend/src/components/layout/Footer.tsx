"use client";

import Link from "next/link";

export default function Footer() {
  const handleMouseEnter = (e: React.MouseEvent<HTMLAnchorElement>) => {
    (e.target as HTMLElement).style.opacity = "0.8";
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLAnchorElement>) => {
    (e.target as HTMLElement).style.opacity = "1";
  };

  const linkStyle = {
    color: "var(--color-foreground)",
    textDecoration: "none",
    transition: "opacity 0.2s ease"
  };

  return (
    <footer
      className="border-t border-border py-12"
      style={{ backgroundColor: "var(--color-background-section-1)" }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h4
              className="font-semibold mb-4"
              style={{ color: "var(--color-cyan-400)" }}
            >
              Research
            </h4>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/database" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Innovation Database
                </Link>
              </li>
              <li>
                <Link 
                  href="/methodology" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Research Methods
                </Link>
              </li>
              <li>
                <Link 
                  href="/reports" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Analysis Reports
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4
              className="font-semibold mb-4"
              style={{ color: "var(--color-cyan-300)" }}
            >
              Innovations
            </h4>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/startups" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  AI Startups
                </Link>
              </li>
              <li>
                <Link 
                  href="/institutions" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Research Centers
                </Link>
              </li>
              <li>
                <Link 
                  href="/case-studies" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Success Stories
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4
              className="font-semibold mb-4"
              style={{ color: "var(--color-green-400)" }}
            >
              Community
            </h4>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/submit" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Submit Research
                </Link>
              </li>
              <li>
                <Link 
                  href="/collaborate" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Collaborate
                </Link>
              </li>
              <li>
                <Link 
                  href="/network" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Research Network
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4
              className="font-semibold mb-4"
              style={{ color: "var(--color-gray-300)" }}
            >
              About
            </h4>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/about" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Mission
                </Link>
              </li>
              <li>
                <Link 
                  href="/team" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Research Team
                </Link>
              </li>
              <li>
                <Link 
                  href="/contact" 
                  style={linkStyle}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Contact
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-border mt-8 pt-8 text-center">
          <p style={{ color: "var(--color-foreground)" }}>
            &copy; 2025 TAIFA-FIALA. Documenting Africa's AI innovation
            ecosystem through systematic research.
          </p>
          <p className="text-sm mt-2" style={{ color: "var(--color-foreground)" }}>
            Building comprehensive evidence bases • Tracking 159+ AI startups
            • Supporting policy & investment decisions
          </p>
        </div>
      </div>
    </footer>
  );
}
