# Multi-stage build for Wei Agent
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
COPY crates/agent ./crates/agent
COPY crates/indexer/Cargo.toml ./crates/indexer/

# Create minimal src structure for indexer to satisfy Cargo
RUN mkdir -p ./crates/indexer/src && \
    echo "// Empty file to satisfy Cargo" > ./crates/indexer/src/lib.rs

# Build only the agent binary
RUN cargo build --release --bin agent

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y libpq5 ca-certificates postgresql-client libssl3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy migrations directory
COPY --from=builder /usr/src/wei/crates/agent/migrations /app/migrations

# Copy the agent binary from builder stage
COPY --from=builder /usr/src/wei/target/release/agent /app/agent

# Create a non-root user for security and set permissions
RUN useradd -r -s /bin/false -m -d /app appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /app/agent
USER appuser

# Expose the default port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

# Set default environment variables
ENV WEI_AGENT_PORT=8000
ENV RUST_LOG=info

# Run the agent
CMD ["/app/agent"]