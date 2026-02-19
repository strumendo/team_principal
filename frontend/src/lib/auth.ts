/**
 * NextAuth.js v5 configuration with Credentials provider.
 * Configuracao do NextAuth.js v5 com provedor de Credenciais.
 */
import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { authApi } from "./api-client";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const { data, error } = await authApi.login(
          credentials.email as string,
          credentials.password as string,
        );

        if (error || !data) {
          return null;
        }

        // Decode the JWT to get user info
        // Decodifica o JWT para obter informacoes do usuario
        const payload = JSON.parse(
          Buffer.from(data.access_token.split(".")[1], "base64").toString(),
        );

        return {
          id: payload.sub,
          email: credentials.email as string,
          fullName: "",
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        const u = user as unknown as {
          id: string;
          email: string;
          fullName: string;
          accessToken: string;
          refreshToken: string;
        };
        token.id = u.id;
        token.email = u.email;
        token.fullName = u.fullName;
        token.accessToken = u.accessToken;
        token.refreshToken = u.refreshToken;
      }
      return token;
    },
    async session({ session, token }) {
      const t = token as unknown as {
        id: string;
        email: string;
        fullName: string;
        accessToken: string;
        refreshToken: string;
      };
      session.user.id = t.id;
      session.user.email = t.email;
      (session.user as unknown as { fullName: string }).fullName = t.fullName;
      (session as unknown as { accessToken: string }).accessToken = t.accessToken;
      (session as unknown as { refreshToken: string }).refreshToken = t.refreshToken;
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
});
