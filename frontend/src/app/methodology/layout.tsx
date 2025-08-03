import { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Methodology | TAIFA-FIALA",
  description: "Technical methodology and data pipeline architecture for African AI funding intelligence",
};

export default function MethodologyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
