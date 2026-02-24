# Race Results & Standings API Reference / Referencia da API de Resultados e Classificacao

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [Business Rules / Regras de Negocio](#business-rules--regras-de-negocio)
4. [Permissions / Permissoes](#permissions--permissoes)
5. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
6. [API Endpoints — Race Results CRUD](#api-endpoints--race-results-crud)
7. [API Endpoints — Championship Standings](#api-endpoints--championship-standings)
8. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
9. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
10. [Database Migrations / Migracoes de Banco](#database-migrations--migracoes-de-banco)
11. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Results module records race finishing outcomes per team and computes championship standings by aggregating race results. Results belong to a race (N:1) and reference a team (N:1). Championship standings are computed on-the-fly — no separate standings table.

O modulo de Resultados registra os resultados de chegada por equipe e calcula a classificacao do campeonato agregando resultados de corrida. Resultados pertencem a uma corrida (N:1) e referenciam uma equipe (N:1). A classificacao do campeonato e calculada dinamicamente — sem tabela separada.

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/results/models.py` | ORM model: `RaceResult` |
| `app/results/schemas.py` | 8 Pydantic schemas (request/response) |
| `app/results/service.py` | Business logic: CRUD + standings computation |
| `app/results/router.py` | API endpoint definitions (6 endpoints) |
| `alembic/versions/008_create_race_results_table.py` | Migration: `race_results` table |

---

## Data Model / Modelo de Dados

### Entity Relationship Diagram / Diagrama de Entidade-Relacionamento

```
┌──────────────────────────────┐
│          races                │
├──────────────────────────────┤
│ id              UUID PK       │
│ championship_id UUID FK       │
│ ...                           │
└──────────┬───────────────────┘
           │
           │ races.id (FK)
           │
┌──────────┴───────────────────┐        ┌──────────────────────────────┐
│       race_results            │        │          teams                │
├──────────────────────────────┤        ├──────────────────────────────┤
│ id              UUID PK       │        │ id              UUID PK       │
│ race_id         UUID FK       │───────>│ ...                           │
│ team_id         UUID FK       │        └──────────────────────────────┘
│ position        INTEGER       │
│ points          FLOAT         │ default: 0.0
│ laps_completed  INTEGER       │ nullable
│ fastest_lap     BOOLEAN       │ default: false
│ dnf             BOOLEAN       │ default: false
│ dsq             BOOLEAN       │ default: false
│ notes           VARCHAR(512)  │ nullable
│ created_at      TIMESTAMPTZ   │
│ updated_at      TIMESTAMPTZ   │
├──────────────────────────────┤
│ UQ(race_id, team_id)         │ uq_race_result_team
│ IDX(race_id), IDX(team_id)  │
└──────────────────────────────┘
```

### Field Details / Detalhes dos Campos

| Field | Type | Constraints | Description (EN) | Descricao (pt-BR) |
|---|---|---|---|---|
| `id` | UUID | PK, default uuid4 | Primary key | Chave primaria |
| `race_id` | UUID | FK races.id, CASCADE, NOT NULL, INDEXED | Parent race | Corrida pai |
| `team_id` | UUID | FK teams.id, CASCADE, NOT NULL, INDEXED | Team that finished | Equipe que terminou |
| `position` | Integer | NOT NULL | Finishing position (1, 2, 3...) | Posicao de chegada |
| `points` | Float | NOT NULL, default 0.0 | Points scored | Pontos marcados |
| `laps_completed` | Integer | nullable | Laps completed | Voltas completadas |
| `fastest_lap` | Boolean | default false | Fastest lap award | Premio de volta mais rapida |
| `dnf` | Boolean | default false | Did Not Finish | Nao terminou |
| `dsq` | Boolean | default false | Disqualified | Desclassificado |
| `notes` | String(512) | nullable | Steward notes | Notas dos comissarios |
| `created_at` | DateTime(tz) | server_default=now() | Creation timestamp | Data de criacao |
| `updated_at` | DateTime(tz) | server_default=now(), onupdate=now() | Last update | Ultima atualizacao |

---

## Business Rules / Regras de Negocio

1. **Race must be finished** — Results can only be created for races with `status == "finished"`. Returns 409 otherwise.

   **Corrida deve estar finalizada** — Resultados so podem ser criados para corridas com `status == "finished"`. Retorna 409 caso contrario.

2. **Team must be enrolled in race** — Team must have an entry in `race_entries` for that race. Returns 409 otherwise.

   **Equipe deve estar inscrita na corrida** — Equipe deve ter inscricao em `race_entries` para aquela corrida. Retorna 409 caso contrario.

3. **One result per team per race** — DB unique constraint `uq_race_result_team` + service check. Returns 409 on duplicate.

   **Um resultado por equipe por corrida** — Constraint unica no DB + verificacao no service. Retorna 409 em duplicata.

4. **Position unique among non-DSQ** — Validated in service layer (not DB) because DSQ entries may share positions. Returns 409 on conflict.

   **Posicao unica entre nao-DSQ** — Validado na camada de servico (nao no DB) porque entradas DSQ podem compartilhar posicoes. Retorna 409 em conflito.

5. **Immutable fields** — `race_id` and `team_id` are NOT in `UpdateRequest` and cannot be changed after creation.

   **Campos imutaveis** — `race_id` e `team_id` NAO estao no `UpdateRequest` e nao podem ser alterados apos criacao.

6. **Standings exclude DSQ** — Championship standings aggregate only non-DSQ results. DSQ results are excluded from points and wins.

   **Classificacao exclui DSQ** — A classificacao do campeonato agrega apenas resultados nao-DSQ.

---

## Permissions / Permissoes

| Permission | Description (EN) | Descricao (pt-BR) |
|---|---|---|
| `results:read` | Read race results and standings | Ler resultados e classificacao |
| `results:create` | Create race results | Criar resultados |
| `results:update` | Update race results | Atualizar resultados |
| `results:delete` | Delete race results | Excluir resultados |

**Role assignments / Atribuicoes de papel:**
- `admin`: all 4 permissions
- `pilot`: `results:read` only

---

## Pydantic Schemas / Schemas Pydantic

### Response Schemas / Schemas de Resposta

| Schema | Purpose (EN) | Proposito (pt-BR) |
|---|---|---|
| `RaceResultResponse` | Standard result response | Resposta padrao de resultado |
| `RaceResultListResponse` | List item (same as Response) | Item de lista |
| `RaceResultDetailResponse` | Detail with nested team | Detalhe com equipe aninhada |
| `RaceResultTeamResponse` | Team summary in detail view | Resumo da equipe no detalhe |
| `ChampionshipStandingResponse` | Standing entry with team, points, wins | Entrada de classificacao |

### Request Schemas / Schemas de Requisicao

| Schema | Purpose (EN) | Proposito (pt-BR) |
|---|---|---|
| `RaceResultCreateRequest` | Create result payload | Payload de criacao |
| `RaceResultUpdateRequest` | Partial update payload | Payload de atualizacao parcial |

---

## API Endpoints — Race Results CRUD

### List Race Results / Listar Resultados da Corrida

```
GET /api/v1/races/{race_id}/results
```

**Permission:** `results:read`
**Response:** `200 OK` — `list[RaceResultListResponse]`

Returns all results for a race, ordered by position ascending.

### Create Race Result / Criar Resultado de Corrida

```
POST /api/v1/races/{race_id}/results
```

**Permission:** `results:create`
**Response:** `201 Created` — `RaceResultResponse`

**Request body:**
```json
{
    "team_id": "uuid",
    "position": 1,
    "points": 25.0,
    "laps_completed": 30,
    "fastest_lap": true,
    "dnf": false,
    "dsq": false,
    "notes": "string"
}
```

Required fields: `team_id`, `position`. All others have defaults.

### Get Race Result / Buscar Resultado de Corrida

```
GET /api/v1/results/{result_id}
```

**Permission:** `results:read`
**Response:** `200 OK` — `RaceResultDetailResponse` (includes nested `team` object)

### Update Race Result / Atualizar Resultado de Corrida

```
PATCH /api/v1/results/{result_id}
```

**Permission:** `results:update`
**Response:** `200 OK` — `RaceResultResponse`

**Request body (all optional):**
```json
{
    "position": 2,
    "points": 18.0,
    "laps_completed": 28,
    "fastest_lap": false,
    "dnf": true,
    "dsq": false,
    "notes": "updated notes"
}
```

### Delete Race Result / Excluir Resultado de Corrida

```
DELETE /api/v1/results/{result_id}
```

**Permission:** `results:delete`
**Response:** `204 No Content`

---

## API Endpoints — Championship Standings

### Get Championship Standings / Obter Classificacao do Campeonato

```
GET /api/v1/championships/{championship_id}/standings
```

**Permission:** `results:read`
**Response:** `200 OK` — `list[ChampionshipStandingResponse]`

Computes standings dynamically by aggregating non-DSQ race results:
- `total_points`: SUM of points from all non-DSQ results in the championship's races
- `races_scored`: COUNT of non-DSQ race results
- `wins`: COUNT of position=1 non-DSQ results
- Ordered by `total_points` descending
- `position` is 1-indexed based on order

**Response example:**
```json
[
    {
        "position": 1,
        "team_id": "uuid",
        "team_name": "team_alpha",
        "team_display_name": "Team Alpha",
        "total_points": 50.0,
        "races_scored": 2,
        "wins": 2
    }
]
```

### Get Driver Championship Standings / Obter Classificacao de Pilotos do Campeonato

```
GET /api/v1/championships/{championship_id}/driver-standings
```

**Permission:** `results:read`
**Response:** `200 OK` — `list[DriverStandingResponse]`

Computes driver standings dynamically by aggregating non-DSQ race results that have a `driver_id`:
- `total_points`: SUM of points from all non-DSQ results for the driver
- `races_scored`: COUNT of non-DSQ race results
- `wins`: COUNT of position=1 non-DSQ results
- Results without a driver are excluded
- Ordered by `total_points` descending
- `position` is 1-indexed based on order

**Response example:**
```json
[
    {
        "position": 1,
        "driver_id": "uuid",
        "driver_name": "driver_alpha",
        "driver_display_name": "Driver Alpha",
        "team_id": "uuid",
        "team_name": "team_alpha",
        "team_display_name": "Team Alpha",
        "total_points": 50.0,
        "races_scored": 2,
        "wins": 2
    }
]
```

---

## Error Responses / Respostas de Erro

| Status | Condition (EN) | Condicao (pt-BR) |
|---|---|---|
| 401 | Missing or invalid auth token | Token ausente ou invalido |
| 403 | Insufficient permissions | Permissoes insuficientes |
| 404 | Race, team, or result not found | Corrida, equipe ou resultado nao encontrado |
| 409 | Race not finished | Corrida nao finalizada |
| 409 | Team not enrolled in race | Equipe nao inscrita na corrida |
| 409 | Duplicate result for team in race | Resultado duplicado para equipe |
| 409 | Position taken by non-DSQ result | Posicao ocupada por resultado nao-DSQ |

---

## Service Layer / Camada de Servico

### Functions / Funcoes

| Function | Purpose (EN) | Proposito (pt-BR) |
|---|---|---|
| `list_race_results(db, race_id)` | List results ordered by position | Lista resultados por posicao |
| `get_result_by_id(db, result_id)` | Get single result | Busca resultado unico |
| `create_result(db, race_id, ...)` | Create with full validation | Cria com validacao completa |
| `update_result(db, result, ...)` | Partial update with position check | Atualizacao parcial com verificacao |
| `delete_result(db, result)` | Delete result | Exclui resultado |
| `get_championship_standings(db, champ_id)` | Aggregate standings computation | Calculo agregado de classificacao |
| `get_driver_championship_standings(db, champ_id)` | Driver standings computation | Calculo de classificacao de pilotos |

---

## Database Migrations / Migracoes de Banco

### Migration 008 — `race_results` table

```
Revision: 008
Down revision: 007
```

Creates the `race_results` table with all columns, indexes on `race_id` and `team_id`, and unique constraint `uq_race_result_team`.

Cria a tabela `race_results` com todas as colunas, indices em `race_id` e `team_id`, e constraint unica `uq_race_result_team`.

---

## Test Coverage / Cobertura de Testes

### Race Results Tests / Testes de Resultados (`test_race_results.py` — 28 tests)

| Test | Category |
|---|---|
| `test_list_race_results_empty` | List |
| `test_list_race_results_with_data` | List |
| `test_list_race_results_ordered_by_position` | List |
| `test_list_race_results_race_not_found` | List |
| `test_create_result_success` | Create |
| `test_create_result_minimal_fields` | Create |
| `test_create_result_race_not_finished` | Create (409) |
| `test_create_result_team_not_enrolled` | Create (409) |
| `test_create_result_duplicate_team` | Create (409) |
| `test_create_result_duplicate_position_non_dsq` | Create (409) |
| `test_create_result_dsq_allows_duplicate_position` | Create |
| `test_create_result_race_not_found` | Create (404) |
| `test_create_result_team_not_found` | Create (404) |
| `test_create_result_with_driver` | Create + Driver |
| `test_create_result_driver_wrong_team` | Create + Driver (409) |
| `test_create_result_driver_not_found` | Create + Driver (404) |
| `test_get_result_by_id` | Get |
| `test_get_result_not_found` | Get |
| `test_get_result_detail_includes_driver` | Get + Driver |
| `test_get_result_detail_driver_null` | Get + Driver |
| `test_update_result_points` | Update |
| `test_update_result_position_conflict` | Update (409) |
| `test_update_result_dsq_bypasses_position_check` | Update |
| `test_update_result_not_found` | Update |
| `test_delete_result` | Delete |
| `test_delete_result_not_found` | Delete |
| `test_create_result_unauthorized` | Auth (401) |
| `test_create_result_forbidden` | Auth (403) |

### Championship Standings Tests / Testes de Classificacao (`test_championship_standings.py` — 9 tests)

| Test | Category |
|---|---|
| `test_get_standings_empty_no_results` | Empty |
| `test_get_standings_with_data_ordered_by_points` | Ordering |
| `test_get_standings_excludes_dsq_results` | DSQ exclusion |
| `test_get_standings_counts_wins_correctly` | Wins count |
| `test_get_standings_multiple_races_accumulate_points` | Accumulation |
| `test_get_standings_position_assigned_1_indexed` | Position |
| `test_get_standings_championship_not_found` | Error (404) |
| `test_get_standings_unauthorized` | Auth (401) |
| `test_get_standings_forbidden` | Auth (403) |

### Driver Standings Tests / Testes de Classificacao de Pilotos (`test_driver_standings.py` — 8 tests)

| Test | Category |
|---|---|
| `test_get_driver_standings_empty` | Empty |
| `test_get_driver_standings_ordered_by_points` | Ordering |
| `test_get_driver_standings_excludes_dsq` | DSQ exclusion |
| `test_get_driver_standings_counts_wins` | Wins count |
| `test_get_driver_standings_ignores_results_without_driver` | No driver filter |
| `test_get_driver_standings_championship_not_found` | Error (404) |
| `test_get_driver_standings_unauthorized` | Auth (401) |
| `test_get_driver_standings_forbidden` | Auth (403) |

**Total: 45 tests across 3 test files (28 + 9 + 8). 284 total across the project.**
