import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Acadea Ticket Drafter",
  description:
    "Interview-based drafting tool for Acadea support tickets. Chat, review, copy into Zendesk.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
