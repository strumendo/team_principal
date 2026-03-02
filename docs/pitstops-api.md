# Pit Stops & Strategies API / API de Pit Stops e Estrategias

EP16 — Strategy / Pit Stops module endpoints.
Endpoints do modulo EP16 — Estrategia / Pit Stops.

---

## Pit Stop Endpoints / Endpoints de Pit Stop

### List Pit Stops / Listar Pit Stops

```
GET /api/v1/races/{race_id}/pitstops
```

**Permission / Permissao:** `pitstops:read`

**Query parameters / Parametros de consulta:**
- `driver_id` (optional) — Filter by driver / Filtrar por piloto
- `team_id` (optional) — Filter by team / Filtrar por equipe

**Response / Resposta:** `200 OK` — `PitStopResponse[]`

---

### Create Pit Stop / Criar Pit Stop

```
POST /api/v1/races/{race_id}/pitstops
```

**Permission / Permissao:** `pitstops:create`

**Request body / Corpo da requisicao:**
```json
{
  "driver_id": "uuid",
  "team_id": "uuid",
  "lap_number": 15,
  "duration_ms": 2450,
  "tire_from": "soft",
  "tire_to": "medium",
  "notes": "Clean stop"
}
```

**Response / Resposta:** `201 Created` — `PitStopResponse`

**Errors / Erros:**
- `404` — Race, driver, or team not found / Corrida, piloto ou equipe nao encontrados
- `409` — Duplicate pit stop (same race/driver/lap) / Pit stop duplicado

---

### Get Pit Stop Summary / Obter Resumo de Pit Stops

```
GET /api/v1/races/{race_id}/pitstops/summary
```

**Permission / Permissao:** `pitstops:read`

**Response / Resposta:** `200 OK` — `PitStopSummaryResponse`
```json
{
  "drivers": [
    {
      "driver_id": "uuid",
      "driver_display_name": "Lewis Hamilton",
      "total_stops": 3,
      "avg_duration_ms": 2400,
      "fastest_pit_ms": 2300
    }
  ]
}
```

---

### Get Pit Stop Detail / Obter Detalhe do Pit Stop

```
GET /api/v1/pitstops/{pit_stop_id}
```

**Permission / Permissao:** `pitstops:read`

**Response / Resposta:** `200 OK` — `PitStopDetailResponse` (includes driver and team info / inclui dados do piloto e equipe)

---

### Update Pit Stop / Atualizar Pit Stop

```
PATCH /api/v1/pitstops/{pit_stop_id}
```

**Permission / Permissao:** `pitstops:update`

**Request body / Corpo da requisicao:** (all fields optional / todos os campos opcionais)
```json
{
  "duration_ms": 2300,
  "tire_from": "medium",
  "tire_to": "hard",
  "notes": "Updated notes"
}
```

**Response / Resposta:** `200 OK` — `PitStopResponse`

---

### Delete Pit Stop / Excluir Pit Stop

```
DELETE /api/v1/pitstops/{pit_stop_id}
```

**Permission / Permissao:** `pitstops:delete`

**Response / Resposta:** `204 No Content`

---

## Strategy Endpoints / Endpoints de Estrategia

### List Strategies / Listar Estrategias

```
GET /api/v1/races/{race_id}/strategies
```

**Permission / Permissao:** `strategies:read`

**Query parameters / Parametros de consulta:**
- `driver_id` (optional) — Filter by driver / Filtrar por piloto
- `team_id` (optional) — Filter by team / Filtrar por equipe

**Response / Resposta:** `200 OK` — `RaceStrategyResponse[]`

---

### Create Strategy / Criar Estrategia

```
POST /api/v1/races/{race_id}/strategies
```

**Permission / Permissao:** `strategies:create`

**Request body / Corpo da requisicao:**
```json
{
  "driver_id": "uuid",
  "team_id": "uuid",
  "name": "Two Stop Medium-Hard",
  "description": "Start on mediums, switch to hards",
  "target_stops": 2,
  "planned_laps": "15,35",
  "starting_compound": "medium"
}
```

**Response / Resposta:** `201 Created` — `RaceStrategyResponse`

---

### Get Strategy Detail / Obter Detalhe da Estrategia

```
GET /api/v1/strategies/{strategy_id}
```

**Permission / Permissao:** `strategies:read`

**Response / Resposta:** `200 OK` — `RaceStrategyDetailResponse` (includes driver and team info / inclui dados do piloto e equipe)

---

### Update Strategy / Atualizar Estrategia

```
PATCH /api/v1/strategies/{strategy_id}
```

**Permission / Permissao:** `strategies:update`

**Request body / Corpo da requisicao:** (all fields optional / todos os campos opcionais)
```json
{
  "name": "Three Stop Aggressive",
  "description": "Updated strategy",
  "target_stops": 3,
  "planned_laps": "10,25,40",
  "starting_compound": "soft",
  "is_active": false
}
```

**Response / Resposta:** `200 OK` — `RaceStrategyResponse`

---

### Delete Strategy / Excluir Estrategia

```
DELETE /api/v1/strategies/{strategy_id}
```

**Permission / Permissao:** `strategies:delete`

**Response / Resposta:** `204 No Content`

---

## Tire Compounds / Compostos de Pneu

| Compound / Composto | Value / Valor |
|---------------------|---------------|
| Soft / Macio | `soft` |
| Medium / Medio | `medium` |
| Hard / Duro | `hard` |
| Intermediate / Intermediario | `intermediate` |
| Wet / Chuva | `wet` |

---

## Permissions / Permissoes

| Codename | Module | Description / Descricao |
|----------|--------|-------------------------|
| `pitstops:read` | pitstops | Read pit stop data / Ler dados de pit stop |
| `pitstops:create` | pitstops | Create pit stop data / Criar dados de pit stop |
| `pitstops:update` | pitstops | Update pit stop data / Atualizar dados de pit stop |
| `pitstops:delete` | pitstops | Delete pit stop data / Excluir dados de pit stop |
| `strategies:read` | strategies | Read race strategies / Ler estrategias de corrida |
| `strategies:create` | strategies | Create race strategies / Criar estrategias de corrida |
| `strategies:update` | strategies | Update race strategies / Atualizar estrategias de corrida |
| `strategies:delete` | strategies | Delete race strategies / Excluir estrategias de corrida |
