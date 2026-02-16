# Setup Guide / Guia de Configuracao

## Prerequisites / Pre-requisitos

Before starting, make sure you have installed:

Antes de comecar, certifique-se de ter instalado:

- **Python 3.12+** — [python.org](https://www.python.org/downloads/)
- **Poetry** — [python-poetry.org](https://python-poetry.org/docs/#installation)
- **Node.js 20+** — [nodejs.org](https://nodejs.org/)
- **PostgreSQL 16+** — [postgresql.org](https://www.postgresql.org/download/)
- **Docker & Docker Compose** (optional / opcional) — [docker.com](https://docs.docker.com/get-docker/)

## Option 1: Docker (Recommended / Recomendado)

The easiest way to get started is using Docker Compose:

A maneira mais facil de comecar e usando Docker Compose:

```bash
# 1. Clone the repository / Clone o repositorio
git clone https://github.com/your-org/team_principal.git
cd team_principal

# 2. Copy and configure environment / Copie e configure o ambiente
cp .env.example .env
# Edit .env with your preferred values / Edite .env com seus valores preferidos

# 3. Start all services / Inicie todos os servicos
docker-compose up -d

# 4. Run database migrations / Execute as migracoes do banco
docker-compose exec backend alembic upgrade head

# 5. Seed initial data / Popule dados iniciais
docker-compose exec backend python -m app.db.seed
```

### Accessing Services / Acessando os Servicos

| Service / Servico | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs / Documentacao | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Option 2: Manual Setup / Configuracao Manual

### 1. Database / Banco de Dados

Create a PostgreSQL database:

Crie um banco de dados PostgreSQL:

```bash
createdb team_principal
```

### 2. Backend

```bash
cd backend

# Install dependencies / Instale as dependencias
poetry install

# Activate virtual environment / Ative o ambiente virtual
poetry shell

# Run migrations / Execute as migracoes
alembic upgrade head

# Seed the database / Popule o banco de dados
python -m app.db.seed

# Start development server / Inicie o servidor de desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend

# Install dependencies / Instale as dependencias
npm install

# Start development server / Inicie o servidor de desenvolvimento
npm run dev
```

## Environment Variables / Variaveis de Ambiente

See `.env.example` for all available variables with descriptions.

Veja `.env.example` para todas as variaveis disponiveis com descricoes.

### Required Variables / Variaveis Obrigatorias

| Variable / Variavel | Description / Descricao |
|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string / String de conexao async PostgreSQL |
| `SECRET_KEY` | Secret key for JWT signing / Chave secreta para assinatura JWT |
| `NEXTAUTH_SECRET` | Secret key for NextAuth.js / Chave secreta para NextAuth.js |
| `NEXTAUTH_URL` | NextAuth.js base URL / URL base do NextAuth.js |

## Troubleshooting / Solucao de Problemas

### Port already in use / Porta ja em uso

```bash
# Check what's using the port / Verifique o que esta usando a porta
lsof -i :8000
lsof -i :3000
```

### Database connection error / Erro de conexao com banco de dados

Make sure PostgreSQL is running and the credentials in `.env` are correct.

Certifique-se de que o PostgreSQL esta rodando e as credenciais no `.env` estao corretas.

### Poetry not found / Poetry nao encontrado

```bash
# Install Poetry / Instale o Poetry
curl -sSL https://install.python-poetry.org | python3 -
```
