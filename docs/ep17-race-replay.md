# EP17 — Race Replay / Analise de Corrida

## Overview / Visao Geral

EP17 adds race replay and analysis capabilities to the platform, providing a unified view to replay and analyze races lap-by-lap. It introduces two new models — **LapPosition** (driver position per lap) and **RaceEvent** (race events timeline) — plus read-only analysis endpoints that aggregate existing data from telemetry, pit stops, and results into actionable insights.

EP17 adiciona capacidades de replay e analise de corrida a plataforma, fornecendo uma visao unificada para reproduzir e analisar corridas volta a volta. Introduz dois novos modelos — **LapPosition** (posicao do piloto por volta) e **RaceEvent** (linha do tempo de eventos) — alem de endpoints de analise somente leitura que agregam dados existentes de telemetria, pit stops e resultados em insights acionaveis.

---

## New Models / Novos Modelos

### LapPosition
Position of each driver on each lap (core replay data).
Posicao de cada piloto em cada volta (dados centrais de replay).

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | default uuid4 |
| race_id | UUID FK(races.id) | CASCADE, indexed |
| driver_id | UUID FK(drivers.id) | CASCADE, indexed |
| team_id | UUID FK(teams.id) | CASCADE |
| lap_number | Integer | not null |
| position | Integer | not null (1-based) |
| gap_to_leader_ms | Integer | nullable |
| interval_ms | Integer | nullable |
| created_at | DateTime(tz) | server_default=now() |

UniqueConstraint: `(race_id, driver_id, lap_number)`

### RaceEvent
Events during the race (safety car, incidents, flags, etc.).
Eventos durante a corrida (safety car, incidentes, bandeiras, etc.).

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | default uuid4 |
| race_id | UUID FK(races.id) | CASCADE, indexed |
| lap_number | Integer | not null |
| event_type | Enum(RaceEventType) | native_enum=False, length=30 |
| description | Text | nullable |
| driver_id | UUID FK(drivers.id) | nullable |
| created_at | DateTime(tz) | server_default=now() |

### RaceEventType Enum
`safety_car`, `virtual_safety_car`, `red_flag`, `incident`, `penalty`, `overtake`, `mechanical_failure`, `race_start`, `race_end`

---

## Endpoints (15 total)

### LapPosition CRUD (6 endpoints)
| Method | Path | Permission | Status |
|--------|------|------------|--------|
| GET | `/api/v1/races/{race_id}/positions` | replay:read | 200 |
| POST | `/api/v1/races/{race_id}/positions` | replay:create | 201 |
| POST | `/api/v1/races/{race_id}/positions/bulk` | replay:create | 201 |
| GET | `/api/v1/positions/{position_id}` | replay:read | 200 |
| PATCH | `/api/v1/positions/{position_id}` | replay:update | 200 |
| DELETE | `/api/v1/positions/{position_id}` | replay:delete | 204 |

Query filters: `driver_id`, `team_id`, `lap_number`

### RaceEvent CRUD (5 endpoints)
| Method | Path | Permission | Status |
|--------|------|------------|--------|
| GET | `/api/v1/races/{race_id}/events` | replay:read | 200 |
| POST | `/api/v1/races/{race_id}/events` | replay:create | 201 |
| GET | `/api/v1/events/{event_id}` | replay:read | 200 |
| PATCH | `/api/v1/events/{event_id}` | replay:update | 200 |
| DELETE | `/api/v1/events/{event_id}` | replay:delete | 204 |

Query filters: `event_type`, `driver_id`, `lap_number`

### Analysis Endpoints (4 read-only / somente leitura)
| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/v1/races/{race_id}/replay` | replay:read | Full replay: positions + events + pit stops grouped by lap / Replay completo agrupado por volta |
| GET | `/api/v1/races/{race_id}/analysis/stints` | replay:read | Stint analysis: avg pace, best lap, degradation / Analise de stints |
| GET | `/api/v1/races/{race_id}/analysis/overtakes` | replay:read | Detected overtakes from position changes / Ultrapassagens detectadas |
| GET | `/api/v1/races/{race_id}/analysis/summary` | replay:read | Race summary: leader changes, overtakes, SC laps, DNFs / Resumo da corrida |

---

## Permissions / Permissoes
- `replay:read`, `replay:create`, `replay:update`, `replay:delete`
- Pilot role gets `replay:read` / Papel piloto recebe `replay:read`
- Admin gets all / Admin recebe todas

---

## Frontend Components / Componentes Frontend

| Component | Description |
|-----------|-------------|
| `PositionChart` | Line chart: lap (X) vs position (Y inverted, P1 at top) / Grafico de posicao |
| `GapChart` | Line chart: lap (X) vs gap to leader (Y) / Grafico de gap |
| `RaceTimeline` | Horizontal event markers on lap axis / Marcadores de eventos na linha do tempo |
| `StintTable` | Stint breakdown per driver (compound, laps, pace, degradation) / Tabela de stints |
| `RaceSummary` | Stats cards (overtakes, leader changes, SC laps, DNFs, fastest lap) / Cards de estatisticas |
| `LapPositionForm` | Bulk position entry form / Formulario de entrada de posicoes em massa |
| `RaceEventForm` | Race event creation form / Formulario de criacao de evento |

### Replay Page / Pagina de Replay
Located at `/races/[id]/replay` with three tabs:
Localizada em `/races/[id]/replay` com tres abas:

1. **Replay** — PositionChart + GapChart + RaceTimeline + Overtakes table
2. **Analysis / Analise** — StintTable
3. **Summary / Resumo** — RaceSummary

Features / Funcionalidades:
- Driver filter dropdown / Filtro de piloto por dropdown
- Add Positions / Add Event buttons / Botoes para adicionar posicoes e eventos

---

## Tests / Testes
~26 tests in `backend/tests/test_replay.py`:
- LapPosition CRUD (8): create, duplicate (409), invalid race (404), list empty/data/filter, update, delete
- RaceEvent CRUD (6): create, list empty/data/filter, update, delete
- Bulk create (2): success, invalid race
- Analysis (7): replay with data/empty, stints, overtakes detection, summary with data/empty, overtakes empty
- Auth (3): unauthorized create/list (401), not found (404)

---

## Migration / Migracao
Alembic revision `012` — creates `lap_positions` and `race_events` tables.
Revisao Alembic `012` — cria tabelas `lap_positions` e `race_events`.
