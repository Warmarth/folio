import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Folio",
  description:
    "A practical learning platform for projects, exercises, code review, and industry mentorship.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}