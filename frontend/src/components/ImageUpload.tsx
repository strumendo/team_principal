/**
 * Reusable image upload component with preview and error handling.
 * Componente reutilizavel de upload de imagem com preview e tratamento de erros.
 */
"use client";

import { useState, useRef } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/v1$/, "") ||
  "http://localhost:8000";

const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB
const ACCEPTED_TYPES = "image/jpeg,image/png,image/webp";

interface ImageUploadProps {
  currentImageUrl: string | null;
  uploadUrl: string;
  token: string;
  onUploadSuccess: (url: string) => void;
  label: string;
}

export default function ImageUpload({
  currentImageUrl,
  uploadUrl,
  token,
  onUploadSuccess,
  label,
}: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const displayUrl = preview
    ? preview
    : currentImageUrl
      ? `${API_BASE_URL}${currentImageUrl}`
      : null;

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    // Client-side validation / Validacao no cliente
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Invalid file type. Allowed: JPEG, PNG, WebP / Tipo invalido. Permitidos: JPEG, PNG, WebP");
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setError("File too large. Maximum: 5 MB / Arquivo muito grande. Maximo: 5 MB");
      return;
    }

    setPreview(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${apiUrl}${uploadUrl}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        setError(data?.detail || `Upload failed (${response.status})`);
        return;
      }

      const data = await response.json();
      onUploadSuccess(data.url);
      setPreview(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch {
      setError("Network error. Please try again. / Erro de rede. Tente novamente.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mb-6">
      <label className="mb-2 block text-sm font-medium text-gray-700">
        {label}
      </label>

      {/* Preview — uses <img> because src can be a blob URL or dynamic backend URL */}
      {/* Visualizacao — usa <img> pois src pode ser blob URL ou URL dinamica do backend */}
      {displayUrl && (
        <div className="mb-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={displayUrl}
            alt={label}
            className="h-24 w-24 rounded-lg border object-cover"
          />
        </div>
      )}

      {/* File input / Campo de arquivo */}
      <div className="flex items-center gap-3">
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          onChange={handleFileSelect}
          className="block w-full text-sm text-gray-500 file:mr-4 file:rounded file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
        />
        <button
          onClick={handleUpload}
          disabled={uploading || !fileInputRef.current?.files?.length}
          className="whitespace-nowrap rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {uploading ? "Uploading... / Enviando..." : "Upload"}
        </button>
      </div>

      {/* Error / Erro */}
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
