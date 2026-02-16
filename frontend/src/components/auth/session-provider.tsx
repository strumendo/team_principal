"use client";

/**
 * NextAuth SessionProvider wrapper for client components.
 * Wrapper do SessionProvider do NextAuth para componentes client.
 */
import { SessionProvider } from "next-auth/react";

export default function AuthSessionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return <SessionProvider>{children}</SessionProvider>;
}
