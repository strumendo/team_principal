import Link from "next/link";

/**
 * Login page placeholder.
 * Placeholder da pagina de login.
 */
export default function LoginPage() {
  return (
    <div>
      <h2 className="mb-6 text-center text-2xl font-bold text-gray-900">
        Login
      </h2>
      <p className="mb-4 text-center text-gray-500">
        Authentication will be implemented in PR-8.
      </p>
      <p className="text-center text-sm text-gray-400">
        <Link href="/register" className="text-primary-600 hover:underline">
          Don&apos;t have an account? Register / Nao tem conta? Registre-se
        </Link>
      </p>
    </div>
  );
}
