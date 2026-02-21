# WareHouse - Gestione Magazzino e Logistica

Sistema integrato per la gestione completa di magazzino, ordini, spedizioni e clienti.

## Stack Tecnologico

- **Frontend:** Vue 3 + Vite + TailwindCSS
- **Backend:** Python / FastAPI
- **Database:** PostgreSQL 16
- **Reverse Proxy:** Nginx
- **Container:** Docker Compose

## Requisiti

- Docker Desktop installato e in esecuzione

## Avvio Produzione

```bash
docker compose up --build -d
```

L'applicazione sarà disponibile su `http://localhost:8080`.

## Struttura

```
backend/       → API FastAPI (Python)
frontend/      → SPA Vue 3
nginx/         → Reverse proxy + serve frontend
```

## Credenziali Default

| Ruolo | Email | Password |
|-------|-------|----------|
| Admin | admin@warehouse.local | Admin2026! |

## Comandi Utili

```bash
# Avvio
docker compose up --build -d

# Log
docker compose logs -f

# Stop
docker compose down

# Reset database
docker compose down -v
docker compose up --build -d
```

## API

Documentazione API disponibile su `http://localhost:8080/api/docs`.
