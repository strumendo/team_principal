import Link from "next/link";

/**
 * Register page placeholder.
 * Placeholder da pagina de registro.
 */
export default function RegisterPage() {
  return (
    <div>
      <h2 className="mb-6 text-center text-2xl font-bold text-gray-900">
        Register / Registrar
      </h2>
      <p className="mb-4 text-center text-gray-500">
        Registration will be implemented in PR-8.
      </p>
      <p className="text-center text-sm text-gray-400">
        <Link href="/login" className="text-primary-600 hover:underline">
          Already have an account? Login / Ja tem conta? Faca login
        </Link>
      </p>
    </div>
  );
}
