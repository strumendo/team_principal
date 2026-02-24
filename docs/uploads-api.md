# Uploads API / API de Uploads

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Configuration / Configuracao](#configuration--configuracao)
3. [Storage Architecture / Arquitetura de Armazenamento](#storage-architecture--arquitetura-de-armazenamento)
4. [Permissions / Permissoes](#permissions--permissoes)
5. [Endpoints](#endpoints)
6. [Validation / Validacao](#validation--validacao)
7. [Frontend Component / Componente Frontend](#frontend-component--componente-frontend)
8. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
9. [Tests / Testes](#tests--testes)

---

## Overview / Visao Geral

The uploads module provides file upload endpoints for user avatars, team logos, and driver photos. Files are stored on the local filesystem and served via FastAPI's `StaticFiles` middleware.

O modulo de uploads fornece endpoints de upload de arquivos para avatares de usuarios, logos de equipes e fotos de pilotos. Arquivos sao armazenados no sistema de arquivos local e servidos via middleware `StaticFiles` do FastAPI.

Key design decisions:
- **Local filesystem storage** — files saved to `uploads/{category}/{uuid}.{ext}`
- **Atomic upload + URL update** — each endpoint saves the file and updates the entity URL in a single request
- **Old file cleanup** — re-uploading replaces the previous file automatically
- **UUID filenames** — prevents collisions and path traversal attacks
- **No new dependencies** — uses `python-multipart` (already installed) and built-in FastAPI features

Decisoes de design chave:
- **Armazenamento local** — arquivos salvos em `uploads/{category}/{uuid}.{ext}`
- **Upload + atualizacao atomica** — cada endpoint salva o arquivo e atualiza a URL da entidade em uma unica requisicao
- **Limpeza de arquivo antigo** — re-enviar substitui o arquivo anterior automaticamente
- **Nomes UUID** — previne colisoes e ataques de path traversal
- **Sem novas dependencias** — usa `python-multipart` (ja instalado) e recursos nativos do FastAPI

---

## Configuration / Configuracao

Three settings in `app/config.py`:

Tres configuracoes em `app/config.py`:

| Setting | Default | Description |
|---|---|---|
| `UPLOAD_DIR` | `"uploads"` | Directory for stored files / Diretorio para arquivos armazenados |
| `UPLOAD_MAX_SIZE_BYTES` | `5242880` (5 MB) | Maximum file size / Tamanho maximo do arquivo |
| `UPLOAD_ALLOWED_TYPES` | `["image/jpeg", "image/png", "image/webp"]` | Allowed MIME types / Tipos MIME permitidos |

---

## Storage Architecture / Arquitetura de Armazenamento

```
uploads/                    # Root directory (created on startup)
├── avatars/                # User avatars / Avatares de usuarios
│   └── {uuid}.jpg
├── logos/                  # Team logos / Logos de equipes
│   └── {uuid}.png
└── photos/                 # Driver photos / Fotos de pilotos
    └── {uuid}.webp
```

Files are served at `/uploads/{category}/{filename}` via `StaticFiles` mount. The returned URL path is stored in the entity's URL field (`avatar_url`, `logo_url`, `photo_url`).

Arquivos sao servidos em `/uploads/{category}/{filename}` via mount `StaticFiles`. O caminho URL retornado e armazenado no campo URL da entidade (`avatar_url`, `logo_url`, `photo_url`).

Content-type to extension mapping / Mapeamento de content-type para extensao:

| Content-Type | Extension |
|---|---|
| `image/jpeg` | `.jpg` |
| `image/png` | `.png` |
| `image/webp` | `.webp` |

---

## Permissions / Permissoes

| Endpoint | Permission Required |
|---|---|
| `POST /uploads/users/{id}/avatar` | Own user (any authenticated) OR `users:update` |
| `POST /uploads/teams/{id}/logo` | `teams:update` |
| `POST /uploads/drivers/{id}/photo` | `drivers:update` |

No new permissions are needed — upload endpoints reuse existing entity-level permissions.

Nenhuma permissao nova e necessaria — endpoints de upload reutilizam permissoes existentes das entidades.

---

## Endpoints

### POST `/api/v1/uploads/users/{user_id}/avatar`

Upload a user avatar image.

Envia uma imagem de avatar de usuario.

**Request:** `multipart/form-data` with `file` field

**Response (200):**
```json
{
  "url": "/uploads/avatars/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
}
```

### POST `/api/v1/uploads/teams/{team_id}/logo`

Upload a team logo image.

Envia uma imagem de logo de equipe.

**Request:** `multipart/form-data` with `file` field

**Response (200):**
```json
{
  "url": "/uploads/logos/a1b2c3d4-e5f6-7890-abcd-ef1234567890.png"
}
```

### POST `/api/v1/uploads/drivers/{driver_id}/photo`

Upload a driver photo image.

Envia uma imagem de foto de piloto.

**Request:** `multipart/form-data` with `file` field

**Response (200):**
```json
{
  "url": "/uploads/photos/a1b2c3d4-e5f6-7890-abcd-ef1234567890.webp"
}
```

---

## Validation / Validacao

| Rule | HTTP Status | Detail Message |
|---|---|---|
| Invalid content type | 422 | `Invalid file type: {type}. Allowed: image/jpeg, image/png, image/webp` |
| File too large (> 5 MB) | 422 | `File too large. Maximum size: 5 MB` |
| Entity not found | 404 | `User not found` / `Team not found` / `Driver not found` |
| Missing permission | 403 | `Missing permissions: {codename}` |
| No auth token | 401 | `Not authenticated` |

---

## Frontend Component / Componente Frontend

### `ImageUpload` Component

Reusable component at `frontend/src/components/ImageUpload.tsx`.

Componente reutilizavel em `frontend/src/components/ImageUpload.tsx`.

**Props:**

| Prop | Type | Description |
|---|---|---|
| `currentImageUrl` | `string \| null` | Current image URL from entity / URL da imagem atual da entidade |
| `uploadUrl` | `string` | API endpoint path (e.g., `/uploads/users/{id}/avatar`) |
| `token` | `string` | Auth token / Token de autenticacao |
| `onUploadSuccess` | `(url: string) => void` | Callback on successful upload / Callback apos upload bem-sucedido |
| `label` | `string` | Display label / Rotulo de exibicao |

**Features:**
- File selection with preview (blob URL) / Selecao de arquivo com preview
- Client-side validation (type + size) / Validacao no cliente
- Loading state during upload / Estado de carregamento durante upload
- Error display / Exibicao de erros

### API Client / Cliente API

`uploadsApi` in `frontend/src/lib/api-client.ts`:

| Method | Description |
|---|---|
| `uploadUserAvatar(token, userId, file)` | Upload user avatar / Enviar avatar de usuario |
| `uploadTeamLogo(token, teamId, file)` | Upload team logo / Enviar logo de equipe |
| `uploadDriverPhoto(token, driverId, file)` | Upload driver photo / Enviar foto de piloto |

---

## Error Responses / Respostas de Erro

All errors follow the standard FastAPI format:

Todos os erros seguem o formato padrao do FastAPI:

```json
{
  "detail": "Error message here"
}
```

| Code | Scenario |
|---|---|
| 401 | Missing or invalid auth token / Token ausente ou invalido |
| 403 | Insufficient permissions / Permissoes insuficientes |
| 404 | Entity (user/team/driver) not found / Entidade nao encontrada |
| 422 | Invalid file type or file too large / Tipo invalido ou arquivo muito grande |

---

## Tests / Testes

14 tests in `backend/tests/test_uploads.py`:

14 testes em `backend/tests/test_uploads.py`:

| Test | Category |
|---|---|
| `test_upload_user_avatar_own` | Upload own avatar (any auth user) |
| `test_upload_user_avatar_admin` | Upload another user's avatar (users:update) |
| `test_upload_user_avatar_forbidden` | Upload another user's avatar without permission -> 403 |
| `test_upload_user_avatar_not_found` | Upload for non-existent user -> 404 |
| `test_upload_user_avatar_replaces_old` | Re-upload replaces old file and URL |
| `test_upload_team_logo` | Upload team logo (teams:update) |
| `test_upload_team_logo_forbidden` | Upload without teams:update -> 403 |
| `test_upload_team_logo_not_found` | Non-existent team -> 404 |
| `test_upload_driver_photo` | Upload driver photo (drivers:update) |
| `test_upload_driver_photo_forbidden` | Upload without drivers:update -> 403 |
| `test_upload_driver_photo_not_found` | Non-existent driver -> 404 |
| `test_upload_invalid_content_type` | Upload .txt file -> 422 |
| `test_upload_file_too_large` | Upload > max size -> 422 |
| `test_upload_unauthorized` | No auth token -> 401 |
