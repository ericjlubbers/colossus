import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Colossus",
  description: "Self-hosted fitness tracker",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.className} bg-gray-950 text-gray-100 min-h-screen`}
      >
        <Providers>
          <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center h-14">
              <Link
                href="/"
                className="text-lg font-bold tracking-tight text-white"
              >
                Colossus
              </Link>
              <div className="ml-8 flex gap-6 text-sm font-medium text-gray-400">
                <Link
                  href="/exercises"
                  className="hover:text-white transition-colors"
                >
                  Exercises
                </Link>
              </div>
            </div>
          </nav>
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
