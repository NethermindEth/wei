FROM rustlang/rust:nightly as builder

WORKDIR /usr/src/wei

# Install dependencies
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .

# Build the indexer binary
RUN cargo build --release --bin indexer

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y libpq5 ca-certificates postgresql-client libcurl4 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy binary from builder stage
COPY --from=builder /usr/src/wei/target/release/indexer /app/indexer

# Copy migrations
COPY --from=builder /usr/src/wei/crates/indexer/migrations /app/crates/indexer/migrations

# Copy env example for reference


set -e\n\
\n\
wait_for_postgres() {\n\
  echo "Waiting for PostgreSQL to be ready..."\n\
  # Use fixed values for PostgreSQL connection\n\
  PG_HOST="wei-postgres"\n\
  PG_PORT="5432"\n\
\n\
  echo "Checking PostgreSQL connection at $PG_HOST:$PG_PORT..."\n\
\n\
  # Wait for PostgreSQL to be ready\n\
  until pg_isready -h $PG_HOST -p $PG_PORT -U postgres; do\n\
    echo "PostgreSQL is unavailable - sleeping"\n\
    sleep 1\n\
  done\n\
\n\
  echo "PostgreSQL is up and running!"\n\
}\n\
\n\
wait_for_postgres\n\
echo "Starting indexer service..."\n\
# Update the database URL to use the correct hostname\n\
export INDEXER__DATABASE__URL="${INDEXER__DATABASE__URL:-postgresql://postgres:postgres@wei-postgres:5432/wei_indexer}"\n\
exec /app/indexer "$@"' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
