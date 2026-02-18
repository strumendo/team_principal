# Troubleshooting & Error Registry / Solucao de Problemas & Registro de Erros

This document catalogs all errors encountered during development, their root causes, and resolutions. It serves as a reference for future debugging.

Este documento cataloga todos os erros encontrados durante o desenvolvimento, suas causas raiz e resolucoes. Serve como referencia para depuracao futura.

---

## Table of Contents / Indice

1. [Ruff Lint Errors (60 errors)](#1-ruff-lint-errors-60-errors)
2. [Mypy Type-Checking Errors (10 errors)](#2-mypy-type-checking-errors-10-errors)
3. [Stale ORM Relationship Cache](#3-stale-orm-relationship-cache)
4. [PR Merge Chain Issues](#4-pr-merge-chain-issues)
5. [bcrypt + passlib Incompatibility](#5-bcrypt--passlib-incompatibility)
6. [SQLAlchemy UUID Dialect Incompatibility](#6-sqlalchemy-uuid-dialect-incompatibility)
7. [user_roles Dual Foreign Key Ambiguity](#7-user_roles-dual-foreign-key-ambiguity)

---

## 1. Ruff Lint Errors (60 errors)

**When / Quando:** EP02 PR CI pipeline
**Total:** 60 errors across 6 rule categories

### 1.1. B008 — Function call in default argument (53 errors)

**Error message / Mensagem de erro:**
```
B008 Do not perform function calls in argument defaults; instead, perform the call within the function, or read the default from a module-level singleton variable
```

**Root cause / Causa raiz:**
FastAPI's dependency injection pattern uses `Depends()` as default parameter values — e.g., `db: AsyncSession = Depends(get_db)`. This is a fundamental FastAPI idiom, NOT a bug.

O padrao de injecao de dependencia do FastAPI usa `Depends()` como valores padrao de parametro. Isso e um idioma fundamental do FastAPI, NAO um bug.

**Affected files / Arquivos afetados:**
- `app/auth/router.py` (all endpoints)
- `app/users/router.py` (all endpoints)
- `app/roles/router.py` (all endpoints)
- `app/core/dependencies.py` (dependency functions)
- `app/health/router.py`

**Resolution / Resolucao:**
Added `B008` to the global ruff ignore list in `pyproject.toml`:
```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM"]
ignore = ["B008"]
```

**File:** `backend/pyproject.toml`

---

### 1.2. N802 — Function name should be lowercase (2 errors)

**Error message / Mensagem de erro:**
```
N802 Function name `DATABASE_URL` should be lowercase
N802 Function name `SYNC_DATABASE_URL` should be lowercase
```

**Root cause / Causa raiz:**
Pydantic Settings uses `@property` methods with UPPER_CASE names to compute database URLs from individual components. This follows the convention for settings/environment variables.

Pydantic Settings usa metodos `@property` com nomes em UPPER_CASE para computar URLs de banco de dados. Isso segue a convencao para configuracoes/variaveis de ambiente.

**Affected file / Arquivo afetado:** `app/config.py`

**Resolution / Resolucao:**
Added per-file ignore in `pyproject.toml`:
```toml
[tool.ruff.lint.per-file-ignores]
"app/config.py" = ["N802"]
```

---

### 1.3. B904 — Exception chaining with `raise ... from` (2 errors)

**Error message / Mensagem de erro:**
```
B904 Within an `except` clause, raise exceptions with `raise ... from err`
```

**Root cause / Causa raiz:**
When catching `ValueError` and re-raising a different exception, Python best practice requires explicit exception chaining with `from` to preserve the original traceback.

Ao capturar `ValueError` e re-lancar uma excecao diferente, a pratica recomendada do Python requer encadeamento explicito com `from` para preservar o traceback original.

**Affected files / Arquivos afetados:**
- `app/auth/service.py:85` — `raise CredentialsException("Invalid refresh token")` inside `except ValueError`
- `app/core/dependencies.py:44` — `raise CredentialsException()` inside `except ValueError`

**Resolution / Resolucao:**
Changed to explicit exception chaining:
```python
# Before / Antes:
except ValueError:
    raise CredentialsException("Invalid refresh token")

# After / Depois:
except ValueError as err:
    raise CredentialsException("Invalid refresh token") from err
```

---

### 1.4. UP017 — Replace `timezone.utc` with `UTC` (2 errors)

**Error message / Mensagem de erro:**
```
UP017 Use `datetime.UTC` alias
```

**Root cause / Causa raiz:**
Python 3.11+ provides `datetime.UTC` as a shorter alias for `datetime.timezone.utc`. Ruff's UP017 rule enforces the modern form.

Python 3.11+ fornece `datetime.UTC` como alias mais curto para `datetime.timezone.utc`. A regra UP017 do Ruff impoe a forma moderna.

**Affected file / Arquivo afetado:** `app/core/security.py`

**Resolution / Resolucao:**
```python
# Before / Antes:
from datetime import datetime, timedelta, timezone
datetime.now(timezone.utc)

# After / Depois:
from datetime import UTC, datetime, timedelta
datetime.now(UTC)
```

---

### 1.5. E501 — Line too long (1 error)

**Error message / Mensagem de erro:**
```
E501 Line too long (121 > 120)
```

**Affected file / Arquivo afetado:** `app/users/service.py`

**Resolution / Resolucao:**
Broke the long function signature across multiple lines:
```python
# Before / Antes:
async def update_user(db: AsyncSession, user: User, full_name: str | None = None, avatar_url: str | None = None) -> User:

# After / Depois:
async def update_user(
    db: AsyncSession, user: User, full_name: str | None = None, avatar_url: str | None = None
) -> User:
```

---

### 1.6. I001 — Import sorting (auto-fixed)

**Error message / Mensagem de erro:**
```
I001 Import block is un-sorted or un-formatted
```

**Affected files / Arquivos afetados:** `app/main.py`, `app/roles/router.py`

**Resolution / Resolucao:**
Auto-fixed with `ruff check --fix`. Ruff reorders imports according to isort-compatible sections (stdlib → third-party → first-party).

---

## 2. Mypy Type-Checking Errors (10 errors)

**When / Quando:** EP02 PR CI pipeline
**Config:** `mypy --strict` with `pydantic.mypy` plugin, `--ignore-missing-imports`

### 2.1. no-any-return — jwt.encode returns `Any` (2 errors)

**Error message / Mensagem de erro:**
```
app/core/security.py:38: error: Returning Any from function declared to return "str" [no-any-return]
app/core/security.py:49: error: Returning Any from function declared to return "str" [no-any-return]
```

**Root cause / Causa raiz:**
`python-jose`'s `jwt.encode()` is typed as returning `Any` in its stubs. Returning it directly from a function declared `-> str` triggers mypy's `no-any-return` in strict mode.

O `jwt.encode()` do `python-jose` e tipado como retornando `Any` em seus stubs. Retorna-lo diretamente de uma funcao declarada `-> str` dispara o `no-any-return` do mypy em modo strict.

**Resolution / Resolucao:**
Used a typed intermediate variable to narrow the type:
```python
# Before / Antes:
return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# After / Depois:
encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
return encoded
```

**File:** `app/core/security.py` (lines 38, 50)

---

### 2.2. no-any-return — jwt.decode returns `Any` (1 error)

**Error message / Mensagem de erro:**
```
app/core/security.py:58: error: Returning Any from function declared to return "dict[str, object] | None" [no-any-return]
```

**Root cause / Causa raiz:**
Same issue as 2.1 but for `jwt.decode()`. The function returns `Any` per python-jose stubs.

**Resolution / Resolucao:**
Used a typed intermediate variable:
```python
# Before / Antes:
return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

# After / Depois:
payload: dict[str, object] = jwt.decode(
    token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
)
return payload
```

**File:** `app/core/security.py` (line 60)

---

### 2.3. type-arg — Bare `dict` without type arguments (1 error)

**Error message / Mensagem de erro:**
```
app/core/security.py:52: error: Missing type parameters for generic type "dict" [type-arg]
```

**Root cause / Causa raiz:**
`decode_token` was declared as `-> dict | None` without type parameters. In mypy strict mode, generic types must be fully parameterized.

`decode_token` estava declarado como `-> dict | None` sem parametros de tipo. Em modo strict, tipos genericos devem ser completamente parametrizados.

**Resolution / Resolucao:**
```python
# Before / Antes:
def decode_token(token: str) -> dict | None:

# After / Depois:
def decode_token(token: str) -> dict[str, object] | None:
```

**File:** `app/core/security.py` (line 54)

---

### 2.4. type-arg — Bare `list` return types in router (5 errors)

**Error message / Mensagem de erro:**
```
app/roles/router.py:53: error: Missing type parameters for generic type "list" [type-arg]
app/roles/router.py:96: error: Missing type parameters for generic type "list" [type-arg]
app/roles/router.py:200: error: Missing type parameters for generic type "list" [type-arg]
app/roles/router.py:214: error: Missing type parameters for generic type "list" [type-arg]
app/roles/router.py:229: error: Missing type parameters for generic type "list" [type-arg]
```

**Root cause / Causa raiz:**
Endpoint functions that return lists were annotated as `-> list:` without type parameters. In mypy strict mode, all generic types require explicit type arguments.

Funcoes de endpoint que retornam listas estavam anotadas como `-> list:` sem parametros de tipo.

**Resolution / Resolucao:**
Added ORM model imports and parameterized return types:
```python
from app.roles.models import Permission, Role

# Permissions endpoint:
) -> list[Permission]:

# Roles endpoints:
) -> list[Role]:
```

**File:** `app/roles/router.py` (lines 54, 97, 201, 215, 230)

---

### 2.5. assignment — Incompatible types from payload.get() (1 error)

**Error message / Mensagem de erro:**
```
app/core/dependencies.py:39: error: Incompatible types in assignment (expression has type "object", variable has type "str | None") [assignment]
```

**Root cause / Causa raiz:**
After changing `decode_token` return type to `dict[str, object] | None`, the `.get("sub")` call returns `object` instead of `str | None`. The variable was annotated as `str | None` which is incompatible.

Apos mudar o tipo de retorno de `decode_token` para `dict[str, object] | None`, `.get("sub")` retorna `object` ao inves de `str | None`.

**Resolution / Resolucao:**
Used `isinstance` type narrowing instead of explicit type annotation:
```python
# Before / Antes:
user_id_str: str | None = payload.get("sub")
if user_id_str is None:
    raise CredentialsException()
user_id = uuid.UUID(user_id_str)

# After / Depois:
raw_sub = payload.get("sub")
if not isinstance(raw_sub, str):
    raise CredentialsException()
user_id = uuid.UUID(raw_sub)
```

**Files:** `app/core/dependencies.py` (line 39), `app/auth/service.py` (line 80)

---

### 2.6. arg-type — Type inference confusion from variable reuse (1 error)

**Error message / Mensagem de erro:**
```
app/roles/service.py:178: error: Argument 1 to "list" has incompatible type ... [arg-type]
```

**Root cause / Causa raiz:**
The `list_user_roles` function reused the same `result` variable for two different queries:
1. `select(User).where(...)` — result typed as `Result[Tuple[User]]`
2. `select(Role).join(...)` — result typed as `Result[Tuple[Role]]`

Mypy carries the first type annotation forward and fails to properly re-narrow the variable after reassignment, causing a type mismatch on `result.scalars().all()`.

A funcao `list_user_roles` reutilizava a variavel `result` para duas queries diferentes. O mypy carrega a primeira anotacao de tipo e falha em re-estreitar a variavel apos a reatribuicao.

**Resolution / Resolucao:**
Renamed variables to disambiguate:
```python
# Before / Antes:
result = await db.execute(select(User).where(User.id == user_id))
if result.scalar_one_or_none() is None:
    raise NotFoundException("User not found")
result = await db.execute(select(Role).join(...))
return list(result.scalars().all())

# After / Depois:
user_result = await db.execute(select(User).where(User.id == user_id))
if user_result.scalar_one_or_none() is None:
    raise NotFoundException("User not found")
roles_result = await db.execute(select(Role).join(...))
return list(roles_result.scalars().all())
```

**File:** `app/roles/service.py` (lines 170-178)

---

## 3. Stale ORM Relationship Cache

**When / Quando:** EP02 PR4 — `test_assign_role_to_user` failure
**Symptom / Sintoma:** After assigning a role via direct SQL INSERT on `user_roles`, the `list_user_roles` function returned an empty list.

### Root Cause / Causa Raiz

The `assign_role_to_user` function uses a direct `insert(user_roles).values(...)` statement to set the `assigned_by` column (which the ORM relationship doesn't support). However, after this INSERT, the SQLAlchemy ORM relationship `user.roles` still holds the stale, cached version (empty list) from when the user was initially loaded.

A funcao `assign_role_to_user` usa `insert(user_roles).values(...)` direto para setar a coluna `assigned_by`. Porem, apos esse INSERT, o relacionamento ORM `user.roles` ainda mantem a versao em cache (lista vazia) de quando o usuario foi carregado inicialmente.

### Why It Happens / Por Que Acontece

SQLAlchemy's `lazy="selectin"` loads relationships when the parent object is first queried. If you modify the association table directly (bypassing the ORM relationship), the ORM doesn't know the data changed. Even `db.refresh(user)` may not help if the session identity map still holds the stale relationship.

O `lazy="selectin"` do SQLAlchemy carrega relacionamentos quando o objeto pai e consultado pela primeira vez. Se voce modifica a tabela associativa diretamente (ignorando o relacionamento ORM), o ORM nao sabe que os dados mudaram.

### Resolution / Resolucao

Changed `list_user_roles` to use an explicit JOIN query instead of the ORM relationship:

```python
# Before / Antes (broken):
user = await get_user_by_id(db, user_id)
return list(user.roles)

# After / Depois (working):
roles_result = await db.execute(
    select(Role)
    .join(user_roles, Role.id == user_roles.c.role_id)
    .where(user_roles.c.user_id == user_id)
)
return list(roles_result.scalars().all())
```

**File:** `app/roles/service.py:164-178`

### Lesson Learned / Licao Aprendida

When using direct SQL (INSERT/DELETE) on association tables, never rely on ORM relationships for subsequent reads in the same session. Use explicit JOIN queries instead.

Ao usar SQL direto (INSERT/DELETE) em tabelas associativas, nunca confie em relacionamentos ORM para leituras subsequentes na mesma sessao. Use queries JOIN explicitas.

---

## 4. PR Merge Chain Issues

**When / Quando:** EP02 PR merging sequence (PRs #13-#19)

### Scenario / Cenario

The RBAC implementation was split into 4 sequential PRs with branch dependencies:
```
PR1 (ep02/rbac-permissions-crud) → PR2 (ep02/rbac-roles-crud) → PR3 (ep02/rbac-dependencies) → PR4 (ep02/rbac-user-roles)
```

Each PR targeted its predecessor's branch as the base (e.g., PR2 targeted `ep02/rbac-permissions-crud`). When PR1 was merged and its branch deleted, the downstream PRs became unmergeable because their base branch no longer existed.

Cada PR tinha a branch do predecessor como base. Quando o PR1 foi mergeado e sua branch deletada, os PRs subsequentes ficaram imergeaveis porque a branch base nao existia mais.

### Symptoms / Sintomas

- PRs showed "MERGED" state but content wasn't actually in `main`
- PRs were auto-closed when base branches were deleted
- Merge attempts failed with conflicts

### Resolution / Resolucao

For each subsequent PR:
1. Rebased the branch onto `origin/main`
2. Force-pushed the rebased branch
3. Created a replacement PR targeting `main`

```bash
git checkout ep02/rbac-roles-crud
git rebase origin/main
git push --force-with-lease origin ep02/rbac-roles-crud
gh pr create --title "..." --base main
```

### Result / Resultado

| Original PR | Replacement PR | Status |
|---|---|---|
| #13 | — | Merged (first in chain) |
| #14 | #17 | Merged |
| #15 | #18 | Merged |
| #16 | #19 | Open (final PR) |

### Lesson Learned / Licao Aprendida

When using sequential PR chains, always target `main` as the base branch. Use GitHub's "stacked PRs" workflow or merge each PR before creating the next one. Avoid targeting non-default branches as PR bases.

Ao usar cadeias sequenciais de PRs, sempre use `main` como branch base. Use o workflow de "PRs empilhados" do GitHub ou merge cada PR antes de criar o proximo.

---

## 5. bcrypt + passlib Incompatibility

**When / Quando:** EP01 — Initial auth setup

### Symptom / Sintoma

`passlib[bcrypt]` fails with runtime errors when used with `bcrypt >= 4.1`:
```
(trapped) error reading bcrypt version
```

### Root Cause / Causa Raiz

`passlib` hasn't been updated to support `bcrypt >= 4.x`. The internal API it relies on was removed in newer bcrypt versions.

`passlib` nao foi atualizado para suportar `bcrypt >= 4.x`. A API interna que ele utiliza foi removida nas versoes mais novas do bcrypt.

### Resolution / Resolucao

Use `bcrypt` directly instead of `passlib`:

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
```

**File:** `app/core/security.py`

---

## 6. SQLAlchemy UUID Dialect Incompatibility

**When / Quando:** EP01 — Test setup with SQLite

### Symptom / Sintoma

Tests using in-memory SQLite fail with:
```
sqlalchemy.exc.CompileError: (in table 'users', column 'id'): Compiler <...> can't render element of type UUID
```

### Root Cause / Causa Raiz

`sqlalchemy.dialects.postgresql.UUID` is PostgreSQL-specific and cannot be used with SQLite. Since tests use in-memory SQLite (`sqlite+aiosqlite://`), dialect-specific types break.

`sqlalchemy.dialects.postgresql.UUID` e especifico do PostgreSQL e nao pode ser usado com SQLite.

### Resolution / Resolucao

Use the generic `sqlalchemy.Uuid` type (added in SQLAlchemy 2.0) which works across all dialects:

```python
# Before / Antes:
from sqlalchemy.dialects.postgresql import UUID
id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ...)

# After / Depois:
from sqlalchemy import Uuid
id: Mapped[uuid.UUID] = mapped_column(Uuid, ...)
```

**Files:** All model files (`app/users/models.py`, `app/roles/models.py`)

---

## 7. user_roles Dual Foreign Key Ambiguity

**When / Quando:** EP01 — Defining Role↔User relationship

### Symptom / Sintoma

SQLAlchemy raises:
```
sqlalchemy.exc.AmbiguousForeignKeysError: Could not determine join condition between parent/child tables
```

### Root Cause / Causa Raiz

The `user_roles` table has TWO foreign keys pointing to `users`:
1. `user_id` — the user who holds the role
2. `assigned_by` — the user who assigned the role

SQLAlchemy cannot automatically determine which FK to use for the `Role.users` relationship.

A tabela `user_roles` tem DUAS foreign keys apontando para `users`: `user_id` (o usuario que possui o papel) e `assigned_by` (o usuario que atribuiu o papel). O SQLAlchemy nao consegue determinar automaticamente qual FK usar.

### Resolution / Resolucao

Use explicit `primaryjoin`/`secondaryjoin` on the relationship:

```python
class Role(Base):
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles,
        primaryjoin="Role.id == user_roles.c.role_id",
        secondaryjoin="User.id == user_roles.c.user_id",
        back_populates="roles",
        lazy="selectin",
    )
```

**File:** `app/roles/models.py` (lines 55-62)

---

## Quick Reference / Referencia Rapida

### Ruff Configuration / Configuracao do Ruff

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM"]
ignore = ["B008"]  # FastAPI Depends() pattern

[tool.ruff.lint.per-file-ignores]
"app/config.py" = ["N802"]  # Pydantic Settings property names
```

### Verification Commands / Comandos de Verificacao

```bash
cd backend
poetry run ruff check app/          # Lint — should be 0 errors
poetry run ruff format app/         # Format
poetry run mypy app/ --ignore-missing-imports  # Type check — should be 0 errors
poetry run pytest -v                # Tests — all should pass
```
