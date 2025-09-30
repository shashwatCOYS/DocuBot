import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";

const inter = Inter({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DocuBot - AI Documentation Assistant",
  description: "Transform documentation websites into intelligent chat assistants for developers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
          <Navigation />
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
