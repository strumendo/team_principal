# TeamPrincipal

**E-Sports Racing Management Platform**
**Plataforma de Gerenciamento de E-Sports Racing**

---

## Overview / Visao Geral

TeamPrincipal is a web platform for managing e-sports racing teams, providing tools for team organization, performance tracking, and communication.

TeamPrincipal e uma plataforma web para gerenciamento de equipes de e-sports racing, fornecendo ferramentas para organizacao de equipes, acompanhamento de desempenho e comunicacao.

## Tech Stack / Stack Tecnologica

| Layer / Camada | Technology / Tecnologia |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Frontend | Next.js 14 (React) + TypeScript |
| Database / Banco de Dados | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| Auth / Autenticacao | JWT (backend) + NextAuth.js v5 (frontend) |
| CSS | Tailwind CSS |
| Infrastructure / Infraestrutura | Docker + AWS (ECS/EC2 + S3) |

## Project Structure / Estrutura do Projeto

```
team_principal/
├── backend/          # FastAPI application / Aplicacao FastAPI
├── frontend/         # Next.js application / Aplicacao Next.js
├── docs/             # Documentation / Documentacao
├── docker-compose.yml
└── .env.example
```

## Getting Started / Como Comecar

### Prerequisites / Pre-requisitos

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Docker & Docker Compose (optional / opcional)

### Quick Start with Docker / Inicio Rapido com Docker

```bash
# Clone the repository / Clone o repositorio
git clone https://github.com/your-org/team_principal.git
cd team_principal

# Copy environment variables / Copie as variaveis de ambiente
cp .env.example .env
# Edit .env with your values / Edite .env com seus valores

# Start all services / Inicie todos os servicos
docker-compose up -d
```

### Manual Setup / Configuracao Manual

#### Backend

```bash
cd backend

# Install dependencies / Instale as dependencias
poetry install

# Run migrations / Execute as migracoes
poetry run alembic upgrade head

# Seed the database / Popule o banco de dados
poetry run python -m app.db.seed

# Start the server / Inicie o servidor
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies / Instale as dependencias
npm install

# Start the dev server / Inicie o servidor de desenvolvimento
npm run dev
```

### Access / Acesso

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs / Documentacao da API:** http://localhost:8000/docs

## Development / Desenvolvimento

### Commands / Comandos

```bash
# Backend
cd backend
poetry run pytest                    # Run tests / Executar testes
poetry run ruff check app/           # Lint
poetry run ruff format app/          # Format / Formatar
poetry run mypy app/                 # Type check / Verificacao de tipos

# Frontend
cd frontend
npm run lint                         # Lint
npm run build                        # Build
npm run test                         # Run tests / Executar testes
```

### Branch Strategy / Estrategia de Branches

- `main` — stable releases / versoes estaveis
- `ep{XX}/{feature}` — epic feature branches / branches de features por epico

## Documentation / Documentacao

- [Architecture / Arquitetura](docs/architecture.md)
- [Setup Guide / Guia de Configuracao](docs/setup.md)

## License / Licenca

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Este projeto esta licenciado sob a Licenca MIT. Veja [LICENSE](LICENSE) para detalhes.
