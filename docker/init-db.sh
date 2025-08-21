#!/bin/bash
set -e

# Create databases
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE wei_agent;
    CREATE DATABASE wei_indexer;
    
    GRANT ALL PRIVILEGES ON DATABASE wei_agent TO postgres;
    GRANT ALL PRIVILEGES ON DATABASE wei_indexer TO postgres;
EOSQL

echo "Databases created successfully"
