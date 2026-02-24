# Penalties API Reference / Referencia da API de Penalidades

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Penalty Types / Tipos de Penalidade](#penalty-types--tipos-de-penalidade)
3. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
4. [Business Rules / Regras de Negocio](#business-rules--regras-de-negocio)
5. [Permissions / Permissoes](#permissions--permissoes)
6. [Endpoints](#endpoints)
7. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
8. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Penalties module manages race penalties and incidents that impact drivers, teams, and championship standings. Penalties are linked to a specific race and optionally to a race result, team, and driver.

O modulo de Penalidades gerencia penalidades e incidentes de corrida que impactam pilotos, equipes e classificacoes do campeonato. Penalidades sao vinculadas a uma corrida especifica e opcionalmente a um resultado, equipe e piloto.

---

## Penalty Types / Tipos de Penalidade

| Type / Tipo | Description / Descricao | Standings Impact / Impacto na Classificacao |
|---|---|---|
| `warning` | Formal warning with no points impact / Advertencia formal sem impacto em pontos | None / Nenhum |
| `time_penalty` | Time added to race result / Tempo adicionado ao resultado | None / Nenhum |
| `points_deduction` | Championship points subtracted / Pontos subtraidos do campeonato | Subtracts from standings / Subtrai da classificacao |
| `disqualification` | Full disqualification from race / Desclassificacao total da corrida | Auto-syncs result.dsq flag / Sincroniza flag result.dsq |
| `grid_penalty` | Grid position penalty for next race / Penalidade de posicao no grid | None / Nenhum |

---

## Data Model / Modelo de Dados

### Penalty Table / Tabela de Penalidades

| Column / Coluna | Type / Tipo | Description / Descricao |
|---|---|---|
| `id` | UUID (PK) | Primary key / Chave primaria |
| `race_id` | UUID (FK → races.id) | Required. The race this penalty belongs to / Corrida desta penalidade |
| `result_id` | UUID (FK → race_results.id) | Nullable. Linked race result / Resultado vinculado |
| `team_id` | UUID (FK → teams.id) | Required. Penalized team / Equipe penalizada |
| `driver_id` | UUID (FK → drivers.id) | Nullable. Penalized driver / Piloto penalizado |
| `penalty_type` | Enum (native_enum=False) | One of the 5 penalty types / Um dos 5 tipos |
| `reason` | String(512) | Required. Description of the incident / Descricao do incidente |
| `points_deducted` | Float | Default 0.0. Points to subtract / Pontos a subtrair |
| `time_penalty_seconds` | Integer | Nullable. Seconds of time penalty / Segundos de penalidade |
| `lap_number` | Integer | Nullable. Lap where incident occurred / Volta do incidente |
| `is_active` | Boolean | Default true. Inactive penalties have no effect / Inativas sem efeito |
| `created_at` | DateTime(tz) | Auto-set on creation / Definido automaticamente |
| `updated_at` | DateTime(tz) | Auto-updated on changes / Atualizado automaticamente |

---

## Business Rules / Regras de Negocio

### DSQ Auto-Sync / Sincronizacao Automatica de DSQ

When a penalty of type `disqualification` is created or updated:
- If the penalty is **active** AND has a `result_id`, the linked `RaceResult.dsq` is set to `True`
- If a DSQ penalty is **deleted**, **deactivated**, or its type is **changed** from `disqualification`, the system checks for other active DSQ penalties on the same result before reverting `dsq` to `False`

Quando uma penalidade do tipo `disqualification` e criada ou atualizada:
- Se a penalidade esta **ativa** E possui `result_id`, o `RaceResult.dsq` vinculado e definido como `True`
- Se uma penalidade DSQ e **excluida**, **desativada** ou seu tipo e **alterado** de `disqualification`, o sistema verifica outras penalidades DSQ ativas no mesmo resultado antes de reverter `dsq` para `False`

### Standings Impact / Impacto na Classificacao

Only `points_deduction` penalties affect championship standings:
- Active `points_deduction` penalties are summed per team (for team standings) and per driver (for driver standings)
- The total deducted is subtracted from the team's/driver's total earned points
- Standings are re-sorted after deductions and positions re-assigned

Apenas penalidades `points_deduction` afetam a classificacao do campeonato:
- Penalidades ativas de `points_deduction` sao somadas por equipe e por piloto
- O total deduzido e subtraido dos pontos totais ganhos
- A classificacao e re-ordenada apos deducoes e posicoes reatribuidas

---

## Permissions / Permissoes

| Permission / Permissao | Description / Descricao |
|---|---|
| `penalties:read` | List and get penalties / Listar e buscar penalidades |
| `penalties:create` | Create new penalties / Criar novas penalidades |
| `penalties:update` | Update existing penalties / Atualizar penalidades existentes |
| `penalties:delete` | Delete penalties / Excluir penalidades |

The `pilot` role has `penalties:read` by default. Admin has all 4 permissions.

O papel `pilot` tem `penalties:read` por padrao. Admin tem todas as 4 permissoes.

---

## Endpoints

### List Penalties by Race / Listar Penalidades por Corrida

```
GET /api/v1/races/{race_id}/penalties
```

**Auth:** `penalties:read`
**Response:** `200 OK` — `list[PenaltyListResponse]`

### Create Penalty / Criar Penalidade

```
POST /api/v1/races/{race_id}/penalties
```

**Auth:** `penalties:create`
**Body:**
```json
{
  "team_id": "uuid",
  "driver_id": "uuid (optional)",
  "result_id": "uuid (optional)",
  "penalty_type": "warning|time_penalty|points_deduction|disqualification|grid_penalty",
  "reason": "string",
  "points_deducted": 0.0,
  "time_penalty_seconds": null,
  "lap_number": null
}
```
**Response:** `201 Created` — `PenaltyResponse`

### Get Penalty Detail / Buscar Detalhe da Penalidade

```
GET /api/v1/penalties/{penalty_id}
```

**Auth:** `penalties:read`
**Response:** `200 OK` — `PenaltyDetailResponse` (includes nested team/driver info)

### Update Penalty / Atualizar Penalidade

```
PATCH /api/v1/penalties/{penalty_id}
```

**Auth:** `penalties:update`
**Body:** All fields optional — `penalty_type`, `reason`, `points_deducted`, `time_penalty_seconds`, `lap_number`, `result_id`, `driver_id`, `is_active`
**Response:** `200 OK` — `PenaltyResponse`

### Delete Penalty / Excluir Penalidade

```
DELETE /api/v1/penalties/{penalty_id}
```

**Auth:** `penalties:delete`
**Response:** `204 No Content`

---

## Error Responses / Respostas de Erro

| Status | Description / Descricao |
|---|---|
| `401 Unauthorized` | Missing or invalid auth token / Token ausente ou invalido |
| `403 Forbidden` | Insufficient permissions / Permissoes insuficientes |
| `404 Not Found` | Race, team, driver, result, or penalty not found / Recurso nao encontrado |
| `409 Conflict` | Race result does not belong to the specified race / Resultado nao pertence a corrida |
| `422 Unprocessable Entity` | Invalid penalty type or negative points_deducted / Tipo invalido ou pontos negativos |

---

## Test Coverage / Cobertura de Testes

### test_penalties.py (24 tests)
- **List:** empty list, list with data, race not found
- **Create:** all fields, minimal, warning/grid/points_deduction types, race/team/driver/result not found, result wrong race, invalid type
- **Get:** by ID, not found
- **Update:** reason, points, deactivate, not found
- **Delete:** success, not found
- **Auth:** unauthorized (401), forbidden (403)

### test_penalty_dsq_sync.py (8 tests)
- Create DSQ penalty sets result.dsq=True
- Create DSQ without result_id (no crash)
- Delete DSQ penalty reverts result.dsq
- Delete DSQ keeps dsq=True when other DSQ exists
- Update type to/from DSQ syncs flag
- Non-DSQ penalty has no dsq effect
- Inactive DSQ penalty has no sync effect

### test_penalty_standings.py (6 tests)
- Standings without penalties unchanged
- Team standings with points deduction
- Driver standings with points deduction
- Only active penalties deducted
- Only points_deduction type deducted
- Standings reorder after deduction
