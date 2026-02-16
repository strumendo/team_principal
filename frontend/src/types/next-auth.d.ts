/**
 * NextAuth.js type augmentation for custom user fields.
 * Augmentacao de tipos do NextAuth.js para campos customizados do usuario.
 */
import "next-auth";

declare module "next-auth" {
  interface User {
    id: string;
    email: string;
    fullName: string;
    accessToken: string;
    refreshToken: string;
  }

  interface Session {
    user: {
      id: string;
      email: string;
      fullName: string;
    };
    accessToken: string;
    refreshToken: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    email: string;
    fullName: string;
    accessToken: string;
    refreshToken: string;
  }
}
