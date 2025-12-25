import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Auth0Provider } from '@auth0/auth0-react';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DocQA-MS - Clinical Document Intelligence",
  description: "AI-powered clinical document query and analysis system with microservices architecture",
  icons: {
    icon: [
      { url: '/logo.png', href: '/logo.png', sizes: 'any' }
    ]
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning={true}>
        {children}
      </body>
    </html>
  );
}
