"use client";

import FundingChart from "../components/Homepage/FundingChart";
import Announcements from "../components/Homepage/Announcements";
import {
  Section1Text,
  Section2Text,
  Section3Text,
} from "@/components/ui/adaptive-text";
import { TrendingUp, MapPin, Users, Briefcase, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      {/* Hero Section */}
      <section
        className="py-16 relative min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "var(--color-background-section-1)" }}
      >
        {/* Background Africa Outline */}
        <div className="absolute inset-0 flex justify-center items-center z-0 opacity-10">
          <img
            src="/africa-outline-grey.png"
            alt="Africa outline"
            width={800}
            height={800}
            className="object-contain"
          />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              African AI Innovation Archive
            </div>

            <Section1Text
              as="h1"
              className="text-6xl md:text-8xl font-bold mb-6 tracking-tight"
            >
              African AI by the Numbers.
            </Section1Text>

            <Section1Text
              as="p"
              variant="paragraph"
              className="text-xl md:text-2xl max-w-3xl mx-auto"
            >
             Since 2023, over $1.2 billion has been invested in African AI ventures across the continent—most in fintech, few in health.
             We are aggregating open data on AI innovations—funded and unfunded, commercial and academic—to better understand where innovation is happening, who it serves, and who it is leaving behind.
            </Section1Text>
          </div>
        </div>
      </section>

      {/* Funding Analysis Section */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Section2Text as="h2" className="text-3xl font-bold mb-4">
              African AI Investment Analysis
            </Section2Text>
            <Section2Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-2xl mx-auto"
            >
              A comprehensive look at the data behind these investments.
            </Section2Text>
          </div>
          <FundingChart />
        </div>
      </section>

      {/* Announcements Section */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Section2Text as="h2" className="text-3xl font-bold mb-4">
              Major Funding Announcements
            </Section2Text>
            <Section2Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-2xl mx-auto"
            >
              At least $4.6 billion more funding has been announced by key
              players in both industry and the development sector.
            </Section2Text>
          </div>
          <Announcements />
        </div>
      </section>

      {/* Equity Tracking Section */}
      <section
        className="py-20"
        style={{ backgroundColor: "var(--color-background-section-3)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Section3Text as="h2" className="text-4xl font-bold mb-6">
              Documentation for Equitable Development
            </Section3Text>
            <Section3Text
              as="p"
              variant="paragraph"
              className="text-xl max-w-4xl mx-auto leading-relaxed"
              style={{ color: "var(--color-text-paragraph-section-3)" }}
            >
              Documenting these innovations systematically during an
              unprecedented time of growth for the African continent and
              ensuring that key indicators of equity remain at the centre of
              this development.
            </Section3Text>
          </div>

          {/* Equity Cards */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {/* Card 1: Geographical Concentration */}
            <div
              className="p-8 rounded-2xl border transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-105 hover:-translate-y-1"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div
                className="p-3 rounded-lg mb-6 inline-block"
                style={{
                  backgroundColor: "var(--color-primary-background)",
                }}
              >
                <MapPin
                  className="h-6 w-6"
                  style={{ color: "var(--color-primary)" }}
                />
              </div>
              <h3
                className="text-xl font-bold mb-4"
                style={{ color: "var(--color-card-foreground)" }}
              >
                Geographic Concentration
              </h3>
              <p
                className="text-base mb-4"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                Tracking how AI innovation expands beyond the current
                concentration in just 4 major urban centers to serve all African
                communities.
              </p>
            </div>

            {/* Card 2: Sectoral Alignment */}
            <div
              className="p-8 rounded-2xl border transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-105 hover:-translate-y-1"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div
                className="p-3 rounded-lg mb-6 inline-block"
                style={{
                  backgroundColor: "var(--color-info-background)",
                }}
              >
                <Briefcase
                  className="h-6 w-6"
                  style={{ color: "var(--color-info)" }}
                />
              </div>
              <h3
                className="text-xl font-bold mb-4"
                style={{ color: "var(--color-card-foreground)" }}
              >
                Sectoral Alignment
              </h3>
              <p
                className="text-base mb-4"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                Documenting how AI investment aligns with African priorities
                and sectors that employ the majority of Africa's workforce:
                agriculture, manufacturing, and health.
              </p>
            </div>

            {/* Card 3: Gender Equity */}
            <div
              className="p-8 rounded-2xl border transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-105 hover:-translate-y-1"
              style={{
                backgroundColor: "var(--color-card)",
                borderColor: "var(--color-border)",
              }}
            >
              <div
                className="p-3 rounded-lg mb-6 inline-block"
                style={{
                  backgroundColor: "var(--color-accent-background)",
                }}
              >
                <Users
                  className="h-6 w-6"
                  style={{ color: "var(--color-accent)" }}
                />
              </div>
              <h3
                className="text-xl font-bold mb-4"
                style={{ color: "var(--color-card-foreground)" }}
              >
                Women-Led Innovation
              </h3>
              <p
                className="text-base mb-4"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                Documenting investments made to women-led innovations at a time
                when investment in female entrepreneurs is at its lowest since
                2019.
              </p>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <Section3Text
              as="h3"
              className="text-3xl font-bold mb-6"
              style={{ color: "var(--color-foreground)" }}
            >
              Join Us in Documenting These Stories
            </Section3Text>
            <Section3Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-3xl mx-auto mb-8"
              style={{ color: "var(--color-text-paragraph-section-3)" }}
            >
              Help us track, verify, and showcase the stories of African AI
              innovation and the brilliant innovators behind it. Together, we can
              help ensure this unprecedented growth phase serves all of Africa
              equitably.
            </Section3Text>
            <Link href="/about#contact">
              <button
                className="inline-flex items-center px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 hover:opacity-90 hover:scale-105"
                style={{
                  backgroundColor: "var(--color-primary)",
                  color: "var(--color-primary-foreground)",
                }}
              >
                Get Involved
                <ArrowRight className="ml-2 h-5 w-5" />
              </button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
