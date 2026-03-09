# Frontend Refactoring / Refatoracao do Frontend

## Overview / Visao Geral

This document describes the frontend refactoring pass, focused on eliminating code duplication, extracting shared components, and improving UI consistency across the application.

Este documento descreve a refatoracao do frontend, focada em eliminar duplicacao de codigo, extrair componentes compartilhados e melhorar a consistencia visual do aplicativo.

---

## Shared Theme Constants / Constantes de Tema Compartilhadas

### `src/lib/theme.ts`

Centralized all duplicated color/label constants into a single source of truth:

Centralizou todas as constantes de cores/rotulos duplicadas em uma unica fonte de verdade:

| Constant | Description | Previously duplicated in |
|----------|-------------|--------------------------|
| `CHAMPIONSHIP_STATUS_COLORS` | Championship status badge colors | 4 files |
| `CHAMPIONSHIP_STATUS_LABELS` | Championship status display labels | 3 files |
| `RACE_STATUS_COLORS` | Race status badge colors | 3 files |
| `RACE_STATUS_LABELS` | Race status display labels | 2 files |
| `COMPOUND_COLORS` | Tire compound badge colors | 3 files |
| `ACTIVE_COLORS` | Active/inactive badge colors | 8+ files (inline) |

---

## Shared UI Components / Componentes UI Compartilhados

### `src/components/ui/LoadingState.tsx`

Replaces the `<p className="text-gray-500">Loading... / Carregando...</p>` pattern that appeared in 20+ pages with a consistent loading spinner + message.

Substitui o padrao de texto de carregamento que aparecia em 20+ paginas por um spinner de carregamento consistente.

**Before / Antes:**
```tsx
if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;
```

**After / Depois:**
```tsx
if (loading) return <LoadingState />;
```

### `src/components/ui/ErrorState.tsx`

Replaces inline error text with a styled error card with optional retry button.

Substitui texto de erro inline por um card de erro estilizado com botao de retry opcional.

**Before / Antes:**
```tsx
if (error) return <p className="text-red-600">{error}</p>;
```

**After / Depois:**
```tsx
if (error) return <ErrorState message={error} onRetry={fetchData} />;
```

### `src/components/ui/StatusBadge.tsx`

Provides three reusable badge components:

Fornece tres componentes de badge reutilizaveis:

- **`StatusBadge`** — Generic badge with label + color class
- **`ActiveBadge`** — Boolean active/inactive badge (`isActive` prop)
- **`CompoundBadge`** — Tire compound badge with automatic color mapping

**Before / Antes:**
```tsx
<span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
  entry.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
}`}>
  {entry.is_active ? "Yes / Sim" : "No / Nao"}
</span>
```

**After / Depois:**
```tsx
<ActiveBadge isActive={entry.is_active} />
```

---

## Files Changed / Arquivos Alterados

### New Files / Arquivos Novos
| File | Description |
|------|-------------|
| `src/lib/theme.ts` | Centralized color constants and labels |
| `src/components/ui/LoadingState.tsx` | Loading spinner component |
| `src/components/ui/ErrorState.tsx` | Error display component with retry |
| `src/components/ui/StatusBadge.tsx` | Badge components (Status, Active, Compound) |

### Updated Files / Arquivos Atualizados (22 files)

**Pages using LoadingState + ErrorState:**
- All 20+ dashboard pages now use shared loading/error components

**Pages using theme constants:**
- `championships/page.tsx` — Uses `CHAMPIONSHIP_STATUS_COLORS`, `CHAMPIONSHIP_STATUS_LABELS`, `ActiveBadge`
- `championships/[id]/page.tsx` — Uses `CHAMPIONSHIP_STATUS_COLORS`, `ActiveBadge`
- `championships/[id]/races/page.tsx` — Uses `RACE_STATUS_COLORS`, `RACE_STATUS_LABELS`, `ActiveBadge`
- `standings/page.tsx` — Uses `CHAMPIONSHIP_STATUS_COLORS`, `CHAMPIONSHIP_STATUS_LABELS`
- `races/[id]/page.tsx` — Uses `RACE_STATUS_COLORS`, `ActiveBadge`
- `drivers/page.tsx`, `drivers/[id]/page.tsx` — Uses `ActiveBadge`
- `admin/users/page.tsx` — Uses `ActiveBadge`

**Components using shared COMPOUND_COLORS:**
- `components/pitstops/PitStopTable.tsx` — Uses `CompoundBadge` from StatusBadge
- `components/pitstops/StrategyCard.tsx` — Uses `COMPOUND_COLORS` from theme
- `components/replay/StintTable.tsx` — Uses `COMPOUND_COLORS` from theme

---

## Impact / Impacto

- **~200 lines of duplicated color constants removed** across 9 files
- **~100 lines of inline badge code replaced** with shared components
- **20+ pages** now use consistent loading/error UI with spinner animation
- **Single source of truth** for all status colors, labels, and badge styling
- **All 64 frontend tests pass**, lint clean, type check clean
