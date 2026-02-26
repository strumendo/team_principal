# Calendar API / API do Calendario

## Overview / Visao Geral

The Calendar API provides a global view of races across all championships for a given month. It aggregates race data from the existing Races and Championships modules into a single endpoint optimized for calendar views.

A API do Calendario fornece uma visualizacao global de corridas em todos os campeonatos para um dado mes. Ela agrega dados de corridas dos modulos existentes de Corridas e Campeonatos em um unico endpoint otimizado para visualizacoes de calendario.

---

## Endpoints

### List Calendar Races / Listar Corridas do Calendario

```
GET /api/v1/calendar/races
```

Returns races across all (or filtered) championships for a given year/month, ordered by `scheduled_at`. Only races with a non-null `scheduled_at` are included.

Retorna corridas de todos (ou filtrados) campeonatos para um dado ano/mes, ordenadas por `scheduled_at`. Apenas corridas com `scheduled_at` nao nulo sao incluidas.

**Authentication / Autenticacao:** Bearer token with `races:read` permission.

**Query Parameters / Parametros de Consulta:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `year` | `int` | No | Current year | Year to query / Ano a consultar |
| `month` | `int` | No | Current month | Month to query (1-12) / Mes a consultar (1-12) |
| `championship_id` | `UUID` | No | — | Filter by championship / Filtrar por campeonato |

**Response (200):** `CalendarRaceResponse[]`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "display_name": "Round 1 - Interlagos",
    "round_number": 1,
    "status": "scheduled",
    "scheduled_at": "2026-03-15T14:00:00Z",
    "track_name": "Interlagos",
    "track_country": "Brazil",
    "championship_id": "660e8400-e29b-41d4-a716-446655440001",
    "championship_display_name": "GT Series 2026",
    "championship_status": "active"
  }
]
```

**Response Schema / Schema de Resposta:**

| Field | Type | Description |
|---|---|---|
| `id` | `UUID` | Race ID / ID da corrida |
| `display_name` | `string` | Race display name / Nome de exibicao da corrida |
| `round_number` | `int` | Round number / Numero da rodada |
| `status` | `RaceStatus` | Race status (scheduled, qualifying, active, finished, cancelled) |
| `scheduled_at` | `datetime` | Scheduled date and time / Data e hora agendada |
| `track_name` | `string?` | Track name / Nome da pista |
| `track_country` | `string?` | Track country / Pais da pista |
| `championship_id` | `UUID` | Championship ID / ID do campeonato |
| `championship_display_name` | `string` | Championship display name / Nome do campeonato |
| `championship_status` | `string` | Championship status / Status do campeonato |

**Error Responses / Respostas de Erro:**

| Status | Description |
|---|---|
| `401` | Missing or invalid authentication token / Token ausente ou invalido |
| `403` | Missing `races:read` permission / Sem permissao `races:read` |

---

## Frontend Integration / Integracao com Frontend

The calendar page is accessible at `/calendar` in the dashboard sidebar. It provides:

A pagina do calendario e acessivel em `/calendar` na barra lateral do dashboard. Ela fornece:

- **Monthly grid view** (desktop) — 7-column calendar grid with race events as colored pills
- **Agenda view** (mobile) — list of race days with details
- **Month navigation** — prev/next buttons and "Today" shortcut
- **Championship filter** — dropdown to filter by specific championship
- **Status color coding** — races color-coded by status (scheduled: gray, qualifying: yellow, active: green, finished: blue, cancelled: red)
- **Click to navigate** — clicking a race pill navigates to `/races/{id}`

---

## Architecture Notes / Notas de Arquitetura

- The calendar module (`app/calendar/`) is read-only — it does not create any new database models
- It reuses existing `Race` and `Championship` models via joined queries
- Permission reuse: the endpoint uses `races:read` (no new permissions needed)
- Date filtering uses UTC-based range: `[month_start, next_month_start)`

---

## Test Coverage / Cobertura de Testes

| Test | Description |
|---|---|
| `test_calendar_races_for_month` | Returns races for the given month |
| `test_calendar_races_ordered_by_date` | Races ordered by scheduled_at ascending |
| `test_calendar_races_filter_by_championship` | Championship filter works correctly |
| `test_calendar_races_empty_month` | Empty result for month with no races |
| `test_calendar_races_excludes_other_months` | Only current month's races returned |
| `test_calendar_races_excludes_no_date` | Races without scheduled_at excluded |
| `test_calendar_races_response_fields` | All expected fields present in response |
| `test_calendar_races_championship_status` | Championship status included |
| `test_calendar_races_unauthorized` | 401 without auth |
| `test_calendar_races_forbidden` | 403 without permission |
| `test_calendar_races_december_boundary` | December year boundary handled |
| `test_calendar_races_default_params` | Works without explicit year/month |
