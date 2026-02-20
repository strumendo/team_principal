# Dashboard API / API do Dashboard

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Permissions / Permissoes](#permissions--permissoes)
3. [Endpoint](#endpoint)
4. [Response Schema / Schema de Resposta](#response-schema--schema-de-resposta)
5. [Response Fields / Campos da Resposta](#response-fields--campos-da-resposta)
6. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
7. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
8. [Tests / Testes](#tests--testes)

---

## Overview / Visao Geral

The dashboard endpoint aggregates data from multiple modules into a single API call, providing an overview of the platform's current state. This avoids N+1 requests from the frontend.

O endpoint do dashboard agrega dados de multiplos modulos em uma unica chamada API, fornecendo uma visao geral do estado atual da plataforma. Isso evita N+1 requisicoes do frontend.

The response includes three sections:
- **Active Championships** — all championships with `status=active`, enriched with race counts and team enrollment counts
- **Next Races** — up to 5 upcoming scheduled races across all active championships, ordered by date
- **Championship Standings** — top 5 standings per active championship, reusing the existing standings computation

A resposta inclui tres secoes:
- **Campeonatos Ativos** — todos os campeonatos com `status=active`, enriquecidos com contagens de corridas e equipes inscritas
- **Proximas Corridas** — ate 5 corridas agendadas de todos os campeonatos ativos, ordenadas por data
- **Classificacoes** — top 5 classificacao por campeonato ativo, reutilizando a computacao de classificacao existente

---

## Permissions / Permissoes

| Permission | Required |
|---|---|
| `championships:read` | Yes (AND) |
| `results:read` | Yes (AND) |

Both the `admin` and `pilot` roles already include these permissions. Superusers bypass all permission checks.

Ambos os papeis `admin` e `pilot` ja incluem essas permissoes. Superusuarios ignoram todas as verificacoes de permissao.

---

## Endpoint

```
GET /api/v1/dashboard/summary
```

**Authentication:** Bearer token (JWT)

**Response:** `200 OK` with `DashboardSummaryResponse`

---

## Response Schema / Schema de Resposta

### DashboardSummaryResponse

```json
{
  "active_championships": [DashboardChampionshipResponse],
  "next_races": [DashboardNextRaceResponse],
  "championship_standings": [DashboardChampionshipStandingsResponse]
}
```

### DashboardChampionshipResponse

```json
{
  "id": "uuid",
  "name": "formula_e_2026",
  "display_name": "Formula E 2026",
  "season_year": 2026,
  "status": "active",
  "start_date": "2026-02-01",
  "end_date": "2026-11-30",
  "total_races": 10,
  "completed_races": 3,
  "team_count": 8
}
```

### DashboardNextRaceResponse

```json
{
  "id": "uuid",
  "name": "round_04",
  "display_name": "Round 4 - Monaco",
  "championship_id": "uuid",
  "championship_display_name": "Formula E 2026",
  "round_number": 4,
  "scheduled_at": "2026-03-15T14:00:00Z",
  "track_name": "Monaco Circuit",
  "track_country": "Monaco"
}
```

### DashboardChampionshipStandingsResponse

```json
{
  "championship_id": "uuid",
  "championship_display_name": "Formula E 2026",
  "standings": [DashboardStandingEntryResponse]
}
```

### DashboardStandingEntryResponse

```json
{
  "position": 1,
  "team_id": "uuid",
  "team_name": "team_alpha",
  "team_display_name": "Team Alpha",
  "total_points": 50.0,
  "races_scored": 2,
  "wins": 2
}
```

---

## Response Fields / Campos da Resposta

### active_championships

| Field | Type | Description (EN) | Descricao (pt-BR) |
|---|---|---|---|
| `id` | UUID | Championship ID | ID do campeonato |
| `name` | string | Unique slug | Slug unico |
| `display_name` | string | Human-readable name | Nome legivel |
| `season_year` | int | Season year | Ano da temporada |
| `status` | string | Always `"active"` | Sempre `"active"` |
| `start_date` | date \| null | Championship start | Inicio do campeonato |
| `end_date` | date \| null | Championship end | Fim do campeonato |
| `total_races` | int | All races in championship | Total de corridas |
| `completed_races` | int | Races with `status=finished` | Corridas com `status=finished` |
| `team_count` | int | Enrolled teams | Equipes inscritas |

### next_races

| Field | Type | Description (EN) | Descricao (pt-BR) |
|---|---|---|---|
| `id` | UUID | Race ID | ID da corrida |
| `name` | string | Unique slug within championship | Slug unico no campeonato |
| `display_name` | string | Human-readable name | Nome legivel |
| `championship_id` | UUID | Parent championship | Campeonato pai |
| `championship_display_name` | string | Championship name | Nome do campeonato |
| `round_number` | int | Round number | Numero da rodada |
| `scheduled_at` | datetime | Scheduled date/time (UTC) | Data/hora agendada (UTC) |
| `track_name` | string \| null | Track name | Nome da pista |
| `track_country` | string \| null | Track country | Pais da pista |

### championship_standings

| Field | Type | Description (EN) | Descricao (pt-BR) |
|---|---|---|---|
| `championship_id` | UUID | Championship ID | ID do campeonato |
| `championship_display_name` | string | Championship name | Nome do campeonato |
| `standings` | array | Top 5 entries | Top 5 entradas |

### standings entries

| Field | Type | Description (EN) | Descricao (pt-BR) |
|---|---|---|---|
| `position` | int | Standing position (1-indexed) | Posicao (comeca em 1) |
| `team_id` | UUID | Team ID | ID da equipe |
| `team_name` | string | Team slug | Slug da equipe |
| `team_display_name` | string | Team display name | Nome da equipe |
| `total_points` | float | Sum of points (excl. DSQ) | Soma de pontos (excl. DSQ) |
| `races_scored` | int | Number of races scored | Numero de corridas pontuadas |
| `wins` | int | Number of 1st place finishes | Numero de 1o lugar |

---

## Service Layer / Camada de Servico

The `get_dashboard_summary()` function in `app/dashboard/service.py` executes three query groups:

A funcao `get_dashboard_summary()` em `app/dashboard/service.py` executa tres grupos de queries:

1. **Active championships query** — Selects all championships with `status=active` with correlated subqueries for `total_races`, `completed_races` (status=finished), and `team_count` (from `championship_entries` table)

2. **Next races query** — JOINs `races` with `championships`, filters by `status=scheduled` + `scheduled_at IS NOT NULL` + championship in active list, orders by `scheduled_at ASC`, limited to 5

3. **Standings loop** — For each active championship, calls the existing `get_championship_standings()` from `app/results/service.py` and slices to the top 5 entries. Championships with no results are omitted from the response.

---

## Error Responses / Respostas de Erro

| Code | Condition (EN) | Condicao (pt-BR) |
|---|---|---|
| `401` | Missing or invalid token | Token ausente ou invalido |
| `403` | Missing `championships:read` or `results:read` | Faltando `championships:read` ou `results:read` |

---

## Tests / Testes

13 tests in `backend/tests/test_dashboard.py`:

| Test | Description (EN) | Descricao (pt-BR) |
|---|---|---|
| `test_dashboard_summary_empty` | Empty state returns empty lists | Estado vazio retorna listas vazias |
| `test_dashboard_summary_active_championships` | Active championships returned | Campeonatos ativos retornados |
| `test_dashboard_summary_excludes_non_active` | Only active status included | Apenas status ativo incluido |
| `test_dashboard_summary_race_counts` | Total + completed race counts | Contagem de corridas total + completadas |
| `test_dashboard_summary_team_count` | Enrolled team count | Contagem de equipes inscritas |
| `test_dashboard_summary_next_races_ordered` | Sorted by scheduled_at ASC | Ordenado por scheduled_at ASC |
| `test_dashboard_summary_next_races_limit` | Respects limit of 5 | Respeita limite de 5 |
| `test_dashboard_summary_next_races_excludes_non_scheduled` | Only scheduled status | Apenas status scheduled |
| `test_dashboard_summary_next_races_excludes_null_scheduled_at` | Null date excluded | Data nula excluida |
| `test_dashboard_summary_standings_top_5` | Top 5 only | Apenas top 5 |
| `test_dashboard_summary_standings_empty` | Empty standings omitted | Classificacao vazia omitida |
| `test_dashboard_summary_unauthorized` | 401 without auth | 401 sem autenticacao |
| `test_dashboard_summary_forbidden` | 403 without permissions | 403 sem permissoes |
