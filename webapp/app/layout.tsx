import type { Metadata, Viewport } from "next";
import "./globals.css";
import ErrorBoundary from "@/components/ui/ErrorBoundary";

export const metadata: Metadata = {
  title: "TermAI Explorer",
  description: "Terminal-inspired AI webapp with visualizations",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ErrorBoundary>{children}</ErrorBoundary>
      </body>
    </html>
  );
}
