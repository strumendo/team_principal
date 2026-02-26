# Standings API Reference / Referencia da API de Classificacao

## Overview / Visao Geral

The Standings API provides championship classification data for teams and drivers, including a detailed race-by-race breakdown endpoint.

A API de Classificacao fornece dados de classificacao de campeonato para equipes e pilotos, incluindo um endpoint de detalhamento corrida-a-corrida.

---

## Endpoints

### 1. Team Standings / Classificacao de Equipes

**`GET /api/v1/championships/{championship_id}/standings`**

Returns team standings ordered by total points (descending). Excludes DSQ results.

Retorna classificacao de equipes ordenada por pontos totais (decrescente). Exclui resultados DSQ.

**Permission / Permissao:** `results:read`

**Response / Resposta:**
```json
[
  {
    "position": 1,
    "team_id": "uuid",
    "team_name": "team_alpha",
    "team_display_name": "Team Alpha",
    "total_points": 50.0,
    "races_scored": 2,
    "wins": 1
  }
]
```

---

### 2. Driver Standings / Classificacao de Pilotos

**`GET /api/v1/championships/{championship_id}/driver-standings`**

Returns driver standings ordered by total points (descending). Only includes results with a `driver_id`. Excludes DSQ results.

Retorna classificacao de pilotos ordenada por pontos totais (decrescente). Inclui apenas resultados com `driver_id`. Exclui resultados DSQ.

**Permission / Permissao:** `results:read`

**Response / Resposta:**
```json
[
  {
    "position": 1,
    "driver_id": "uuid",
    "driver_name": "driver_alpha",
    "driver_display_name": "Driver Alpha",
    "driver_abbreviation": "DRA",
    "team_id": "uuid",
    "team_name": "team_alpha",
    "team_display_name": "Team Alpha",
    "total_points": 25.0,
    "races_scored": 1,
    "wins": 1
  }
]
```

---

### 3. Standings Breakdown / Detalhamento de Classificacao

**`GET /api/v1/championships/{championship_id}/standings/breakdown`**

Returns a full breakdown with finished races as columns and per-race points for each team and driver. Aggregation is done in Python for SQLite test compatibility.

Retorna um detalhamento completo com corridas finalizadas como colunas e pontos por corrida para cada equipe e piloto. A agregacao e feita em Python para compatibilidade com SQLite nos testes.

**Permission / Permissao:** `results:read`

**Response / Resposta:**
```json
{
  "races": [
    {
      "race_id": "uuid",
      "race_name": "round_01",
      "race_display_name": "Round 1",
      "round_number": 1
    }
  ],
  "team_standings": [
    {
      "position": 1,
      "team_id": "uuid",
      "team_name": "team_alpha",
      "team_display_name": "Team Alpha",
      "total_points": 43.0,
      "wins": 1,
      "race_points": [
        {
          "race_id": "uuid",
          "points": 25.0,
          "position": 1,
          "dsq": false
        }
      ]
    }
  ],
  "driver_standings": [
    {
      "position": 1,
      "driver_id": "uuid",
      "driver_name": "driver_alpha",
      "driver_display_name": "Driver Alpha",
      "driver_abbreviation": "DRA",
      "team_id": "uuid",
      "team_name": "team_alpha",
      "team_display_name": "Team Alpha",
      "total_points": 25.0,
      "wins": 1,
      "race_points": [
        {
          "race_id": "uuid",
          "points": 25.0,
          "position": 1,
          "dsq": false
        }
      ]
    }
  ]
}
```

**Notes / Observacoes:**
- DSQ results appear in `race_points` with `dsq: true` and `points: 0.0` / Resultados DSQ aparecem em `race_points` com `dsq: true` e `points: 0.0`
- Only finished races are included / Apenas corridas finalizadas sao incluidas
- Races are ordered by `round_number` / Corridas sao ordenadas por `round_number`
- Teams and drivers are ordered by `total_points` descending / Equipes e pilotos sao ordenados por `total_points` decrescente

---

## Error Responses / Respostas de Erro

| Status | Description / Descricao |
|--------|------------------------|
| 401 | Unauthorized — missing or invalid token / Nao autorizado — token ausente ou invalido |
| 403 | Forbidden — missing `results:read` permission / Proibido — sem permissao `results:read` |
| 404 | Championship not found / Campeonato nao encontrado |

---

## Frontend Pages / Paginas do Frontend

### Standings Hub / Hub de Classificacao

**Route / Rota:** `/standings`

Lists all championships as cards with links to their standings pages. Accessible from the sidebar.

Lista todos os campeonatos como cards com links para suas paginas de classificacao. Acessivel pelo sidebar.

### Championship Standings / Classificacao do Campeonato

**Route / Rota:** `/championships/{id}/standings`

Features / Funcionalidades:
- **Tabs / Abas:** "Teams / Equipes" and "Drivers / Pilotos"
- **Breakdown toggle / Toggle de detalhamento:** shows race-by-race matrix with per-round points
- **Podium styling / Estilo de podio:** gold (1st), silver (2nd), bronze (3rd) with colored left border
- **Responsive:** matrix table on desktop, cards with points grid on mobile
- **DSQ indicator:** strikethrough red text for disqualified results / texto riscado vermelho para resultados desclassificados
