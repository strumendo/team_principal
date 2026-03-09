# Quality Pass — Test Coverage & CI Improvements
# Melhoria de Qualidade — Cobertura de Testes & CI

## Summary / Resumo

This quality pass addresses the critical gap in frontend test coverage and improves the overall test infrastructure.

Este passo de qualidade endereça a lacuna crítica na cobertura de testes do frontend e melhora a infraestrutura geral de testes.

## Changes / Alterações

### Frontend Tests / Testes Frontend (64 tests in 13 suites)

**Component Tests / Testes de Componentes:**
- `PitStopTable` — Table rendering, compound badges, empty state, delete action (6 tests)
- `PitStopForm` — Form fields, driver options, submission, saving state (5 tests)
- `StrategyCard` — Strategy display, active/inactive badge, action buttons (7 tests)
- `LapTimeTable` — Lap times, sector formatting, PB badge, invalid laps (7 tests)
- `ImageUpload` — File validation, preview, upload endpoint, error handling (7 tests)
- `RaceSummary` — Stats cards, fastest lap details, null handling (4 tests)
- `StintTable` — Stint data, compound badges, degradation, empty state (4 tests)
- `RaceTimeline` — Event markers, legend, empty state (4 tests)

**Page Tests / Testes de Páginas:**
- `LoginPage` — Form rendering, signIn call, redirect, error handling (5 tests)
- `RegisterPage` — Form rendering, API call + auto-login, error states (5 tests)
- `DashboardPage` — Loading state, API call with auth token (2 tests)

**Library Tests / Testes de Bibliotecas:**
- `api-client` — Headers, success/error responses, network errors, auth endpoints (5 tests)
- `home` — Existing landing page tests (3 tests)

### Backend Coverage / Cobertura Backend
- Added `pytest-cov` dependency for test coverage reporting
- Configured coverage in `pyproject.toml`: HTML + terminal output, 74% coverage
- Excluded seed data and app entry point from coverage metrics

### CI Pipeline / Pipeline CI
- Added frontend test step (`npm run test:ci`) to CI workflow
- Tests now run between lint/type-check and build steps

### .gitignore Updates / Atualizações .gitignore
- Added `coverage/` directory (Jest output)
- Added `*.tsbuildinfo` (TypeScript incremental build)

## Test Results / Resultados dos Testes

**Frontend:** 13 suites, 64 tests — all passing
**Backend:** 411 tests — all passing, 74% code coverage
