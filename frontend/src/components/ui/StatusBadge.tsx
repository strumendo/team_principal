/**
 * Reusable badge component for status, compounds, and boolean values.
 * Componente de badge reutilizavel para status, compostos e valores booleanos.
 */

import { ACTIVE_COLORS, COMPOUND_COLORS } from "@/lib/theme";

interface StatusBadgeProps {
  label: string;
  colorClass: string;
}

export default function StatusBadge({ label, colorClass }: StatusBadgeProps) {
  return (
    <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${colorClass}`}>
      {label}
    </span>
  );
}

/**
 * Badge for active/inactive boolean values.
 * Badge para valores booleanos ativo/inativo.
 */
export function ActiveBadge({ isActive }: { isActive: boolean }) {
  return (
    <StatusBadge
      label={isActive ? "Yes / Sim" : "No / Nao"}
      colorClass={isActive ? ACTIVE_COLORS.active : ACTIVE_COLORS.inactive}
    />
  );
}

/**
 * Badge for tire compound with color mapping.
 * Badge para composto de pneu com mapeamento de cores.
 */
export function CompoundBadge({ compound }: { compound: string | null }) {
  if (!compound) return <span className="text-gray-400">-</span>;

  const colorClass = COMPOUND_COLORS[compound] || "bg-gray-100 text-gray-800";

  return (
    <StatusBadge
      label={compound.charAt(0).toUpperCase() + compound.slice(1)}
      colorClass={colorClass}
    />
  );
}
