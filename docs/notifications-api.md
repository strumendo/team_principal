# Notifications API / API de Notificacoes

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Permissions / Permissoes](#permissions--permissoes)
3. [Endpoints](#endpoints)
4. [Request & Response Schemas / Schemas de Requisicao & Resposta](#request--response-schemas--schemas-de-requisicao--resposta)
5. [Notification Types / Tipos de Notificacao](#notification-types--tipos-de-notificacao)
6. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
7. [Entity Linking / Vinculacao de Entidade](#entity-linking--vinculacao-de-entidade)
8. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
9. [Tests / Testes](#tests--testes)

---

## Overview / Visao Geral

The notifications module provides an in-app notification system using REST polling. Users can view, filter, mark as read, and delete their own notifications. Admins with the `notifications:create` permission can create and broadcast notifications to one or more users.

O modulo de notificacoes fornece um sistema de notificacao in-app usando polling REST. Usuarios podem visualizar, filtrar, marcar como lida e excluir suas proprias notificacoes. Admins com a permissao `notifications:create` podem criar e enviar notificacoes para um ou mais usuarios.

Key design decisions:
- **REST polling** — no WebSockets, frontend polls `/unread-count` every 60s
- **User-scoped** — each user only sees their own notifications
- **Ownership enforcement** — mark-read, delete operations validate `user_id` match
- **Bulk operations** — `mark-all-read` uses a single UPDATE statement for efficiency
- **Entity linking** — notifications can reference entities (race, championship, team) for deep linking

Decisoes de design chave:
- **Polling REST** — sem WebSockets, frontend consulta `/unread-count` a cada 60s
- **Escopo do usuario** — cada usuario so ve suas proprias notificacoes
- **Validacao de propriedade** — operacoes de marcar lida e excluir validam correspondencia de `user_id`
- **Operacoes em massa** — `mark-all-read` usa uma unica instrucao UPDATE para eficiencia
- **Vinculacao de entidade** — notificacoes podem referenciar entidades (corrida, campeonato, equipe) para deep linking

---

## Permissions / Permissoes

| Endpoint | Permission Required |
|---|---|
| `GET /notifications/` | Authenticated user (own only) |
| `GET /notifications/unread-count` | Authenticated user (own only) |
| `PATCH /notifications/{id}/read` | Authenticated user (own only) |
| `POST /notifications/mark-all-read` | Authenticated user (own only) |
| `DELETE /notifications/{id}` | Authenticated user (own only) |
| `POST /notifications/` | `notifications:create` (admin) |

Three new permissions are added to the seed:
- `notifications:read` — included in the `pilot` role
- `notifications:create` — admin only
- `notifications:delete` — admin only

Tres novas permissoes sao adicionadas ao seed:
- `notifications:read` — incluida no papel `pilot`
- `notifications:create` — somente admin
- `notifications:delete` — somente admin

---

## Endpoints

### GET /api/v1/notifications/

List own notifications with optional filters.

Lista as proprias notificacoes com filtros opcionais.

**Query Parameters:**

| Param | Type | Description (EN) | Descricao (pt-BR) |
|---|---|---|---|
| `is_read` | bool (optional) | Filter by read status | Filtrar por status de leitura |
| `type` | string (optional) | Filter by notification type | Filtrar por tipo de notificacao |

**Response:** `200 OK` with `NotificationListResponse[]`

---

### GET /api/v1/notifications/unread-count

Get count of unread notifications for the current user.

Retorna a contagem de notificacoes nao lidas do usuario atual.

**Response:** `200 OK` with `UnreadCountResponse`

```json
{
  "unread_count": 5
}
```

---

### PATCH /api/v1/notifications/{id}/read

Mark a notification as read. Only the owner can mark it.

Marca uma notificacao como lida. Apenas o dono pode marca-la.

**Response:** `200 OK` with `NotificationResponse`

---

### POST /api/v1/notifications/mark-all-read

Mark all unread notifications as read for the current user.

Marca todas as notificacoes nao lidas como lidas para o usuario atual.

**Response:** `200 OK`

```json
{
  "marked_count": 3
}
```

---

### DELETE /api/v1/notifications/{id}

Delete own notification. Only the owner can delete it.

Exclui a propria notificacao. Apenas o dono pode exclui-la.

**Response:** `204 No Content`

---

### POST /api/v1/notifications/

Create notification(s). Admin only — requires `notifications:create` permission. If `user_ids` is provided, broadcasts to all listed users.

Cria notificacao(oes). Somente admin — requer permissao `notifications:create`. Se `user_ids` for fornecido, envia para todos os usuarios listados.

**Request Body:** `NotificationCreateRequest`

**Response:** `201 Created` with `NotificationResponse[]`

---

## Request & Response Schemas / Schemas de Requisicao & Resposta

### NotificationListResponse

```json
{
  "id": "uuid",
  "type": "race_scheduled",
  "title": "Race Scheduled: Monaco GP",
  "message": "The race 'Monaco GP' has been scheduled.",
  "entity_type": "race",
  "entity_id": "uuid",
  "is_read": false,
  "created_at": "2026-02-23T10:00:00Z"
}
```

### NotificationResponse

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "type": "race_scheduled",
  "title": "Race Scheduled: Monaco GP",
  "message": "The race 'Monaco GP' has been scheduled.",
  "entity_type": "race",
  "entity_id": "uuid",
  "is_read": false,
  "created_at": "2026-02-23T10:00:00Z",
  "updated_at": "2026-02-23T10:00:00Z"
}
```

### NotificationCreateRequest

```json
{
  "type": "general",
  "title": "System Announcement",
  "message": "Maintenance window scheduled.",
  "entity_type": null,
  "entity_id": null,
  "user_ids": ["uuid1", "uuid2"]
}
```

### UnreadCountResponse

```json
{
  "unread_count": 5
}
```

---

## Notification Types / Tipos de Notificacao

| Type | Description (EN) | Descricao (pt-BR) | Entity Type |
|---|---|---|---|
| `race_scheduled` | A race has been scheduled | Uma corrida foi agendada | `race` |
| `result_published` | Race results have been published | Resultados da corrida foram publicados | `race` |
| `team_invite` | User invited to join a team | Usuario convidado para equipe | `team` |
| `championship_update` | Championship status changed | Status do campeonato alterado | `championship` |
| `general` | General platform notification | Notificacao geral da plataforma | null |

The `type` field uses `native_enum=False` in SQLAlchemy for SQLite test compatibility.

O campo `type` usa `native_enum=False` no SQLAlchemy para compatibilidade com SQLite nos testes.

---

## Service Layer / Camada de Servico

The `app/notifications/service.py` module provides:

O modulo `app/notifications/service.py` fornece:

### CRUD Functions / Funcoes CRUD

| Function | Description (EN) | Descricao (pt-BR) |
|---|---|---|
| `list_notifications()` | List user notifications with optional filters | Lista notificacoes do usuario com filtros opcionais |
| `get_unread_count()` | Count unread notifications (SQL COUNT) | Conta notificacoes nao lidas (SQL COUNT) |
| `get_notification_by_id()` | Get by ID or raise 404 | Busca por ID ou lanca 404 |
| `mark_as_read()` | Mark single as read (validates ownership) | Marca como lida (valida propriedade) |
| `mark_all_as_read()` | Bulk UPDATE all unread for user | UPDATE em massa de todas nao lidas do usuario |
| `delete_notification()` | Delete (validates ownership) | Exclui (valida propriedade) |
| `create_notification()` | Create for single user | Cria para um unico usuario |
| `create_broadcast_notifications()` | Create for multiple users | Cria para multiplos usuarios |

### Helper Functions (for future event-driven use) / Funcoes Auxiliares (para uso futuro baseado em eventos)

| Function | Description (EN) | Descricao (pt-BR) |
|---|---|---|
| `notify_race_scheduled()` | Broadcast race scheduled notification | Envia notificacao de corrida agendada |
| `notify_result_published()` | Broadcast results published notification | Envia notificacao de resultados publicados |
| `notify_team_invite()` | Send team invite notification to single user | Envia notificacao de convite de equipe |

These helpers are not wired to any endpoint yet — they will be used in future episodes when events trigger notifications automatically.

Esses auxiliares nao estao conectados a nenhum endpoint ainda — serao usados em episodios futuros quando eventos dispararem notificacoes automaticamente.

---

## Entity Linking / Vinculacao de Entidade

Notifications can reference platform entities for deep linking:

Notificacoes podem referenciar entidades da plataforma para deep linking:

| `entity_type` | `entity_id` | Frontend Link |
|---|---|---|
| `race` | Race UUID | `/races/{entity_id}` |
| `championship` | Championship UUID | `/championships/{entity_id}` |
| `team` | Team UUID | `/teams/{entity_id}` |
| null | null | No link |

The frontend `NotificationsPage` resolves entity links automatically and displays a "View details" link.

O `NotificationsPage` do frontend resolve links de entidade automaticamente e exibe um link "Ver detalhes".

---

## Error Responses / Respostas de Erro

| Code | Condition (EN) | Condicao (pt-BR) |
|---|---|---|
| `401` | Missing or invalid token | Token ausente ou invalido |
| `403` | Accessing another user's notification | Acessando notificacao de outro usuario |
| `403` | Missing `notifications:create` on POST / | Faltando `notifications:create` no POST / |
| `404` | Notification not found | Notificacao nao encontrada |

---

## Tests / Testes

25 tests in `backend/tests/test_notifications.py`:

25 testes em `backend/tests/test_notifications.py`:

| Test | Description (EN) | Descricao (pt-BR) |
|---|---|---|
| `test_list_notifications_empty` | Empty list when no notifications | Lista vazia sem notificacoes |
| `test_list_notifications_with_data` | Returns notifications | Retorna notificacoes |
| `test_list_notifications_filter_unread` | Filter by is_read=false | Filtro por nao lidas |
| `test_list_notifications_filter_read` | Filter by is_read=true | Filtro por lidas |
| `test_list_notifications_filter_type` | Filter by type | Filtro por tipo |
| `test_list_notifications_only_own` | User sees only own | Usuario ve apenas as proprias |
| `test_unread_count_zero` | Zero when no unread | Zero quando nenhuma nao lida |
| `test_unread_count_with_unread` | Count matches unread | Contagem corresponde a nao lidas |
| `test_unread_count_excludes_read` | Excludes read ones | Exclui as lidas |
| `test_unread_count_excludes_other_users` | Excludes other users | Exclui outros usuarios |
| `test_mark_as_read` | Marks as read | Marca como lida |
| `test_mark_as_read_not_found` | 404 for invalid ID | 404 para ID invalido |
| `test_mark_as_read_other_user_forbidden` | 403 for other user's | 403 para notificacao de outro |
| `test_mark_all_as_read` | Marks all unread | Marca todas nao lidas |
| `test_mark_all_as_read_empty` | Returns 0 when none unread | Retorna 0 quando nenhuma nao lida |
| `test_delete_notification` | Deletes own notification | Exclui propria notificacao |
| `test_delete_notification_not_found` | 404 for invalid ID | 404 para ID invalido |
| `test_delete_other_user_notification_forbidden` | 403 for other user's | 403 para notificacao de outro |
| `test_create_notification_single_user` | Creates for single user | Cria para um usuario |
| `test_create_notification_broadcast` | Broadcasts to multiple users | Envia para multiplos usuarios |
| `test_create_notification_with_entity` | Creates with entity link | Cria com link de entidade |
| `test_create_notification_no_user_ids` | Returns empty list | Retorna lista vazia |
| `test_create_notification_forbidden` | 403 without permission | 403 sem permissao |
| `test_list_notifications_unauthorized` | 401 without token | 401 sem token |
| `test_unread_count_unauthorized` | 401 without token | 401 sem token |
