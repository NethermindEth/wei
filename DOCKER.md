# Docker Setup for Wei

This document explains how to use the Docker setup for the Wei project.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configuration

Before running the Docker containers, you need to set up your environment variables:

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit the `.env` file and fill in your actual values, especially:
   - API keys for OpenRouter, Snapshot, and Tally
   - Any other configuration specific to your environment

## Running with Docker Compose

### Start all services

To start all services (PostgreSQL, agent, and indexer):

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL database
- Create the required databases (wei_agent and wei_indexer)
- Run migrations for both services using dedicated migration containers
- Start both the agent and indexer services

### How Migrations Work

The Docker setup uses a different approach for database migrations:

1. The `postgres` service creates the empty databases
2. Dedicated migration services (`agent-migrations` and `indexer-migrations`) run the SQL migration files
3. Only after migrations complete successfully, the main services start

### Start specific services

To start only specific services:

```bash
# Start only the database
docker-compose up -d postgres

# Start only the agent service (and its dependencies)
docker-compose up -d agent

# Start only the indexer service (and its dependencies)
docker-compose up -d indexer
```

### View logs

To view logs from the services:

```bash
# View logs from all services
docker-compose logs -f

# View logs from a specific service
docker-compose logs -f agent
docker-compose logs -f indexer
docker-compose logs -f postgres
```

### Stop services

To stop all services:

```bash
docker-compose down
```

To stop all services and remove volumes (this will delete all data in the database):

```bash
docker-compose down -v
```

## Building the Docker image

If you've made changes to the code and need to rebuild the Docker image:

```bash
docker-compose build
```

Or to rebuild a specific service:

```bash
docker-compose build agent
docker-compose build indexer
```

## Running commands inside containers

To run commands inside a container:

```bash
# Run a command in the agent container
docker-compose exec agent /bin/bash

# Run a command in the indexer container
docker-compose exec indexer /bin/bash

# Run a command in the postgres container
docker-compose exec postgres psql -U postgres
```

## Development workflow

For development, you might want to:

1. Make changes to the code on your host machine
2. Rebuild the Docker image: `docker-compose build`
3. Restart the services: `docker-compose up -d`

## Troubleshooting

### Database connection issues

If the services can't connect to the database:

1. Check if the PostgreSQL container is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check the PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Ensure the database initialization script ran correctly:
   ```bash
   docker-compose exec postgres psql -U postgres -c "\l"
   ```
   This should list both `wei_agent` and `wei_indexer` databases.

### Service startup issues

If a service fails to start:

1. Check the service logs:
   ```bash
   docker-compose logs agent
   # or
   docker-compose logs indexer
   ```

2. Ensure migrations ran successfully:
   ```bash
   docker-compose exec agent /bin/bash -c "sqlx migrate info --source crates/agent/migrations"
   # or
   docker-compose exec indexer /bin/bash -c "sqlx migrate info --source crates/indexer/migrations"
   ```
