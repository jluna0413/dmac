# PostgreSQL Setup for DMac

This document provides instructions for setting up PostgreSQL for the DMac project.

## Prerequisites

- Docker and Docker Compose
- Python 3.10 or later
- PowerShell (for Windows) or Bash (for Linux/macOS)

## Setup Instructions

### 1. Install Required Python Packages

```bash
pip install asyncpg psycopg2-binary
```

### 2. Start PostgreSQL with Docker Compose

The easiest way to run PostgreSQL is using Docker Compose:

```bash
docker-compose up -d postgres
```

This will start a PostgreSQL server with the following configuration:
- Username: postgres
- Password: postgres
- Database: dmac
- Port: 5432

### 3. Set the Database Connection String

Set the `DMAC_DB_URL` environment variable to the PostgreSQL connection string:

```bash
# Windows (PowerShell)
$env:DMAC_DB_URL = "postgresql://postgres:postgres@localhost/dmac"

# Linux/macOS (Bash)
export DMAC_DB_URL="postgresql://postgres:postgres@localhost/dmac"
```

### 4. Start the DMac Server

```bash
python run_server.py
```

## Using the Start Script

For convenience, you can use the provided start script:

```bash
# Windows
.\start_server.ps1

# Linux/macOS
./start_server.sh
```

This script will:
1. Start PostgreSQL using Docker Compose
2. Wait for PostgreSQL to be ready
3. Set the database connection string
4. Start the DMac server
5. Clean up when the server stops

## Troubleshooting

### Connection Issues

If you encounter connection issues, check that:
- Docker is running
- The PostgreSQL container is running (`docker ps`)
- The connection string is correct

### Database Initialization

The database tables will be created automatically when the server starts. If you need to reset the database, you can remove the Docker volume:

```bash
docker-compose down -v
```

## Production Deployment

For production deployment, consider:
- Using a managed PostgreSQL service
- Setting up proper authentication
- Configuring backups
- Setting up replication for high availability
