# DevOps Improvements / Melhorias de DevOps

## Overview / Visão Geral

This document describes the DevOps improvements made to the TeamPrincipal project, covering Docker optimization, production configuration, dependency management, and build automation.

Este documento descreve as melhorias de DevOps feitas no projeto TeamPrincipal, cobrindo otimização Docker, configuração de produção, gerenciamento de dependências e automação de build.

---

## Docker Optimization / Otimização Docker

### Backend Dockerfile

The backend Dockerfile was restructured into a multi-stage build with three stages:

O Dockerfile do backend foi reestruturado em um build multi-stage com três estágios:

1. **deps** — Installs Poetry and copies dependency files (shared base)
2. **dev** — Full dependencies + hot reload with `--reload`
3. **prod** — Main dependencies only, non-root user (`appuser`), health check, 4 workers

Key improvements / Melhorias principais:
- **Separate deps stage**: Caches `poetry install` independently from code changes
- **Non-root user**: `appuser:appgroup` (UID/GID 1001) for security
- **HEALTHCHECK directive**: Automatic container health monitoring via `/api/v1/health`
- **Production-only deps**: `--only main` excludes dev/test packages

### Frontend Dockerfile

The frontend Dockerfile was optimized similarly:

O Dockerfile do frontend foi otimizado de forma similar:

1. **deps** — Installs npm dependencies (shared base)
2. **dev** — Development server with hot reload
3. **builder** — Production build with `NEXT_PUBLIC_API_URL` build arg
4. **prod** — Standalone Next.js output, non-root user (`nextjs`), health check

Key improvements / Melhorias principais:
- **Separate deps stage**: Caches `npm ci` independently from code changes
- **Build args**: `NEXT_PUBLIC_API_URL` injected at build time
- **Standalone output**: Minimal production image using Next.js standalone mode
- **HEALTHCHECK directive**: Uses `wget` to check `/` endpoint

### .dockerignore Files

Both backend and frontend have `.dockerignore` files to exclude unnecessary files from Docker context:

Ambos backend e frontend possuem arquivos `.dockerignore` para excluir arquivos desnecessários do contexto Docker:

- Test files, coverage reports, IDE configs
- Git files, documentation, environment files
- Build artifacts (`__pycache__`, `node_modules`, `.next`)

---

## Production Docker Compose / Docker Compose de Produção

`docker-compose.prod.yml` provides a production-ready configuration:

`docker-compose.prod.yml` oferece uma configuração pronta para produção:

### Services / Serviços

| Service | Image | Network | Exposed |
|---------|-------|---------|---------|
| db | postgres:16-alpine | internal | No (internal only) |
| backend | Custom (prod target) | internal + web | 8000 (internal) |
| frontend | Custom (prod target) | web | 3000 (internal) |

### Security Features / Recursos de Segurança
- **Required env vars**: `POSTGRES_PASSWORD`, `SECRET_KEY`, `NEXTAUTH_SECRET` (fail-fast)
- **Network isolation**: Database only accessible on `internal` network
- **No port exposure**: Services use `expose` (internal only), reverse proxy handles external traffic
- **Health checks**: All services have health checks with dependency ordering

### Usage / Uso

```bash
# Set required environment variables
# Defina as variáveis de ambiente obrigatórias
export POSTGRES_PASSWORD=your-secure-password
export SECRET_KEY=your-secret-key
export NEXTAUTH_SECRET=your-nextauth-secret

# Start production
# Iniciar produção
make prod-build
```

---

## Dependency Management / Gerenciamento de Dependências

### Dependabot

`.github/dependabot.yml` configures automated dependency updates:

`.github/dependabot.yml` configura atualizações automáticas de dependências:

| Ecosystem | Directory | Schedule | Labels |
|-----------|-----------|----------|--------|
| pip (Python) | /backend | Weekly (Monday) | dependencies, backend |
| npm (Node.js) | /frontend | Weekly (Monday) | dependencies, frontend |
| github-actions | / | Weekly (Monday) | dependencies, ci |

All PRs use conventional commit prefix: `chore(deps):` or `chore(ci):`

Todos os PRs usam prefixo de commit convencional: `chore(deps):` ou `chore(ci):`

---

## Makefile / Automação com Makefile

The `Makefile` provides common commands for development and deployment:

O `Makefile` oferece comandos comuns para desenvolvimento e deploy:

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make dev` | Start dev environment |
| `make dev-build` | Rebuild and start dev |
| `make dev-down` | Stop dev environment |
| `make dev-logs` | Show dev logs |
| `make test` | Run all tests (backend + frontend) |
| `make test-backend` | Run backend tests only |
| `make test-frontend` | Run frontend tests only |
| `make lint` | Run all linters |
| `make format` | Format backend code |
| `make typecheck` | Type check all code |
| `make db-migrate` | Run database migrations |
| `make db-seed` | Seed database |
| `make prod` | Start production environment |
| `make prod-build` | Build and start production |
| `make prod-down` | Stop production |
| `make build` | Build Docker images |
| `make clean` | Remove containers and volumes |

---

## Files Changed / Arquivos Alterados

| File | Action | Description |
|------|--------|-------------|
| `backend/Dockerfile` | Modified | Multi-stage optimization, non-root user, healthcheck |
| `frontend/Dockerfile` | Modified | Deps stage, build args, healthcheck |
| `backend/.dockerignore` | Created | Exclude test/dev files from Docker context |
| `frontend/.dockerignore` | Updated | Exclude test/dev files from Docker context |
| `docker-compose.prod.yml` | Created | Production compose with security features |
| `.github/dependabot.yml` | Created | Automated dependency updates |
| `Makefile` | Created | Common development and deployment commands |
