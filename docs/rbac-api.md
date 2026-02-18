# RBAC API Reference / Referencia da API RBAC

## Overview / Visao Geral

The RBAC (Role-Based Access Control) system provides granular permission management through roles and permissions. Superusers bypass all permission checks.

O sistema RBAC (Controle de Acesso Baseado em Papeis) fornece gerenciamento granular de permissoes atraves de papeis e permissoes. Superusuarios ignoram todas as verificacoes de permissao.

## System Permissions / Permissoes do Sistema

| Codename | Module | Description / Descricao |
|---|---|---|
| `auth:register` | auth | Register new users / Registrar novos usuarios |
| `users:read` | users | Read any user / Ler qualquer usuario |
| `users:read_self` | users | Read own profile / Ler perfil proprio |
| `users:update` | users | Update any user / Atualizar qualquer usuario |
| `users:update_self` | users | Update own profile / Atualizar perfil proprio |
| `users:list` | users | List all users / Listar todos os usuarios |
| `users:delete` | users | Delete users / Excluir usuarios |
| `roles:read` | roles | Read roles / Ler papeis |
| `roles:create` | roles | Create roles / Criar papeis |
| `roles:update` | roles | Update roles / Atualizar papeis |
| `roles:delete` | roles | Delete roles / Excluir papeis |
| `roles:assign` | roles | Assign roles to users / Atribuir papeis a usuarios |
| `roles:revoke` | roles | Revoke roles from users / Revogar papeis de usuarios |
| `permissions:read` | permissions | Read permissions / Ler permissoes |
| `permissions:create` | permissions | Create permissions / Criar permissoes |
| `permissions:assign` | permissions | Assign permissions to roles / Atribuir permissoes a papeis |
| `permissions:revoke` | permissions | Revoke permissions from roles / Revogar permissoes de papeis |

## System Roles / Papeis do Sistema

| Role | Default Permissions / Permissoes Padrao |
|---|---|
| `admin` | All permissions / Todas as permissoes |
| `pilot` | `users:read_self`, `users:update_self` |
| `tech_lead` | None (configure as needed) / Nenhuma (configurar conforme necessidade) |
| `performance_lead` | None / Nenhuma |
| `radio_support` | None / Nenhuma |
| `media` | None / Nenhuma |

## Authorization Dependencies / Dependencias de Autorizacao

### `require_permissions(*codenames)` — AND logic / Logica AND

Requires the user to have ALL listed permissions. Superuser bypasses.

Requer que o usuario tenha TODAS as permissoes listadas. Superusuario ignora.

### `require_role(*role_names)` — OR logic / Logica OR

Requires the user to have ANY of the listed roles. Superuser bypasses.

Requer que o usuario tenha QUALQUER dos papeis listados. Superusuario ignora.

## API Endpoints

### Permissions / Permissoes

| Method | Path | Permission | Status | Description |
|---|---|---|---|---|
| GET | `/api/v1/permissions/` | `permissions:read` | 200 | List permissions (filter by `?module=`) |
| GET | `/api/v1/permissions/{id}` | `permissions:read` | 200 | Get permission by ID |
| POST | `/api/v1/permissions/` | `permissions:create` | 201 | Create permission |

### Roles / Papeis

| Method | Path | Permission | Status | Description |
|---|---|---|---|---|
| GET | `/api/v1/roles/` | `roles:read` | 200 | List roles (without permissions) |
| GET | `/api/v1/roles/{id}` | `roles:read` | 200 | Get role with permissions |
| POST | `/api/v1/roles/` | `roles:create` | 201 | Create role |
| PATCH | `/api/v1/roles/{id}` | `roles:update` | 200 | Update role |
| DELETE | `/api/v1/roles/{id}` | `roles:delete` | 204 | Delete role (system roles protected) |
| POST | `/api/v1/roles/{id}/permissions` | `permissions:assign` | 200 | Assign permission to role |
| DELETE | `/api/v1/roles/{id}/permissions/{pid}` | `permissions:revoke` | 200 | Revoke permission from role |

### User Roles / Papeis de Usuario

| Method | Path | Permission | Status | Description |
|---|---|---|---|---|
| GET | `/api/v1/users/{user_id}/roles` | `roles:read` | 200 | List user's roles |
| POST | `/api/v1/users/{user_id}/roles` | `roles:assign` | 200 | Assign role to user |
| DELETE | `/api/v1/users/{user_id}/roles/{role_id}` | `roles:revoke` | 200 | Revoke role from user |

## Error Responses / Respostas de Erro

| Status | Description / Descricao |
|---|---|
| 401 | Not authenticated / Nao autenticado |
| 403 | Insufficient permissions or inactive user / Permissoes insuficientes ou usuario inativo |
| 404 | Resource not found / Recurso nao encontrado |
| 409 | Conflict (duplicate) / Conflito (duplicado) |
