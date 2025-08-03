import { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Methodology | TAIFA-FIALA",
  description: "Technical methodology and data pipeline architecture for African AI innovation gathering",
};

export default function MethodologyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
