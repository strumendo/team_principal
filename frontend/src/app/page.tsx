import Link from "next/link";

/**
 * Landing page.
 * Pagina inicial.
 */
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center">
        <h1 className="mb-4 text-5xl font-bold text-primary-600">
          TeamPrincipal
        </h1>
        <p className="mb-8 text-xl text-gray-600">
          E-Sports Racing Management Platform
        </p>
        <div className="flex gap-4">
          <Link
            href="/login"
            className="rounded-lg bg-primary-600 px-6 py-3 font-semibold text-white transition hover:bg-primary-700"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="rounded-lg border border-primary-600 px-6 py-3 font-semibold text-primary-600 transition hover:bg-primary-50"
          >
            Register / Registrar
          </Link>
        </div>
      </div>
    </main>
  );
}
