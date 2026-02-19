/**
 * Middleware for route protection.
 * Middleware para protecao de rotas.
 *
 * Redirects unauthenticated users to /login for protected routes.
 * Redireciona usuarios nao autenticados para /login em rotas protegidas.
 */
export { auth as middleware } from "@/lib/auth";

export const config = {
  matcher: ["/dashboard/:path*", "/championships/:path*", "/races/:path*"],
};
