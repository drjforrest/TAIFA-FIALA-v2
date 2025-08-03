import PublicationsTable from "@/components/Publications/PublicationsTable";
import { Section1Text } from "@/components/ui/adaptive-text";

export default function PublicationsPage() {
  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      {/* Header */}
      <div
        style={{ backgroundColor: "var(--color-background-section-1)" }}
        className="shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Section1Text as="h1" className="text-3xl font-bold">
            Research Publications
          </Section1Text>
          <Section1Text as="p" variant="paragraph" className="mt-2">
            Browse African AI research publications and academic papers
          </Section1Text>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <PublicationsTable />
      </div>
    </div>
  );
}

export const metadata = {
  title: "Publications - TAIFA-FIALA Innovation Archive",
  description: "Browse African AI research publications and academic papers",
};
