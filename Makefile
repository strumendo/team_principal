# TeamPrincipal — Makefile
# Comandos comuns para desenvolvimento e deploy
# Common commands for development and deployment

.PHONY: help dev dev-build dev-down test test-backend test-frontend lint lint-backend lint-frontend format typecheck build prod prod-down clean db-migrate db-seed

# Default target / Alvo padrao
help: ## Show this help / Exibir esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================
# Development / Desenvolvimento
# ============================================================

dev: ## Start dev environment / Iniciar ambiente de desenvolvimento
	docker-compose up -d

dev-build: ## Rebuild and start dev / Reconstruir e iniciar dev
	docker-compose up -d --build

dev-down: ## Stop dev environment / Parar ambiente de desenvolvimento
	docker-compose down

dev-logs: ## Show dev logs / Exibir logs de desenvolvimento
	docker-compose logs -f

# ============================================================
# Testing / Testes
# ============================================================

test: test-backend test-frontend ## Run all tests / Executar todos os testes

test-backend: ## Run backend tests / Executar testes do backend
	cd backend && poetry run pytest

test-frontend: ## Run frontend tests / Executar testes do frontend
	cd frontend && npm run test:ci

# ============================================================
# Linting & Formatting / Linting e Formatacao
# ============================================================

lint: lint-backend lint-frontend ## Run all linters / Executar todos os linters

lint-backend: ## Lint backend / Lint do backend
	cd backend && poetry run ruff check app/

lint-frontend: ## Lint frontend / Lint do frontend
	cd frontend && npm run lint

format: ## Format backend code / Formatar codigo do backend
	cd backend && poetry run ruff format app/

typecheck: ## Type check all / Verificar tipos de tudo
	cd backend && poetry run mypy app/
	cd frontend && npx tsc --noEmit

# ============================================================
# Database / Banco de Dados
# ============================================================

db-migrate: ## Run database migrations / Executar migracoes do banco
	cd backend && poetry run alembic upgrade head

db-seed: ## Seed database / Popular banco com dados iniciais
	cd backend && poetry run python -m app.db.seed

# ============================================================
# Production / Producao
# ============================================================

prod: ## Start production environment / Iniciar ambiente de producao
	docker-compose -f docker-compose.prod.yml up -d

prod-build: ## Build and start production / Construir e iniciar producao
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down: ## Stop production environment / Parar ambiente de producao
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Show production logs / Exibir logs de producao
	docker-compose -f docker-compose.prod.yml logs -f

# ============================================================
# Build / Construcao
# ============================================================

build: ## Build Docker images / Construir imagens Docker
	docker-compose build

build-prod: ## Build production images / Construir imagens de producao
	docker-compose -f docker-compose.prod.yml build

# ============================================================
# Cleanup / Limpeza
# ============================================================

clean: ## Remove containers, volumes / Remover containers e volumes
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
