/**
 * Admin create role page.
 * Pagina admin de criacao de papel.
 */
"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { adminRolesApi } from "@/lib/api-client";

export default function AdminCreateRolePage() {
  const { data: session } = useSession();
  const router = useRouter();

  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;

    setSaving(true);
    setError(null);
    const token = (session as unknown as { accessToken: string }).accessToken;
    const { data, error: err } = await adminRolesApi.create(token, {
      name,
      display_name: displayName,
      description: description || undefined,
    });

    if (err) {
      setError(err);
      setSaving(false);
    } else if (data) {
      router.push(`/admin/roles/${data.id}`);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Link href="/admin/roles" className="text-blue-600 hover:underline">
          &larr; Back to Roles / Voltar para Papeis
        </Link>
      </div>

      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Create Role / Criar Papel
      </h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="max-w-lg rounded border p-6">
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Name / Nome (slug)
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="e.g. team_manager"
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Display Name / Nome de Exibicao
          </label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
            placeholder="e.g. Team Manager"
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Description / Descricao
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Creating... / Criando..." : "Create / Criar"}
        </button>
      </form>
    </div>
  );
}
