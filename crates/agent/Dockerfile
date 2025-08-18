# Multi-stage build for Wei Agent
FROM rustlang/rust:nightly AS builder

WORKDIR /usr/src/wei

# Install build dependencies
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy workspace configuration files first for better caching
COPY Cargo.toml Cargo.lock ./

# Copy the agent crate
COPY crates/agent ./crates/agent

# Build only the agent binary with optimizations
RUN cargo build --release --bin agent

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y libpq5 ca-certificates libssl3 curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the agent binary from builder stage
COPY --from=builder /usr/src/wei/target/release/agent /app/agent

# Copy migrations directory if it exists
COPY --from=builder /usr/src/wei/crates/agent/migrations /app/migrations

# Create a non-root user for security
RUN useradd -r -s /bin/false -m -d /app appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the default port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

# Set default environment variables
ENV WEI_AGENT_PORT=8000
ENV RUST_LOG=info

# Run the agent
CMD ["/app/agent"]