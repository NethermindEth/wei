# Multi-stage build for Wei Indexer
FROM rustlang/rust:nightly as builder

WORKDIR /usr/src/wei

# Install build dependencies
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy workspace configuration files
COPY Cargo.toml Cargo.lock ./

# Copy all crates needed for workspace dependencies
COPY crates/indexer ./crates/indexer
COPY crates/agent/Cargo.toml ./crates/agent/

# Create minimal src structure for agent to satisfy Cargo
RUN mkdir -p ./crates/agent/src && \
    echo "// Empty file to satisfy Cargo" > ./crates/agent/src/lib.rs

# Build only the indexer binary
RUN cargo build --release --bin indexer

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y libpq5 ca-certificates postgresql-client libssl3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the indexer binary from builder stage
COPY --from=builder /usr/src/wei/target/release/indexer /app/indexer

# Copy migrations directory
COPY --from=builder /usr/src/wei/crates/indexer/migrations /app/migrations

# Create a non-root user for security
RUN useradd -r -s /bin/false -m -d /app appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the default port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001 || exit 1

# Set default environment variables
ENV INDEXER__SERVER__PORT=3001
ENV INDEXER__SERVER__HOST=0.0.0.0
ENV INDEXER__DATABASE__URL=postgresql://postgres:postgres@wei-postgres:5432/wei_indexer
ENV RUST_LOG=info

# Run the indexer
CMD ["/app/indexer"]
