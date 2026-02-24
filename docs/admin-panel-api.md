# Admin Panel API Reference / Referencia da API do Painel Admin

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [New Backend Endpoints / Novos Endpoints do Backend](#new-backend-endpoints--novos-endpoints-do-backend)
3. [Schemas / Schemas](#schemas--schemas)
4. [Frontend Pages / Paginas do Frontend](#frontend-pages--paginas-do-frontend)
5. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
6. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Admin Panel (EP10) adds visual management of users, roles, and permissions through the frontend. The backend was extended with two new endpoints for user listing and admin-level user updates. The frontend provides six new pages under `/admin/` for managing the complete RBAC system.

O Painel Admin (EP10) adiciona gerenciamento visual de usuarios, papeis e permissoes no frontend. O backend foi estendido com dois novos endpoints para listagem e atualizacao admin de usuarios. O frontend fornece seis novas paginas em `/admin/` para gerenciar o sistema RBAC completo.

### Architecture / Arquitetura

```
Frontend (Admin Pages)          Backend (API)
┌──────────────────────┐       ┌──────────────────────────┐
│ /admin/users         │──────>│ GET  /api/v1/users/      │
│ /admin/users/[id]    │──────>│ PATCH /api/v1/users/{id} │
│                      │──────>│ GET/POST/DELETE user roles│
│ /admin/roles         │──────>│ GET  /api/v1/roles/      │
│ /admin/roles/[id]    │──────>│ CRUD /api/v1/roles/{id}  │
│ /admin/roles/create  │──────>│ POST /api/v1/roles/      │
│ /admin/permissions   │──────>│ GET  /api/v1/permissions/ │
└──────────────────────┘       └──────────────────────────┘
```

---

## New Backend Endpoints / Novos Endpoints do Backend

### GET `/api/v1/users/`

List all users with optional filters.

Lista todos os usuarios com filtros opcionais.

| Parameter / Parametro | Type / Tipo | In | Required / Obrigatorio | Description / Descricao |
|---|---|---|---|---|
| `is_active` | `boolean` | query | No | Filter by active status / Filtrar por status ativo |
| `search` | `string` | query | No | Search by name or email (ilike) / Buscar por nome ou email |
| `Authorization` | `Bearer <token>` | header | Yes / Sim | JWT access token |

**Required permission / Permissao requerida:** `users:list`

**Response / Resposta:** `200 OK` — `list[UserListResponse]`

**Example / Exemplo:**
```bash
# List all active users / Listar todos os usuarios ativos
GET /api/v1/users/?is_active=true

# Search by name / Buscar por nome
GET /api/v1/users/?search=John
```

### PATCH `/api/v1/users/{user_id}`

Admin update a user's profile fields.

Atualizacao admin de campos do perfil de um usuario.

| Parameter / Parametro | Type / Tipo | In | Required / Obrigatorio | Description / Descricao |
|---|---|---|---|---|
| `user_id` | `UUID` | path | Yes / Sim | Target user ID / ID do usuario alvo |
| `Authorization` | `Bearer <token>` | header | Yes / Sim | JWT access token |

**Required permission / Permissao requerida:** `users:update`

**Request body / Corpo da requisicao:** `AdminUserUpdate`

```json
{
    "full_name": "Updated Name",
    "email": "new@email.com",
    "is_active": false
}
```

All fields are optional. Email change checks for uniqueness.

Todos os campos sao opcionais. Mudanca de email verifica unicidade.

**Response / Resposta:** `200 OK` — `UserResponse`

**Errors / Erros:** `404` if user not found, `409` if email already in use, `403` if missing permission

---

## Schemas / Schemas

### UserListResponse

Used in `GET /api/v1/users/` list endpoint.

```json
{
    "id": "550e8400-...",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false,
    "avatar_url": null,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

### AdminUserUpdate

Used in `PATCH /api/v1/users/{user_id}` admin update endpoint.

```json
{
    "full_name": "string (optional)",
    "email": "string (optional)",
    "is_active": "boolean (optional)"
}
```

**Note / Nota:** This is separate from `UserUpdate` (self-update), which only allows `full_name` and `avatar_url`. Admin update allows `email` and `is_active` but does NOT allow changing `is_superuser` or `password`.

---

## Frontend Pages / Paginas do Frontend

### Admin Users / Usuarios Admin

| Page / Pagina | Path / Caminho | Description / Descricao |
|---|---|---|
| Users List | `/admin/users` | Search + is_active filter, table with email, name, badges |
| User Detail | `/admin/users/[id]` | Edit form (name, email, active toggle) + role management |

### Admin Roles / Papeis Admin

| Page / Pagina | Path / Caminho | Description / Descricao |
|---|---|---|
| Roles List | `/admin/roles` | Table with name, display_name, system badge, description |
| Create Role | `/admin/roles/create` | Form: name, display_name, description |
| Role Detail | `/admin/roles/[id]` | Edit form (non-system only) + permission management |

### Admin Permissions / Permissoes Admin

| Page / Pagina | Path / Caminho | Description / Descricao |
|---|---|---|
| Permissions List | `/admin/permissions` | Read-only table with module filter |

### Design Notes / Notas de Design

- All pages use the `"use client"` + `useSession()` + `useState` pattern
- No client-side permission checking — the API returns 403 if unauthorized
- Admin sidebar section is visible to all authenticated users; backend enforces access
- No pagination (consistent with all other list endpoints in the project)

---

## Error Responses / Respostas de Erro

| Status | Description / Descricao |
|---|---|
| `401 Unauthorized` | Missing or invalid token / Token ausente ou invalido |
| `403 Forbidden` | Missing `users:list` or `users:update` permission / Permissao ausente |
| `404 Not Found` | User not found / Usuario nao encontrado |
| `409 Conflict` | Email already in use / Email ja em uso |

---

## Test Coverage / Cobertura de Testes

14 new tests added to `tests/test_users.py` (total: 19):

14 novos testes adicionados a `tests/test_users.py` (total: 19):

| Test | Description / Descricao |
|---|---|
| `test_list_users` | Returns list with admin_user |
| `test_list_users_multiple` | Returns multiple users |
| `test_list_users_filter_active` | is_active=true filter |
| `test_list_users_filter_inactive` | is_active=false filter |
| `test_list_users_search_name` | Search by name |
| `test_list_users_search_email` | Search by email |
| `test_list_users_unauthorized` | 401 without token |
| `test_list_users_forbidden` | 403 without users:list |
| `test_admin_update_user_full_name` | Updates full_name |
| `test_admin_update_user_deactivate` | Sets is_active=false |
| `test_admin_update_user_email` | Updates email |
| `test_admin_update_user_email_conflict` | 409 duplicate email |
| `test_admin_update_user_not_found` | 404 invalid ID |
| `test_admin_update_user_forbidden` | 403 without users:update |
