/**
 * Admin create user page.
 * Pagina admin de criacao de usuario.
 */
"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { adminUsersApi } from "@/lib/api-client";

export default function AdminCreateUserPage() {
  const { data: session } = useSession();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;

    if (password.length < 8) {
      setError("Password must be at least 8 characters. / A senha deve ter no minimo 8 caracteres.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match. / As senhas nao coincidem.");
      return;
    }

    setSaving(true);
    setError(null);
    const token = (session as unknown as { accessToken: string }).accessToken;
    const { data, error: err } = await adminUsersApi.create(token, {
      email,
      password,
      full_name: fullName,
      is_active: isActive,
    });

    if (err) {
      setError(err);
      setSaving(false);
    } else if (data) {
      router.push(`/admin/users/${data.id}`);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Link href="/admin/users" className="text-blue-600 hover:underline">
          &larr; Back to Users / Voltar para Usuarios
        </Link>
      </div>

      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Create User / Criar Usuario
      </h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="max-w-lg rounded border p-6">
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="user@example.com"
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Full Name / Nome Completo
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            placeholder="John Doe"
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Password / Senha
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            placeholder="Min. 8 characters / Min. 8 caracteres"
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Confirm Password / Confirmar Senha
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-6">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="rounded border-gray-300"
            />
            Active / Ativo
          </label>
        </div>
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Creating... / Criando..." : "Create User / Criar Usuario"}
        </button>
      </form>
    </div>
  );
}
