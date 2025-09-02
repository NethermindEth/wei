# Multi-stage build for Wei indexer
FROM rustlang/rust:nightly AS builder

WORKDIR /usr/src/wei

# Install build dependencies
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy workspace configuration files first for better caching
COPY Cargo.toml Cargo.lock ./

# Copy all workspace crates (needed for workspace resolution)
COPY crates/ ./crates/

# Build only the indexer binary with optimizations
RUN cargo build --release --bin indexer

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y libpq5 ca-certificates postgresql-client libssl3 libcurl4 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the indexer binary from builder stage
COPY --from=builder /usr/src/wei/target/release/indexer /app/indexer

# Copy migrations directory if it exists
COPY --from=builder /usr/src/wei/crates/indexer/migrations /app/migrations

# Create a non-root user for security
RUN useradd -r -s /bin/false -m -d /app appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the default port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${WEI_AGENT_PORT}/health || exit 1

# Set default environment variables
ENV WEI_INDEXER_PORT=3002
ENV RUST_LOG=info

# Run the indexer
CMD ["/app/indexer"]