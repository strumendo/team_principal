/**
 * Driver detail page.
 * Pagina de detalhe do piloto.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { DriverDetail } from "@/types/driver";
import { driversApi } from "@/lib/api-client";

export default function DriverDetailPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [driver, setDriver] = useState<DriverDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session || !id) return;

    const fetchDriver = async () => {
      setLoading(true);
      const token = (session as unknown as { accessToken: string }).accessToken;
      const { data, error: err } = await driversApi.get(token, id);
      if (err) {
        setError(err);
      } else {
        setDriver(data || null);
        setError(null);
      }
      setLoading(false);
    };

    fetchDriver();
  }, [session, id]);

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!driver) {
    return <p className="text-gray-500">Driver not found. / Piloto nao encontrado.</p>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{driver.display_name}</h1>
          <p className="text-sm text-gray-500">{driver.name}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex rounded bg-gray-200 px-3 py-1 text-lg font-bold text-gray-800">
            {driver.abbreviation}
          </span>
          <span className="text-2xl font-bold text-gray-700">#{driver.number}</span>
        </div>
      </div>

      {/* Driver photo / Foto do piloto */}
      {driver.photo_url && (
        <div className="mb-6">
          <img
            src={driver.photo_url}
            alt={driver.display_name}
            className="h-48 w-48 rounded-lg object-cover shadow-md"
          />
        </div>
      )}

      {/* Driver details / Detalhes do piloto */}
      <div className="mb-8 rounded-lg border bg-white p-6">
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Number / Numero</dt>
            <dd className="text-lg text-gray-900">{driver.number}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Abbreviation / Abreviacao</dt>
            <dd className="text-lg text-gray-900">{driver.abbreviation}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Nationality / Nacionalidade</dt>
            <dd className="text-gray-900">{driver.nationality || "—"}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Date of Birth / Data de Nascimento</dt>
            <dd className="text-gray-900">{driver.date_of_birth || "—"}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Active / Ativo</dt>
            <dd>
              <span
                className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                  driver.is_active
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {driver.is_active ? "Yes / Sim" : "No / Nao"}
              </span>
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Team / Equipe</dt>
            <dd>
              {driver.team ? (
                <span className="font-medium text-gray-900">
                  {driver.team.display_name}
                </span>
              ) : (
                <span className="text-gray-500">—</span>
              )}
            </dd>
          </div>
        </dl>
      </div>

      <div className="mt-6">
        <Link href="/drivers" className="text-blue-600 hover:underline">
          &larr; Back to Drivers / Voltar para Pilotos
        </Link>
      </div>
    </div>
  );
}
