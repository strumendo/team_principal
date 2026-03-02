# Telemetry API / API de Telemetria

EP15 — Lap times, car setups, and driver comparison endpoints.
EP15 — Endpoints de tempos de volta, setups de carro e comparacao de pilotos.

## Overview / Visao Geral

The telemetry module provides endpoints for tracking lap times, sector times, car setup configurations, and driver comparison. Setups are visible to all team members.

O modulo de telemetria fornece endpoints para rastrear tempos de volta, tempos de setor, configuracoes de setup de carro e comparacao de pilotos. Setups sao visiveis por toda a equipe.

## Permissions / Permissoes

| Permission / Permissao | Description / Descricao |
|---|---|
| `telemetry:read` | Read telemetry data / Ler dados de telemetria |
| `telemetry:create` | Create telemetry data / Criar dados de telemetria |
| `telemetry:update` | Update telemetry data / Atualizar dados de telemetria |
| `telemetry:delete` | Delete telemetry data / Excluir dados de telemetria |

## Endpoints

### Lap Times / Tempos de Volta

#### `GET /api/v1/races/{race_id}/laps`
List lap times for a race. / Lista tempos de volta de uma corrida.

**Query Parameters / Parametros de Consulta:**
- `driver_id` (UUID, optional) — Filter by driver / Filtrar por piloto
- `team_id` (UUID, optional) — Filter by team / Filtrar por equipe

**Response:** `200` — `LapTimeResponse[]`

#### `POST /api/v1/races/{race_id}/laps`
Create a single lap time. / Cria um tempo de volta.

**Body:**
```json
{
  "driver_id": "uuid",
  "team_id": "uuid",
  "lap_number": 1,
  "lap_time_ms": 91234,
  "sector_1_ms": 28000,
  "sector_2_ms": 33234,
  "sector_3_ms": 30000,
  "is_valid": true,
  "is_personal_best": false
}
```

**Response:** `201` — `LapTimeResponse`

#### `POST /api/v1/races/{race_id}/laps/bulk`
Bulk create lap times. / Cria tempos de volta em lote.

**Body:**
```json
{
  "laps": [
    { "driver_id": "uuid", "team_id": "uuid", "lap_number": 1, "lap_time_ms": 91234 },
    { "driver_id": "uuid", "team_id": "uuid", "lap_number": 2, "lap_time_ms": 90876 }
  ]
}
```

**Response:** `201` — `LapTimeResponse[]`

#### `GET /api/v1/races/{race_id}/laps/summary`
Get lap time summary: fastest/average per driver and overall fastest.
Resumo de tempos: mais rapido/media por piloto e mais rapido geral.

**Response:** `200` — `LapTimeSummaryResponse`
```json
{
  "drivers": [
    {
      "driver_id": "uuid",
      "driver_display_name": "Max Verstappen",
      "fastest_lap_ms": 90100,
      "avg_lap_ms": 91200,
      "total_laps": 30,
      "personal_best_lap": 15
    }
  ],
  "overall_fastest": { "...LapTimeResponse" }
}
```

#### `DELETE /api/v1/laps/{lap_id}`
Delete a lap time. / Exclui um tempo de volta.

**Response:** `204`

### Car Setups / Setups de Carro

#### `GET /api/v1/races/{race_id}/setups`
List car setups for a race. / Lista setups de carro de uma corrida.

**Query Parameters:** `driver_id`, `team_id` (both optional UUIDs)

**Response:** `200` — `CarSetupResponse[]`

#### `POST /api/v1/races/{race_id}/setups`
Create a car setup. / Cria um setup de carro.

**Body:**
```json
{
  "driver_id": "uuid",
  "team_id": "uuid",
  "name": "Monza Low Downforce",
  "notes": "Optimized for straights",
  "front_wing": 3.5,
  "rear_wing": 2.0,
  "differential": 60.0,
  "brake_bias": 56.0,
  "tire_pressure_fl": 22.5,
  "tire_pressure_fr": 22.5,
  "tire_pressure_rl": 21.0,
  "tire_pressure_rr": 21.0,
  "suspension_stiffness": 7.0,
  "anti_roll_bar": 5.0
}
```

**Response:** `201` — `CarSetupResponse`

#### `GET /api/v1/setups/{setup_id}`
Get setup detail with driver and team info.
Busca detalhe do setup com info do piloto e equipe.

**Response:** `200` — `CarSetupDetailResponse`

#### `PATCH /api/v1/setups/{setup_id}`
Update a car setup (partial update). / Atualiza um setup (atualizacao parcial).

**Response:** `200` — `CarSetupResponse`

#### `DELETE /api/v1/setups/{setup_id}`
Delete a car setup. / Exclui um setup de carro.

**Response:** `204`

### Compare / Comparacao

#### `GET /api/v1/races/{race_id}/telemetry/compare`
Compare lap times for up to 3 drivers. / Compara tempos de volta de ate 3 pilotos.

**Query Parameters:**
- `driver_ids` (string, required) — Comma-separated UUIDs, max 3

**Response:** `200` — `DriverComparison[]`
```json
[
  {
    "driver_id": "uuid",
    "driver_display_name": "Max Verstappen",
    "laps": [ "...LapTimeResponse[]" ]
  }
]
```

## Frontend Pages / Paginas do Frontend

| Page / Pagina | Description / Descricao |
|---|---|
| `/races/[id]/telemetry` | Lap times chart, table, summary, driver filter / Grafico, tabela, resumo, filtro por piloto |
| `/races/[id]/telemetry/compare` | Compare up to 3 drivers with overlay chart / Comparar ate 3 pilotos |
| `/races/[id]/setups` | List, create, edit, delete car setups grouped by driver / CRUD de setups |

## Models / Modelos

### LapTime (`lap_times` table)
- `id` (UUID PK), `race_id`, `driver_id`, `team_id` (FKs)
- `lap_number`, `lap_time_ms` (integers)
- `sector_1_ms`, `sector_2_ms`, `sector_3_ms` (nullable)
- `is_valid`, `is_personal_best` (booleans)
- Unique constraint: `(race_id, driver_id, lap_number)`

### CarSetup (`car_setups` table)
- `id` (UUID PK), `race_id`, `driver_id`, `team_id` (FKs)
- `name` (string), `notes` (text, nullable)
- Aero: `front_wing`, `rear_wing`
- Mechanical: `differential`, `brake_bias`, `suspension_stiffness`, `anti_roll_bar`
- Tires: `tire_pressure_fl/fr/rl/rr`
- `is_active`, `created_at`, `updated_at`
