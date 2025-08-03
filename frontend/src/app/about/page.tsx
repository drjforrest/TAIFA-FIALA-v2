import {
  Section1Text,
  Section2Text,
  Section3Text,
  Section4Text,
} from "@/components/ui/adaptive-text";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui";
import {
  Mail,
  MapPin,
  Users,
  Calendar,
  Heart,
  Globe,
  Shield,
  Target,
  Award,
  Lightbulb,
} from "lucide-react";
import { Metadata } from "next";
import ContactForm from "@/components/contact/ContactForm";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About TAIFA-FIALA | Leadership & Mission",
  description:
    "Learn about TAIFA-FIALA's mission to promote transparency, equity, and accountability in AI funding across Africa. Meet our leadership team and discover our vision for inclusive AI development.",
  keywords: [
    "TAIFA-FIALA",
    "African AI",
    "funding transparency",
    "equity in technology",
    "leadership team",
    "AI development Africa",
  ],
};

export default function AboutPage() {
  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      {/* Section 1: Hero Section - Darkest Background */}
      <section
        className="py-16 relative"
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
              <Heart className="h-4 w-4 mr-2" />
              Our Story & Mission
            </div>

            <Section1Text
              as="h1"
              className="text-4xl md:text-6xl font-bold mb-12 leading-tight"
            >
              About TAIFA-FIALA
            </Section1Text>

            {/* Mission Statement Card */}
            <Card
              className="max-w-5xl mx-auto mb-12"
              style={{ backgroundColor: "var(--color-card)" }}
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-center">
                  <Target
                    className="h-6 w-6 mr-3"
                    style={{ color: "var(--color-primary)" }}
                  />
                  <span style={{ color: "var(--color-card-foreground)" }}>
                    Our Mission
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p
                  className="text-lg leading-relaxed"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  To build and maintain an open, structured, and continuously updated dataset of AI innovations across Africa—capturing efforts across health, finance, agriculture, education, and beyond—to support more inclusive, evidence-based understanding of how AI is shaping lives across the continent.
                </p>
              </CardContent>
            </Card>

            {/* Core Values */}
            <div className="flex flex-wrap justify-center gap-6 md:gap-8">
              <div className="text-center">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3"
                  style={{
                    backgroundColor: "var(--color-accent)",
                    color: "var(--color-accent-foreground)",
                  }}
                >
                  <Lightbulb className="h-6 w-6" />
                </div>
                <Section1Text as="div" className="text-sm font-semibold">
                  Transparency
                </Section1Text>
              </div>
              <div className="text-center">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3"
                  style={{
                    backgroundColor: "var(--color-info)",
                    color: "var(--color-info-foreground)",
                  }}
                >
                  <Users className="h-6 w-6" />
                </div>
                <Section1Text as="div" className="text-sm font-semibold">
                  Equity
                </Section1Text>
              </div>
              <div className="text-center">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3"
                  style={{
                    backgroundColor: "var(--color-secondary)",
                    color: "var(--color-secondary-foreground)",
                  }}
                >
                  <Award className="h-6 w-6" />
                </div>
                <Section1Text as="div" className="text-sm font-semibold">
                  Accountability
                </Section1Text>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: Leadership Team */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-2)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-3"
              style={{
                backgroundColor: "var(--color-info)",
                color: "var(--color-info-foreground)",
              }}
            >
              <Users className="h-4 w-4 mr-2" />
              Meet Our Team
            </div>
            <Section2Text as="h2" className="text-4xl font-bold mb-6">
              Leadership Team
            </Section2Text>
            <Section2Text
              as="p"
              variant="paragraph"
              className="text-lg max-w-3xl mx-auto"
            >
              Combining expertise in data science and a passion for local
              development that serves community needs.
            </Section2Text>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto mt-12">
            {/* Executive Director */}
            <Card
              className="hover:shadow-lg transition-all duration-300"
              style={{ backgroundColor: "var(--color-card)" }}
            >
              <CardContent className="p-6 md:p-8 text-center">
                <div
                  className="w-24 h-24 rounded-full mx-auto mb-6 mt-4 flex items-center justify-center"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                >
                  <Users className="h-12 w-12" />
                </div>

                <h3
                  className="text-2xl font-bold mb-2"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  Hinda Ruton
                </h3>
                <div
                  className="inline-block font-semibold px-4 py-2 rounded-full text-sm mb-6"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                >
                  Executive Director
                </div>

                <p
                  className="leading-relaxed mb-6 text-left"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  Hinda Ruton is the CEO and Founder of Africa Quantitative Sciences, Rwanda's premier data analytics firm. He and his team at AQS bring deep expertise in data science to generate actionable insights from the data collected. With a focus on public health outcome analytics and global health security, he has pioneered innovative data-driven solutions that enhance disease monitoring, support vaccine programs, and strengthen health systems. His vision bridges novel technologies with the operational realities of African institutions and the lived needs of local communities.
                </p>

                <div
                  className="flex justify-center items-center text-sm px-4 py-2 rounded-full"
                  style={{
                    backgroundColor: "var(--color-muted)",
                    color: "var(--color-muted-foreground)",
                  }}
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  <span className="font-medium">Kigali, Rwanda</span>
                </div>
              </CardContent>
            </Card>

            {/* Scientific Director */}
            <Card
              className="hover:shadow-lg transition-all duration-300"
              style={{ backgroundColor: "var(--color-card)" }}
            >
              <CardContent className="p-6 md:p-8 text-center">
                <div
                  className="w-24 h-24 rounded-full mx-auto mb-6 mt-4 flex items-center justify-center"
                  style={{
                    backgroundColor: "var(--color-accent)",
                    color: "var(--color-accent-foreground)",
                  }}
                >
                  <Users className="h-12 w-12" />
                </div>

                <h3
                  className="text-2xl font-bold mb-2"
                  style={{ color: "var(--color-card-foreground)" }}
                >
                  Dr. Jamie Forrest
                </h3>
                <div
                  className="inline-block font-semibold px-4 py-2 rounded-full text-sm mb-6"
                  style={{
                    backgroundColor: "var(--color-accent)",
                    color: "var(--color-accent-foreground)",
                  }}
                >
                  Scientific Director
                </div>

                <p
                  className="leading-relaxed mb-6 text-left"
                  style={{ color: "var(--color-muted-foreground)" }}
                >
                  Dr. Jamie Forrest holds a PhD in Population and Public Health from the University of British Columbia in Vancouver, Canada, and has dedicated his career to addressing health and development challenges in African countries. With years of experience living and working in Rwanda, and earlier roles in South Africa, he brings a grounded understanding of African development contexts. His expertise spans digital health, clinical research methods, and implementation science—with a focus on equity-driven innovations like those powering TAIFA-FIALA’s commitment to making AI development more accountable to African realities.
                </p>

                <div
                  className="flex justify-center items-center text-sm px-4 py-2 rounded-full"
                  style={{
                    backgroundColor: "var(--color-muted)",
                    color: "var(--color-muted-foreground)",
                  }}
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  <span className="font-medium">Canada / Rwanda</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Section 3: Initiative Background */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-3)" }}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <div
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-3"
              style={{
                backgroundColor: "var(--color-secondary)",
                color: "var(--color-secondary-foreground)",
              }}
            >
              <Lightbulb className="h-4 w-4 mr-2" />
              Our Foundation
            </div>
            <Section3Text as="h2" className="text-4xl font-bold mb-8">
              Why TAIFA-FIALA?
            </Section3Text>
          </div>

          <Card
            className="mt-16 p-16"
            style={{ backgroundColor: "var(--color-card)" }}
          >
              <div className="max-w-4xl mx-auto">
                <Section3Text
                  as="p"
                  variant="paragraph"
                  className="text-xl leading-relaxed mb-6"
                >
                  Research gaps continue to obscure African AI innovations, while limited capacity for rigorous evaluation leaves critical lessons undocumented. This weakens the ecosystem’s ability to learn, adapt, and replicate success. Over $130 billion has been announced globally for AI development since 2020—but Africa’s contributions, outcomes, and innovations are often left untracked.
                </Section3Text>

                <div
                  className="p-6 rounded-xl mb-6"
                  style={{
                    backgroundColor: "var(--color-primary)",
                    color: "var(--color-primary-foreground)",
                  }}
                >
                  <p className="text-lg font-semibold">
                    We founded TAIFA-FIALA to bridge the gap between bold funding promises and the lived record of African AI innovation.
                  </p>
                </div>

                <Section3Text
                  as="p"
                  variant="paragraph"
                  className="text-lg leading-relaxed"
                >
                  Through our participatory systematic review methodology, we build the evidence base needed to showcase African AI brilliance. Innovation stories inspire future innovators. Implementation lessons help others avoid pitfalls. And visible patterns of success guide smarter investment. TAIFA-FIALA is a shared space where funders celebrate impact, innovators gain recognition, and researchers access rigorous, actionable evidence.
                </Section3Text>
              </div>
          </Card>
        </div>
      </section>

      {/* Section 4: Coming Soon - Advisory Board */}
      <section
        className="py-16"
        style={{ backgroundColor: "var(--color-background-section-4)" }}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Card
            className="mt-12 p-16 text-center"
            style={{ backgroundColor: "var(--color-card)" }}
          >
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6"
                style={{
                  backgroundColor: "var(--color-accent)",
                  color: "var(--color-accent-foreground)",
                }}
              >
                <Calendar className="h-8 w-8" />
              </div>
              <div
                className="inline-block font-semibold px-4 py-2 rounded-full text-sm mb-4"
                style={{
                  backgroundColor: "var(--color-accent)",
                  color: "var(--color-accent-foreground)",
                }}
              >
                Coming Soon
              </div>
              <Section4Text as="h2" className="text-3xl font-bold mb-4">
                Advisory Board
              </Section4Text>
              <Section4Text
                as="p"
                variant="paragraph"
                className="text-lg max-w-3xl mx-auto leading-relaxed mb-6"
              >
                We are assembling a distinguished advisory board of African AI
                researchers, policy makers, and development practitioners to
                guide TAIFA-FIALA's strategic direction and ensure our work
                serves the broader African AI ecosystem.
              </Section4Text>
              <div
                className="inline-flex items-center px-6 py-3 rounded-full"
                style={{
                  backgroundColor: "var(--color-muted)",
                  color: "var(--color-muted-foreground)",
                }}
              >
                <Globe className="h-4 w-4 mr-2" />
                <span className="font-medium">Announcements forthcoming</span>
              </div>
          </Card>
        </div>
      </section>

      {/* Contact & Collaboration Section */}
      <section
        id="contact"
        className="py-16"
        style={{
          background: `linear-gradient(135deg, var(--color-primary), var(--color-accent))`,
        }}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-white/20 border border-white/30 rounded-full text-sm font-medium text-white mb-6">
              <Mail className="h-4 w-4 mr-2" />
              Get In Touch
            </div>
            <h2 className="text-4xl font-bold text-white mb-6">
              Contact & Collaboration
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-3xl mx-auto">
              Partner with us in building transparent, equitable AI development
              across Africa
            </p>

            {/* Funding Statement */}
            <Card className="max-w-4xl mx-auto mb-12 bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 p-16">
                <div className="flex items-center justify-center mb-4">
                  <Heart className="h-6 w-6 text-blue-600 mr-3" />
                  <span className="text-lg font-semibold text-blue-800">
                    Self-Supporting Initiative
                  </span>
                </div>
                <p className="text-blue-700 leading-relaxed text-lg">
                  <strong className="text-blue-800">
                    TAIFA-FIALA is currently self-supporting.
                  </strong>{" "}
                  If you are interested in helping us grow our reach and expand
                  our platform to serve more African communities, please get in
                  touch with us below.
                </p>
            </Card>
          </div>

          <div className="mb-16">
            <ContactForm />
          </div>

          <div className="text-center">
            <Card className="bg-gradient-to-br from-emerald-50 to-teal-100 border border-emerald-200 max-w-4xl mx-auto p-16">
                <div className="flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-emerald-600 mr-3" />
                  <span className="text-lg font-semibold text-emerald-800">
                    Transparency Note
                  </span>
                </div>
                <p className="text-emerald-700 leading-relaxed mb-4">
                  <strong className="text-emerald-800">
                    TAIFA-FIALA operates as an independent initiative.
                  </strong>
                </p>
                <p className="text-sm text-emerald-600 leading-relaxed">
                  Our funding sources and methodology are fully documented to
                  ensure accountability in our mission to promote transparency
                  in African AI development.
                </p>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
}
