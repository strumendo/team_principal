"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { signIn } from "next-auth/react";
import { authApi } from "@/lib/api-client";

/**
 * Register page with email/password/name form.
 * Pagina de registro com formulario de email/senha/nome.
 */
export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Register via API / Registra via API
    const { error: registerError } = await authApi.register(
      email,
      password,
      fullName,
    );

    if (registerError) {
      setError(registerError);
      setLoading(false);
      return;
    }

    // Auto-login after registration / Auto-login apos registro
    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    setLoading(false);

    if (result?.error) {
      setError("Registration succeeded but login failed. Please try logging in.");
    } else {
      router.push("/dashboard");
    }
  };

  return (
    <div>
      <h2 className="mb-6 text-center text-2xl font-bold text-gray-900">
        Register / Registrar
      </h2>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="fullName"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Full Name / Nome Completo
          </label>
          <input
            id="fullName"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            placeholder="John Doe"
          />
        </div>

        <div>
          <label
            htmlFor="email"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Password / Senha
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-primary-600 py-2 font-semibold text-white transition hover:bg-primary-700 disabled:opacity-50"
        >
          {loading
            ? "Registering... / Registrando..."
            : "Register / Registrar"}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-gray-500">
        <Link href="/login" className="text-primary-600 hover:underline">
          Already have an account? Login / Ja tem conta? Faca login
        </Link>
      </p>
    </div>
  );
}
