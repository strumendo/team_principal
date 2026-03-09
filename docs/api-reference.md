# API Reference Index / Indice de Referencia da API

## Overview / Visao Geral

The TeamPrincipal API is a RESTful API built with FastAPI. All endpoints are prefixed with `/api/v1/`. Authentication uses JWT Bearer tokens.

A API do TeamPrincipal e uma API RESTful construida com FastAPI. Todos os endpoints sao prefixados com `/api/v1/`. A autenticacao usa tokens JWT Bearer.

**Base URL:** `http://localhost:8000/api/v1`
**Interactive docs:** `http://localhost:8000/docs` (Swagger UI)
**Alternative docs:** `http://localhost:8000/redoc` (ReDoc)

---

## Authentication / Autenticacao

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login and get JWT token / Login e obter token JWT |
| POST | `/auth/register` | Register a new user / Registrar novo usuario |
| POST | `/auth/refresh` | Refresh JWT token / Renovar token JWT |
| GET | `/auth/me` | Get current user info / Obter info do usuario atual |

**Details:** Authentication is handled via JWT (python-jose + bcrypt). Tokens are passed in the `Authorization: Bearer <token>` header.

**Detalhes:** Autenticacao e feita via JWT (python-jose + bcrypt). Tokens sao passados no header `Authorization: Bearer <token>`.

---

## API Modules / Modulos da API

### Core Modules / Modulos Principais

| Module | Endpoints | Doc Reference | Description |
|--------|-----------|---------------|-------------|
| **Championships** | 7 | [championships-api.md](./championships-api.md) | CRUD for championships, enrollment management |
| **Races** | 8 | [races-api.md](./races-api.md) | CRUD for races, entry management |
| **Teams** | 6 | [teams-api.md](./teams-api.md) | CRUD for teams |
| **Drivers** | 6 | [drivers-api.md](./drivers-api.md) | CRUD for drivers/pilotos |
| **Race Results** | 5 | [race-results-api.md](./race-results-api.md) | Results submission and standings |

### Analysis & Telemetry / Analise e Telemetria

| Module | Endpoints | Doc Reference | Description |
|--------|-----------|---------------|-------------|
| **Telemetry** | 11 | [telemetry-api.md](./telemetry-api.md) | Lap times, car setups, bulk import, driver comparison |
| **Pit Stops** | 5 | [pitstops-api.md](./pitstops-api.md) | Pit stop recording and summary |
| **Strategies** | 6 | [pitstops-api.md](./pitstops-api.md) | Race strategies management |
| **Race Replay** | 15 | [ep17-race-replay.md](./ep17-race-replay.md) | Lap positions, race events, analysis (replay/stints/overtakes/summary) |
| **Standings** | 3 | [standings-api.md](./standings-api.md) | Standings breakdown by race |

### Platform Features / Funcionalidades da Plataforma

| Module | Endpoints | Doc Reference | Description |
|--------|-----------|---------------|-------------|
| **Calendar** | 1 | [calendar-api.md](./calendar-api.md) | Race calendar with championship filter |
| **Dashboard** | 3 | [dashboard-api.md](./dashboard-api.md) | Dashboard metrics and statistics |
| **Notifications** | 2 | [notifications-api.md](./notifications-api.md) | WebSocket notifications + polling |
| **Uploads** | 3 | [uploads-api.md](./uploads-api.md) | File uploads (avatars, logos, photos) |

### Administration / Administracao

| Module | Endpoints | Doc Reference | Description |
|--------|-----------|---------------|-------------|
| **Admin Panel** | 4 | [admin-panel-api.md](./admin-panel-api.md) | User management (admin-only) |
| **RBAC** | 8 | [rbac-api.md](./rbac-api.md) | Roles and permissions management |

---

## Common Patterns / Padroes Comuns

### Request Format / Formato de Requisicao

```bash
# GET request with auth
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/championships

# POST request with body
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "f1-2026", "display_name": "F1 2026"}' \
  http://localhost:8000/api/v1/championships
```

### Response Format / Formato de Resposta

All endpoints return JSON. Successful responses return the data directly. Error responses follow this format:

Todos os endpoints retornam JSON. Respostas de sucesso retornam os dados diretamente. Respostas de erro seguem este formato:

```json
{
  "detail": "Error message / Mensagem de erro"
}
```

### Pagination / Paginacao

List endpoints support `skip` and `limit` query parameters:
Endpoints de listagem suportam parametros `skip` e `limit`:

```
GET /api/v1/championships?skip=0&limit=20
```

### Status Codes / Codigos de Status

| Code | Meaning |
|------|---------|
| 200 | Success / Sucesso |
| 201 | Created / Criado |
| 204 | No Content (delete) / Sem Conteudo (exclusao) |
| 400 | Bad Request / Requisicao invalida |
| 401 | Unauthorized / Nao autorizado |
| 403 | Forbidden / Proibido |
| 404 | Not Found / Nao encontrado |
| 422 | Validation Error / Erro de validacao |

### Filtering / Filtragem

Many list endpoints support filtering via query parameters:
Muitos endpoints de listagem suportam filtragem via parametros de consulta:

```
GET /api/v1/championships?status=active&season_year=2026&is_active=true
GET /api/v1/races?championship_id=<uuid>&status=scheduled
```

### UUID Primary Keys / Chaves Primarias UUID

All entities use UUIDs as primary keys. Example format: `550e8400-e29b-41d4-a716-446655440000`

Todas as entidades usam UUIDs como chaves primarias.

---

## Permission System / Sistema de Permissoes

The API uses a role-based access control (RBAC) system. Each endpoint requires specific permissions:

A API usa um sistema de controle de acesso baseado em papeis (RBAC). Cada endpoint requer permissoes especificas:

| Module | Permissions |
|--------|------------|
| Championships | `championships:read`, `championships:create`, `championships:update`, `championships:delete` |
| Races | `races:read`, `races:create`, `races:update`, `races:delete` |
| Teams | `teams:read`, `teams:create`, `teams:update`, `teams:delete` |
| Drivers | `drivers:read`, `drivers:create`, `drivers:update`, `drivers:delete` |
| Results | `results:read`, `results:create`, `results:update` |
| Telemetry | `telemetry:read`, `telemetry:create`, `telemetry:update`, `telemetry:delete` |
| Pit Stops | `pitstops:read`, `pitstops:create`, `pitstops:update`, `pitstops:delete` |
| Strategies | `strategies:read`, `strategies:create`, `strategies:update`, `strategies:delete` |
| Replay | `replay:read`, `replay:create`, `replay:update`, `replay:delete` |
| Users | `users:read`, `users:create`, `users:update` |
| Roles | `roles:read`, `roles:create`, `roles:update`, `roles:delete` |
| Uploads | `uploads:create` |

---

## WebSocket / WebSocket

The API provides a WebSocket endpoint for real-time notifications:

A API fornece um endpoint WebSocket para notificacoes em tempo real:

```
ws://localhost:8000/ws?token=<jwt_token>
```

See [notifications-api.md](./notifications-api.md) for details.

---

## Health Check / Verificacao de Saude

| Method | Endpoint | Auth Required |
|--------|----------|---------------|
| GET | `/api/v1/health` | No |

Returns `{"status": "ok"}` when the API is healthy.
