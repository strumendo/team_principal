# RBAC API Reference / Referencia da API RBAC

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [System Permissions / Permissoes do Sistema](#system-permissions--permissoes-do-sistema)
4. [System Roles / Papeis do Sistema](#system-roles--papeis-do-sistema)
5. [Authorization Dependencies / Dependencias de Autorizacao](#authorization-dependencies--dependencias-de-autorizacao)
6. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
7. [API Endpoints — Permissions](#api-endpoints--permissions)
8. [API Endpoints — Roles](#api-endpoints--roles)
9. [API Endpoints — User Roles](#api-endpoints--user-roles)
10. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
11. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
12. [Database Seeding / Seed do Banco de Dados](#database-seeding--seed-do-banco-de-dados)
13. [Test Infrastructure / Infraestrutura de Testes](#test-infrastructure--infraestrutura-de-testes)

---

## Overview / Visao Geral

The RBAC (Role-Based Access Control) system provides granular permission management through roles and permissions. It follows the standard RBAC model where:

- **Users** are assigned **roles**
- **Roles** contain **permissions**
- **Permissions** control access to specific API operations
- **Superusers** (`is_superuser=True`) bypass all permission checks

O sistema RBAC (Controle de Acesso Baseado em Papeis) fornece gerenciamento granular de permissoes. Segue o modelo RBAC padrao onde usuarios recebem papeis, papeis contem permissoes, e permissoes controlam acesso a operacoes especificas da API. Superusuarios ignoram todas as verificacoes.

### Architecture / Arquitetura

```
User ──< user_roles >── Role ──< role_permissions >── Permission
 │                        │
 ├── is_superuser=True    ├── is_system=True (protected)
 │   (bypasses all)       │   (cannot be deleted)
 │                        │
 └── is_active=True       └── permissions[] (selectin loaded)
     (required for access)
```

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/roles/models.py` | ORM models: `Role`, `Permission`, `user_roles`, `role_permissions` |
| `app/roles/schemas.py` | Pydantic request/response schemas |
| `app/roles/service.py` | Business logic (CRUD, assignment, revocation) |
| `app/roles/router.py` | API endpoint definitions (3 routers) |
| `app/core/dependencies.py` | `require_permissions()`, `require_role()` factories |
| `app/db/seed.py` | System roles, permissions, and role-permission seeding |

---

## Data Model / Modelo de Dados

### Entity Relationship Diagram / Diagrama de Entidade-Relacionamento

```
┌──────────────────────────┐
│         users            │
├──────────────────────────┤
│ id          UUID PK      │
│ email       VARCHAR(320) │
│ full_name   VARCHAR(256) │
│ is_active   BOOLEAN      │
│ is_superuser BOOLEAN     │
│ created_at  TIMESTAMPTZ  │
│ updated_at  TIMESTAMPTZ  │
└──────────┬───────────────┘
           │
           │ user_id (FK)
           ▼
┌──────────────────────────┐
│       user_roles         │
├──────────────────────────┤
│ user_id      UUID FK PK  │──→ users.id (CASCADE)
│ role_id      UUID FK PK  │──→ roles.id (CASCADE)
│ assigned_at  TIMESTAMPTZ │
│ assigned_by  UUID FK     │──→ users.id (nullable)
└──────────┬───────────────┘
           │ role_id (FK)
           ▼
┌──────────────────────────┐
│         roles            │
├──────────────────────────┤
│ id           UUID PK     │
│ name         VARCHAR(64) │ UNIQUE, INDEXED
│ display_name VARCHAR(128)│
│ description  VARCHAR(512)│
│ is_system    BOOLEAN     │
│ created_at   TIMESTAMPTZ │
│ updated_at   TIMESTAMPTZ │
└──────────┬───────────────┘
           │
           │ role_id (FK)
           ▼
┌──────────────────────────┐
│    role_permissions      │
├──────────────────────────┤
│ role_id       UUID FK PK │──→ roles.id (CASCADE)
│ permission_id UUID FK PK │──→ permissions.id (CASCADE)
└──────────┬───────────────┘
           │ permission_id (FK)
           ▼
┌──────────────────────────┐
│      permissions         │
├──────────────────────────┤
│ id          UUID PK      │
│ codename    VARCHAR(128) │ UNIQUE, INDEXED
│ description VARCHAR(512) │
│ module      VARCHAR(64)  │ INDEXED
│ created_at  TIMESTAMPTZ  │
│ updated_at  TIMESTAMPTZ  │
└──────────────────────────┘
```

### Association Tables / Tabelas Associativas

**`user_roles`** — N:N relationship between users and roles. Contains `assigned_by` FK to track who assigned the role, and `assigned_at` for audit purposes. Both `user_id` and `role_id` form a composite primary key.

**`role_permissions`** — N:N relationship between roles and permissions. Simple junction table with composite PK of `role_id` and `permission_id`.

**Important:** `user_roles` has TWO foreign keys to `users` (`user_id` and `assigned_by`), which requires explicit `primaryjoin`/`secondaryjoin` on ORM relationships. See `app/roles/models.py:55-62`.

**Importante:** `user_roles` tem DUAS foreign keys para `users` (`user_id` e `assigned_by`), o que requer `primaryjoin`/`secondaryjoin` explicito nos relacionamentos ORM.

### ORM Relationships / Relacionamentos ORM

All relationships use `lazy="selectin"` for eager loading without N+1 queries:

```python
# Role → Permission (bidirectional)
Role.permissions ←→ Permission.roles    # via role_permissions

# Role → User (bidirectional)
Role.users ←→ User.roles               # via user_roles
```

---

## System Permissions / Permissoes do Sistema

17 permissions organized by module. Seeded by `app/db/seed.py`.

17 permissoes organizadas por modulo. Populadas por `app/db/seed.py`.

| Codename | Module | Description / Descricao |
|---|---|---|
| `auth:register` | `auth` | Register new users / Registrar novos usuarios |
| `users:read` | `users` | Read any user profile / Ler perfil de qualquer usuario |
| `users:read_self` | `users` | Read own profile / Ler perfil proprio |
| `users:update` | `users` | Update any user / Atualizar qualquer usuario |
| `users:update_self` | `users` | Update own profile / Atualizar perfil proprio |
| `users:list` | `users` | List all users / Listar todos os usuarios |
| `users:delete` | `users` | Delete users / Excluir usuarios |
| `roles:read` | `roles` | Read roles / Ler papeis |
| `roles:create` | `roles` | Create roles / Criar papeis |
| `roles:update` | `roles` | Update roles / Atualizar papeis |
| `roles:delete` | `roles` | Delete roles / Excluir papeis |
| `roles:assign` | `roles` | Assign roles to users / Atribuir papeis a usuarios |
| `roles:revoke` | `roles` | Revoke roles from users / Revogar papeis de usuarios |
| `permissions:read` | `permissions` | Read permissions / Ler permissoes |
| `permissions:create` | `permissions` | Create permissions / Criar permissoes |
| `permissions:assign` | `permissions` | Assign permissions to roles / Atribuir permissoes a papeis |
| `permissions:revoke` | `permissions` | Revoke permissions from roles / Revogar permissoes de papeis |

---

## System Roles / Papeis do Sistema

6 system roles (`is_system=True` — cannot be deleted). Seeded by `app/db/seed.py`.

6 papeis do sistema (`is_system=True` — nao podem ser excluidos). Populados por `app/db/seed.py`.

| Role | Display Name | Default Permissions | Description |
|---|---|---|---|
| `admin` | Admin | **All 17 permissions** | Full system access |
| `pilot` | Pilot | `users:read_self`, `users:update_self` | Driver with own data access |
| `tech_lead` | Tech Lead | *(none — configure as needed)* | Technical leadership |
| `performance_lead` | Performance Lead | *(none)* | Performance analysis |
| `radio_support` | Radio/Support | *(none)* | Communication and race support |
| `media` | Media | *(none)* | Content creation and media |

---

## Authorization Dependencies / Dependencias de Autorizacao

Defined in `app/core/dependencies.py`. These are FastAPI dependency factories that return `Depends()`-compatible callables.

Definidas em `app/core/dependencies.py`. Sao fabricas de dependencia FastAPI que retornam callables compativeis com `Depends()`.

### Authentication Chain / Cadeia de Autenticacao

```
HTTP Request
  │
  ▼
OAuth2PasswordBearer (extracts Bearer token from header)
  │
  ▼
get_current_user (decodes JWT, queries User from DB)
  │
  ▼
get_current_active_user (checks is_active=True)
  │
  ▼
require_permissions(*codenames)  OR  require_role(*role_names)
  │                                    │
  ▼                                    ▼
Checks ALL permissions (AND)     Checks ANY role (OR)
  │                                    │
  ▼                                    ▼
Returns User or raises 403       Returns User or raises 403
```

### `require_permissions(*codenames)` — AND Logic / Logica AND

Requires the authenticated user to have **ALL** listed permissions. Superuser (`is_superuser=True`) bypasses all checks.

Requer que o usuario tenha **TODAS** as permissoes listadas. Superusuario ignora todas as verificacoes.

**How it works / Como funciona:**
1. Depends on `get_current_active_user` (which depends on `get_current_user`)
2. If `is_superuser=True`, returns user immediately (bypass)
3. Iterates through `user.roles[].permissions[]` to collect all permission codenames
4. Computes `missing = requested_codenames - user_codenames`
5. If any missing, raises `ForbiddenException` with the list of missing permissions

**Usage / Uso:**
```python
@router.get("/")
async def list_items(
    user: User = Depends(require_permissions("items:read")),
):
    ...

# Multiple permissions (AND logic):
@router.delete("/{id}")
async def delete_item(
    user: User = Depends(require_permissions("items:read", "items:delete")),
):
    ...
```

### `require_role(*role_names)` — OR Logic / Logica OR

Requires the authenticated user to have **ANY** of the listed roles. Superuser bypasses.

Requer que o usuario tenha **QUALQUER** dos papeis listados. Superusuario ignora.

**Usage / Uso:**
```python
@router.get("/admin-panel")
async def admin_panel(
    user: User = Depends(require_role("admin", "tech_lead")),
):
    ...
```

---

## Pydantic Schemas / Schemas Pydantic

Defined in `app/roles/schemas.py`. All response schemas use `model_config = {"from_attributes": True}` for ORM model compatibility.

### Request Schemas / Schemas de Requisicao

**`PermissionCreateRequest`**
```json
{
    "codename": "items:read",
    "module": "items",
    "description": "Read items"
}
```

**`RoleCreateRequest`**
```json
{
    "name": "editor",
    "display_name": "Editor",
    "description": "Content editor role"
}
```

**`RoleUpdateRequest`** (all fields optional / todos os campos opcionais)
```json
{
    "display_name": "Senior Editor",
    "description": "Updated description"
}
```

**`RolePermissionRequest`**
```json
{
    "permission_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**`UserRoleAssignRequest`**
```json
{
    "role_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Schemas / Schemas de Resposta

**`PermissionResponse`**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "codename": "users:read",
    "description": "Read any user",
    "module": "users",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**`RoleResponse`** (includes nested permissions / inclui permissoes aninhadas)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "admin",
    "display_name": "Admin",
    "description": "Full system access",
    "is_system": true,
    "permissions": [
        {
            "id": "...",
            "codename": "users:read",
            "description": "Read any user",
            "module": "users",
            "created_at": "...",
            "updated_at": "..."
        }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**`RoleListResponse`** (without permissions — used in list endpoints / sem permissoes — usado em endpoints de listagem)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "admin",
    "display_name": "Admin",
    "description": "Full system access",
    "is_system": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

---

## API Endpoints — Permissions

**Router:** `permissions_router` — prefix `/api/v1/permissions`
**File:** `app/roles/router.py`

### GET `/api/v1/permissions/`

List all permissions, optionally filtered by module.

Lista todas as permissoes, opcionalmente filtradas por modulo.

| Parameter | Type | In | Required | Description |
|---|---|---|---|---|
| `module` | `string` | query | No | Filter by module name |
| `Authorization` | `Bearer <token>` | header | Yes | JWT access token |

**Required permission:** `permissions:read`
**Response:** `200 OK` — `list[PermissionResponse]`

### GET `/api/v1/permissions/{permission_id}`

Get a permission by ID.

| Parameter | Type | In | Required |
|---|---|---|---|
| `permission_id` | `UUID` | path | Yes |

**Required permission:** `permissions:read`
**Response:** `200 OK` — `PermissionResponse`
**Errors:** `404` if not found

### POST `/api/v1/permissions/`

Create a new permission.

**Required permission:** `permissions:create`
**Request body:** `PermissionCreateRequest`
**Response:** `201 Created` — `PermissionResponse`
**Errors:** `409` if codename already exists

---

## API Endpoints — Roles

**Router:** `roles_router` — prefix `/api/v1/roles`
**File:** `app/roles/router.py`

### GET `/api/v1/roles/`

List all roles (without permissions for performance).

**Required permission:** `roles:read`
**Response:** `200 OK` — `list[RoleListResponse]`

### GET `/api/v1/roles/{role_id}`

Get a role by ID with its permissions (nested).

**Required permission:** `roles:read`
**Response:** `200 OK` — `RoleResponse`
**Errors:** `404` if not found

### POST `/api/v1/roles/`

Create a new role. New roles are NOT system roles (`is_system=False`).

**Required permission:** `roles:create`
**Request body:** `RoleCreateRequest`
**Response:** `201 Created` — `RoleResponse`
**Errors:** `409` if name already exists

### PATCH `/api/v1/roles/{role_id}`

Update a role's display name or description.

**Required permission:** `roles:update`
**Request body:** `RoleUpdateRequest`
**Response:** `200 OK` — `RoleResponse`
**Errors:** `404` if not found

### DELETE `/api/v1/roles/{role_id}`

Delete a non-system role. System roles (`is_system=True`) cannot be deleted.

**Required permission:** `roles:delete`
**Response:** `204 No Content`
**Errors:** `403` if system role, `404` if not found

### POST `/api/v1/roles/{role_id}/permissions`

Assign a permission to a role.

**Required permission:** `permissions:assign`
**Request body:** `RolePermissionRequest`
**Response:** `200 OK` — `RoleResponse` (updated role with permissions)
**Errors:** `404` if role/permission not found, `409` if already assigned

### DELETE `/api/v1/roles/{role_id}/permissions/{permission_id}`

Revoke a permission from a role.

**Required permission:** `permissions:revoke`
**Response:** `200 OK` — `RoleResponse` (updated role with permissions)
**Errors:** `404` if role/permission not found or not assigned

---

## API Endpoints — User Roles

**Router:** `user_roles_router` — prefix `/api/v1/users`
**File:** `app/roles/router.py`

### GET `/api/v1/users/{user_id}/roles`

List all roles assigned to a user.

**Required permission:** `roles:read`
**Response:** `200 OK` — `list[RoleListResponse]`
**Errors:** `404` if user not found

### POST `/api/v1/users/{user_id}/roles`

Assign a role to a user. Records `assigned_by` (the current user's ID) and `assigned_at` in the `user_roles` table.

Atribui um papel a um usuario. Registra `assigned_by` (ID do usuario atual) e `assigned_at` na tabela `user_roles`.

**Required permission:** `roles:assign`
**Request body:** `UserRoleAssignRequest`
**Response:** `200 OK` — `list[RoleListResponse]` (updated list of user's roles)
**Errors:** `404` if user/role not found, `409` if role already assigned

**Implementation note:** Uses direct `INSERT INTO user_roles` instead of ORM relationship to set `assigned_by`. See [Troubleshooting — Stale ORM Cache](troubleshooting.md#3-stale-orm-relationship-cache).

### DELETE `/api/v1/users/{user_id}/roles/{role_id}`

Revoke a role from a user.

**Required permission:** `roles:revoke`
**Response:** `200 OK` — `list[RoleListResponse]` (updated list of user's roles)
**Errors:** `404` if user/role not found or not assigned

---

## Error Responses / Respostas de Erro

All errors follow the FastAPI default format:

```json
{
    "detail": "Error description"
}
```

| Status | Exception Class | Description / Descricao |
|---|---|---|
| `401 Unauthorized` | `CredentialsException` | Invalid/expired token, invalid token type, user not found |
| `403 Forbidden` | `ForbiddenException` | Missing permissions, inactive user, cannot delete system role |
| `404 Not Found` | `NotFoundException` | Resource (user, role, permission) not found |
| `409 Conflict` | `ConflictException` | Duplicate codename, name, or assignment |

### Error Examples / Exemplos de Erro

**401 — Invalid token:**
```json
{"detail": "Could not validate credentials"}
```

**403 — Missing permissions:**
```json
{"detail": "Missing permissions: roles:create, roles:delete"}
```

**403 — System role protection:**
```json
{"detail": "Cannot delete system role"}
```

**404 — Resource not found:**
```json
{"detail": "Role not found"}
```

**409 — Duplicate assignment:**
```json
{"detail": "Permission already assigned to role"}
```

---

## Service Layer / Camada de Servico

All business logic is in `app/roles/service.py`. Functions follow the pattern: validate → check conflicts → perform operation → commit.

Toda logica de negocios esta em `app/roles/service.py`. Funcoes seguem o padrao: validar → verificar conflitos → executar operacao → commit.

### Permission Services

| Function | Signature | Description |
|---|---|---|
| `list_permissions` | `(db, module=None) -> list[Permission]` | List permissions, optional module filter |
| `get_permission_by_id` | `(db, permission_id) -> Permission` | Get by ID or raise 404 |
| `create_permission` | `(db, codename, module, description=None) -> Permission` | Create or raise 409 if duplicate |

### Role Services

| Function | Signature | Description |
|---|---|---|
| `list_roles` | `(db) -> list[Role]` | List all roles ordered by name |
| `get_role_by_id` | `(db, role_id) -> Role` | Get by ID or raise 404 |
| `create_role` | `(db, name, display_name, description=None) -> Role` | Create or raise 409 if duplicate |
| `update_role` | `(db, role, display_name=None, description=None) -> Role` | Update fields |
| `delete_role` | `(db, role) -> None` | Delete or raise 403 if system role |
| `assign_permission_to_role` | `(db, role_id, permission_id) -> Role` | Assign or raise 409 if duplicate |
| `revoke_permission_from_role` | `(db, role_id, permission_id) -> Role` | Revoke or raise 404 if not assigned |

### User-Role Services

| Function | Signature | Description |
|---|---|---|
| `list_user_roles` | `(db, user_id) -> list[Role]` | List via explicit JOIN (not ORM relationship) |
| `assign_role_to_user` | `(db, user_id, role_id, assigned_by=None) -> None` | Direct INSERT for assigned_by support |
| `revoke_role_from_user` | `(db, user_id, role_id) -> None` | Direct DELETE on user_roles |

---

## Database Seeding / Seed do Banco de Dados

**File:** `app/db/seed.py`
**Usage / Uso:** `poetry run python -m app.db.seed`

The seed script is **idempotent** — safe to run multiple times. It checks for existing records before creating.

O script de seed e **idempotente** — seguro para executar multiplas vezes. Verifica registros existentes antes de criar.

### Seed Order / Ordem do Seed

1. `seed_roles()` — Creates 6 system roles
2. `seed_permissions()` — Creates 17 system permissions
3. `seed_role_permissions()` — Assigns permissions to roles (admin: all, pilot: self-access)

### Adding New Permissions / Adicionando Novas Permissoes

1. Add entry to `SYSTEM_PERMISSIONS` list in `app/db/seed.py`
2. (Optional) Add to `ROLE_PERMISSIONS` dict for default role assignments
3. Run `python -m app.db.seed`
4. Use the codename in `require_permissions()` on your endpoint

---

## Test Infrastructure / Infraestrutura de Testes

**Framework:** pytest + pytest-asyncio + httpx (AsyncClient)
**Database:** In-memory SQLite (`sqlite+aiosqlite://`) — no PostgreSQL needed for tests
**Config:** `asyncio_mode = "auto"` in `pyproject.toml`

O banco de dados de testes usa SQLite em memoria — nao precisa de PostgreSQL para executar testes.

### Test Files / Arquivos de Teste

| File | Tests | Description |
|---|---|---|
| `tests/test_permissions.py` | 7 | Permissions CRUD + auth |
| `tests/test_roles.py` | 13 | Roles CRUD + system role protection + permission assignment |
| `tests/test_rbac.py` | 12 | Permission enforcement, superuser bypass, role/permission AND/OR logic |
| `tests/test_user_roles.py` | 10 | User-role assignment/revocation + assigned_by audit |
| `tests/test_auth.py` | 7 | Authentication (register, login, refresh) |
| `tests/test_users.py` | 5 | User profile operations |
| `tests/test_health.py` | 2 | Health check endpoints |
| **Total** | **56** | |

### Key Test Fixtures / Fixtures Chave

Defined in `tests/conftest.py`:

| Fixture | Description |
|---|---|
| `db` | Async SQLite session with fresh schema per test |
| `client` | httpx AsyncClient pointing to the test app |
| `test_user` / `auth_headers` | Regular authenticated user |
| `admin_user` / `admin_headers` | User with admin role + all permissions |
| `superuser` / `superuser_headers` | User with `is_superuser=True` (bypasses all) |

### Running Tests / Executando Testes

```bash
cd backend
poetry run pytest -v              # All tests with verbose output
poetry run pytest tests/test_rbac.py  # Specific test file
poetry run pytest -k "superuser"  # Tests matching keyword
```
