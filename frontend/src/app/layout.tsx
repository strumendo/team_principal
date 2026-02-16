import type { Metadata } from "next";
import { Inter } from "next/font/google";
import AuthSessionProvider from "@/components/auth/session-provider";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TeamPrincipal",
  description:
    "E-Sports Racing Management Platform / Plataforma de Gerenciamento de E-Sports Racing",
};

/**
 * Root layout wrapping all pages.
 * Layout raiz que envolve todas as paginas.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthSessionProvider>{children}</AuthSessionProvider>
      </body>
    </html>
  );
}
