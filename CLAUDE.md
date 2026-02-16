# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TeamPrincipal** is an E-Sports Racing Management Platform built with FastAPI (Python) + Next.js (React) + PostgreSQL. Licensed under MIT.

## Tech Stack

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + Alembic
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS + NextAuth.js v5
- **Database:** PostgreSQL 16 (asyncpg for async, psycopg2 for Alembic)
- **Auth:** JWT (python-jose + passlib[bcrypt]) on backend, NextAuth.js on frontend
- **Tooling:** Ruff (lint+format), mypy, pytest, ESLint, Prettier

## Project Structure

```
team_principal/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # App factory
│   │   ├── config.py     # Pydantic Settings
│   │   ├── db/           # Database (base, session, seed)
│   │   ├── core/         # Security, dependencies, exceptions
│   │   ├── auth/         # Auth module (login, register, refresh)
│   │   ├── users/        # Users module (CRUD)
│   │   ├── roles/        # Roles module (RBAC)
│   │   └── health/       # Health check endpoints
│   ├── tests/            # pytest tests
│   ├── alembic/          # DB migrations
│   └── pyproject.toml    # Poetry config
├── frontend/             # Next.js application
│   ├── src/
│   │   ├── app/          # App Router (route groups)
│   │   ├── components/   # UI components
│   │   ├── lib/          # Utilities (auth, api-client)
│   │   └── middleware.ts  # Route protection
│   └── package.json
├── docs/                 # Documentation (bilingual EN + pt-BR)
├── docker-compose.yml
└── .env.example
```

## Common Commands

### Backend
```bash
cd backend
poetry install                        # Install dependencies
poetry run uvicorn app.main:app --reload  # Dev server (port 8000)
poetry run alembic upgrade head       # Run migrations
poetry run python -m app.db.seed      # Seed database
poetry run pytest                     # Run tests
poetry run ruff check app/            # Lint
poetry run ruff format app/           # Format
poetry run mypy app/                  # Type check
```

### Frontend
```bash
cd frontend
npm install                           # Install dependencies
npm run dev                           # Dev server (port 3000)
npm run build                         # Production build
npm run lint                          # Lint
```

### Docker
```bash
docker-compose up -d                  # Start all services
docker-compose down                   # Stop all services
```

## Development Environment

- IDE: PyCharm (JetBrains)
- API docs available at http://localhost:8000/docs when backend is running

## Conventions

- **API versioning:** All endpoints prefixed with `/api/v1/`
- **Primary keys:** UUID (gen_random_uuid())
- **Database naming:** snake_case with SQLAlchemy naming conventions
- **Conventional commits:** enforced via pre-commit hook

## Workflow Rules

### Conversation Management
- Break long chats into smaller, focused sessions when context grows too large.
- Auto-compact long chats to keep conversations efficient and within context limits.

### Git & Commits
- All commits must use the author: `Bruno Strumendo <strumendo@gmail.com>`.
- Commit messages must follow conventional commits style (feat:, fix:, docs:, chore:, etc.).

### Documentation
- Always create or update documentation after implementing any feature or significant change.
- All documentation and code comments must be bilingual: **English and Portuguese (pt-BR)**.

### Task Management
- Always create tasks (TODO items, issues, or task list entries) related to the project when planning or implementing work.

### Pull Requests
- Create pull requests organized by phase, task, or feature — never mix unrelated changes in a single PR.
- Always observe and respect dependencies between developments: if a feature depends on another, ensure the dependent PR is merged first or reference it as a dependency.
- Keep PRs focused and reviewable — smaller, well-scoped PRs are preferred over large, monolithic ones.
- Branch naming: `ep{XX}/{feature-name}` for epic branches.
